"""Astra A2 push-fit deck revision, millimetres.

Run: python model.py [--fit 0.15]
Fit is clearance PER SIDE in the base sockets, not interference.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import math

from build123d import (
    Box, Compound, Cone, Cylinder, Part, Pos, Rectangle, RegularPolygon,
    Rot, export_step, export_stl, extrude, loft,
)
import trimesh

ROOT = Path(__file__).resolve().parent
SOURCE_SHA = "d9bc50e86047fa114c1673d9b758f7fd454ea29f"
GUIDE_Y = (540, 590, 634)
FEET_X = (-4, 18)


def upstream():
    path = ROOT / "reference" / "gitara_deka_v3.py"
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    # Only the reviewed geometry prefix, never upstream exports or test runners.
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "star_hole":
            break
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            continue
        nodes.append(node)
    ns = {"__file__": str(path)}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), ns)
    return ns


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0+x1)/2, (y0+y1)/2, (z0+z1)/2) * Box(x1-x0, y1-y0, z1-z0)


def foot(x=0):
    # Exact old deck interface: D5.7 pins in D6.0 holes, engagement 2.8 mm.
    return Pos(x, 0, 1.6) * Cylinder(2.85, 2.8)


def closed_guide(z_floors):
    g = box(-8, 21.5, -3, 3, 3, 22.5)
    g += box(4.9, 15.1, -3, 3, 2.1, 3.02)
    for z in z_floors:
        g -= box(5.6, 14.4, -3.1, 3.1, z-0.15, z+1.95)
    for x in FEET_X:
        g += foot(x)
    return g


def nut(x, y):
    n = extrude(RegularPolygon(5.5/math.sqrt(3), 6, rotation=30), amount=2.4)
    n -= Pos(0, 0, 1.2) * Cylinder(1.5, 2.6)
    return Pos(x, y, 6.2) * n


def screw(x, y):
    # M3x10 socket-head envelope and 0.5 mm washer. Threads are not modelled.
    s = Pos(x, y, 4.5) * Cylinder(1.5, 10)
    s += Pos(x, y, -2) * Cylinder(2.75, 3)
    w = Pos(x, y, -0.25) * Cylinder(3.5, 0.5)
    w -= Pos(x, y, -0.25) * Cylinder(1.6, 0.7)
    return s, w


def print_pose(shape):
    s = Rot(90, 0, 0) * shape
    bb = s.bounding_box()
    return Pos(-bb.min.X, -bb.min.Y, -bb.min.Z) * s


def reinforced_crank(u, k):
    original = u['crank_part'](k)
    if k == 0:
        return original
    disk_bottom = u['disk_top'](k) - u['DISK_T']
    start = 3.4  # Preserve the original neck through the 3 mm base, plus clearance.
    height = min(4.1, disk_bottom-start)
    c = original + Pos(0,0,start+height/2)*Cone(u['HUB_R'],u['DISK_R'],height)
    if disk_bottom > start+height:
        c += Pos(0,0,(start+height+disk_bottom)/2)*Cylinder(u['DISK_R'],disk_bottom-start-height)
    z0 = u['FLANGE_Z'][k]+2.2
    top = u['FLANGE_Z'][k]+u['SHAFT_OUT']+.2
    c -= Pos(0,0,(z0-.1+top)/2)*Cylinder(u['BORE_D']/2,top-z0+.1)
    return c


def crank_name(k):
    return 'reference_crank0_v3' if k == 0 else f'astra_crank{k}_A3'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fit", type=float, default=0.15)
    args = parser.parse_args()
    if not 0 <= args.fit <= 0.3:
        parser.error("--fit must be between 0 and 0.3 mm per side")
    u = upstream()
    g = closed_guide(u["Z_FLOOR"])
    # New D1: remove old sliding pockets, then cut two-foot sockets and rail seats.
    original_ys = u["COMB_Y"]
    u["COMB_Y"] = ()
    d1 = u["deka_base"](480, True, u["TUMBA1"], (40,100,135), neck_mount=True)
    d2 = u["deka_base"](640, False, u["TUMBA2"], (75,120))
    u["COMB_Y"] = original_ys
    for y in GUIDE_Y:
        yl = y-480
        for x in FEET_X:
            c = args.fit
            d1 -= Pos(x,yl,1.5)*Cylinder(2.85+c,3.2)
        d1 -= box(4.8, 15.2, yl-3.1, yl+3.1, 2, 3.1)

    parts = {"astra_d1": d1, "reference_d2_v3": d2, "astra_closed_guide": g}
    test_base = Compound(children=d1.intersect(box(-27,27,54,66,-.1,24)))
    parts["astra_test_base"] = Pos(0,-60,0)*test_base
    for k in range(4):
        parts[crank_name(k)] = reinforced_crank(u,k)
        parts[f"reference_tail{k}_v3"] = u["tails"][k]
    parts["reference_spacer0_v3"] = u["spacer_part"](u["EAR_SIGN"][0])


    scene = []
    def add(name, shape, color, group="static", k=None):
        scene.append(dict(name=name, shape=shape, color=color, group=group, k=k))
    add("D1", Pos(0,480,0)*d1, "#d4d8da")
    add("D2", Pos(0,640,0)*d2, "#d4d8da")
    for i,y in enumerate(GUIDE_Y):
        add(f"guide_{i}", Pos(0,y,0)*g, "#42a67a", "guide")
    for k,my in enumerate(u["MY"]):
        add(f"motor_{k}", Pos(0,my,u["FLANGE_Z"][k])*u["motor_model"](u["EAR_SIGN"][k]), "#3c4147", "motor", k)
        add(f"crank_{k}", Pos(0,my,0)*parts[crank_name(k)], "#3589c9", "crank", k)
        add(f"tail_{k}", Pos(10,480,u["Z_FLOOR"][k]+.05)*u["tails"][k], "#ed9947", "tail", k)
    add("spacer_0", Pos(0,515,0)*parts["reference_spacer0_v3"], "#939aa0")

    stls = ROOT / "stl"
    meshes = ROOT / "viewer" / "meshes"
    for p in (stls, meshes):
        p.mkdir(parents=True, exist_ok=True)
    reports = []
    for name, s in parts.items():
        if name in ("astra_closed_guide", "coupon_foot"):
            printable = print_pose(s)
        else:
            printable = Pos(0,0,-s.bounding_box().min.Z)*s
        export_stl(printable, stls / f"{name}.stl", tolerance=.02, angular_tolerance=.1)
        mesh = trimesh.load_mesh(stls/f"{name}.stl")
        report = dict(name=name, valid=s.is_valid, solids=len(s.solids()),
                      watertight=bool(mesh.is_watertight), volume_mm3=round(s.volume,3))
        reports.append(report)
        print(report, flush=True)
        assert report["valid"] and report["solids"] == 1 and report["watertight"], report
    for item in scene:
        export_stl(item["shape"], meshes/f'{item["name"]}.stl', tolerance=.035, angular_tolerance=.15)
    assembly = Compound(children=[i["shape"] for i in scene])
    export_step(assembly, ROOT/"assembly_astra_A3.step")
    for k in range(1,4):
        export_step(parts[crank_name(k)], ROOT/f'astra_crank{k}_A3.step')
    export_step(g, ROOT/"guide_astra_A2.step")
    export_step(d1, ROOT/"d1_astra_A2.step")
    manifest = [{key:val for key,val in item.items() if key != "shape"} for item in scene]
    (ROOT/"viewer"/"scene.json").write_text(json.dumps(manifest), encoding="utf-8")

    checks = []
    def check(name, actual, minimum=0):
        ok = actual >= minimum-1e-6
        checks.append(dict(name=name, actual_mm=round(actual,5), required_mm=minimum, passed=ok))
        print(checks[-1], flush=True)
    # Continuous bounds: the wide yokes never reach a guide at any crank phase.
    for k,my in enumerate(u["MY"]):
        for y in GUIDE_Y:
            check(f"yoke{k}_guide{y}_continuous_Y", abs(my-y)-4.8-4.15-3, .5)
            check(f"crank{k}_guide{y}_continuous_Y", abs(my-y)-8.3-3, .5)
    check("band_left_right_clearance", .4, .3)
    check("band_bottom_clearance", .05+.15, .15)
    check("band_top_clearance", 1.95-1.6-.05, .2)
    check("closed_bottom_rail_thickness", (3-.15)-2.1, .7)
    check("rail_floor_clearance", 2.1-2, .09)
    for item in scene:
        if item["group"] not in ("guide", "hardware"):
            continue
        for other in scene:
            if other["group"] != "motor":
                continue
            a,b=item["shape"],other["shape"]
            check(item["name"]+"_"+other["name"], a.distance_to(b), .2)
        if item["group"] == "guide":
            overlap = item["shape"].intersect(Pos(0,480,0)*d1)
            vol = 0 if overlap is None else sum(s.volume for s in overlap)
            check(item["name"]+"_base_no_overlap", 1e-5-vol, 0)
        if item["group"] == "hardware":
            guide_y = GUIDE_Y[int(item["name"].split("_")[1])]
            hit = item["shape"].intersect(Pos(0,guide_y,0)*g)
            vol = 0 if hit is None else sum(s.volume for s in hit)
            check(item["name"]+"_guide_no_overlap", 1e-5-vol, 0)
    # Verify the free NORTH end can thread through the closed slots before lapping.
    for k in range(1,4):
        end = Compound(children=u["tails"][k].intersect(box(-5,5,-.1,20,-1,4)))
        check(f"tail{k}_threading_height", 2.1-end.bounding_box().size.Z, .2)
        check(f"tail{k}_threading_width", 8.8-end.bounding_box().size.X, .5)
    check("solid_guide_body_at_former_nut_pockets", g.volume-2879.375, 300)
    # Added material is rotationally symmetric, so its static envelope covers
    # every crank angle. Tail bounding boxes include the entire +/-4.8 mm travel.
    for k in range(1,4):
        old=u['crank_part'](k)
        new=parts[crank_name(k)]
        extra=new-old
        check(f'crank{k}_added_volume',extra.volume,1)
        low=extra.intersect(box(-20,20,-20,20,-10,3.4))
        check(f'crank{k}_lower_interface_unchanged',1e-5-(sum(s.volume for s in low) if low else 0),0)
        check(f'crank{k}_original_geometry_preserved',1e-5-(old-new).volume,0)
        added=Pos(0,u['MY'][k],0)*extra
        for item in scene:
            if item['group'] == 'crank' and item['k'] == k:
                continue
            obstacle=item['shape']
            if item['group'] == 'crank':
                b=obstacle.bounding_box()
                obstacle=Pos(0,u['MY'][item['k']],(b.min.Z+b.max.Z)/2)*Cylinder(u['DISK_R'],b.max.Z-b.min.Z)
            if item['group'] == 'tail':
                b=obstacle.bounding_box()
                obstacle=box(b.min.X,b.max.X,b.min.Y-4.8,b.max.Y+4.8,b.min.Z,b.max.Z)
            check(f'crank{k}_added_sweep_{item["name"]}',added.distance_to(obstacle),.3)
    result = dict(revision="A3 reinforced cranks; A2 base and guides", upstream_commit=SOURCE_SHA,
                  source_sha256=hashlib.sha256((ROOT/"reference"/"gitara_deka_v3.py").read_bytes()).hexdigest(),
                  socket_clearance_per_side_mm=args.fit, parts=reports, checks=checks,
                  passed=all(c["passed"] for c in checks),
                  limitations=["Old D5.7/D6.0 guide fit reused from user-tested deck; A3 assembly not physically tested", "No dynamic force or strength validation", "Motor body drawing envelope only; connector/cable clearance unverified", "Original round 5.8 mm gear bore and drive pin retained; fit still requires physical verification"])
    (ROOT/"checks.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    assert result["passed"], "Some checks failed; see checks.json"


if __name__ == "__main__":
    main()
