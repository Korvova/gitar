# Модель мотора GB1806 со стаканом-энкодером (по чертежу продавца + фото владельца 25.11). Размеры в мм, приблизительные там, где не замерено.
# Запуск: blender -b -P gb1806_model.py  → GB1806_model.blend рядом
import bpy, bmesh, math, os
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
HERE = os.path.dirname(os.path.abspath(__file__))


def mat(name, rgba, metal=0.0, rough=0.5):
    m = bpy.data.materials.new(name); m.diffuse_color = rgba; m.metallic = metal; m.roughness = rough
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    if b: b.inputs["Base Color"].default_value = rgba; b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    return m


M_BLACK = mat("чёрный анод", (0.03, 0.03, 0.035, 1), 0.6, 0.45)
M_CAP = mat("стакан", (0.06, 0.06, 0.07, 1), 0.4, 0.5)
M_GRAY = mat("статор", (0.25, 0.25, 0.27, 1), 0.7, 0.4)
M_SILVER = mat("серебро", (0.8, 0.8, 0.82, 1), 1.0, 0.25)
M_PCB = mat("плата", (0.05, 0.35, 0.15, 1), 0.0, 0.5)
M_CHIP = mat("микросхема", (0.02, 0.02, 0.02, 1), 0.0, 0.6)
M_RED = mat("провод красный", (0.75, 0.05, 0.05, 1), 0.0, 0.5)
M_WHITE = mat("провод белый", (0.9, 0.9, 0.9, 1), 0.0, 0.5)
M_BLK = mat("провод чёрный", (0.02, 0.02, 0.02, 1), 0.0, 0.5)
M_PH = mat("фазы (припаять)", (0.85, 0.55, 0.1, 1), 0.0, 0.5)
M_MAG = mat("магнит", (0.55, 0.55, 0.6, 1), 0.9, 0.3)


def cyl(name, r, z0, z1, m, x=0.0, y=0.0, verts=96, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=z1 - z0, vertices=verts, location=(x, y, (z0 + z1) / 2))
    o = bpy.context.object; o.name = name; o.data.materials.append(m)
    if parent: o.parent = parent
    return o


def box(name, x0, x1, y0, y1, z0, z1, m, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.object; o.scale = (x1 - x0, y1 - y0, z1 - z0); bpy.ops.object.transform_apply(scale=True)
    o.name = name; o.data.materials.append(m)
    if parent: o.parent = parent
    return o


def cut(target, cutter):
    md = target.modifiers.new("cut", 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = cutter; md.solver = 'EXACT'
    bpy.context.view_layer.objects.active = target; bpy.ops.object.modifier_apply(modifier="cut")
    bpy.data.objects.remove(cutter)


def holes(target, pts, r, z0, z1):
    for (x, y) in pts:
        cut(target, cyl("_h", r, z0, z1, M_BLACK, x, y, 32))


def ring_pts(R, n, a0=0.0):
    return [(R * math.cos(math.radians(a0 + 360 * i / n)), R * math.sin(math.radians(a0 + 360 * i / n))) for i in range(n)]


# ---- высоты (снизу вверх, ось Z = ось мотора) ----
Z_CAP0, Z_CAP1 = 0.0, 7.5          # стакан энкодера (с платой AS5600)
Z_RING0 = Z_CAP1 - 1.0             # фланец статора Ø21 × 1 (внутри верхнего края стакана)
Z_HUB0 = Z_RING0 - 3.5             # выступ Ø9.5 × 3.5 с магнитом (подшипник)
Z_BELL0, Z_BELL1 = Z_CAP1, Z_CAP1 + 13.0   # колокол ротора Ø22 × 13 (КРУТИТСЯ), сверху торец 4×М2 на Ø6
R = 11.0

# ===== РОТОР (крутится) =====
ROT = bpy.data.objects.new("РОТОР (крутится вместе с торцом)", None); sc.collection.objects.link(ROT)
bell = cyl("колокол ротора Ø22 × 13", R, Z_BELL0, Z_BELL1, M_BLACK, parent=ROT)
cut(bell, cyl("_pocket", R - 0.8, Z_BELL0 - 0.1, Z_BELL1 - 1.2, M_BLACK))           # колокол полый (внутри обмотки статора)
holes(bell, ring_pts(3.0, 4, 45), 0.8, Z_BELL1 - 3.0, Z_BELL1 + 0.1)                 # 4 × М2 резьбовые на Ø6 (на фото — по диагонали)
cut(bell, cyl("_c", 1.0, Z_BELL1 - 3.0, Z_BELL1 + 0.1, M_BLACK, verts=32))           # центральное отверстие
for i in range(2):                                                                    # канавка-риска на колоколе (как на фото)
    pass
cyl("магнит на торце вала (для AS5600)", 2.5, Z_HUB0 - 0.01, Z_HUB0 + 1.2, M_MAG, parent=ROT)

# ===== СТАТОР (неподвижный) =====
STA = bpy.data.objects.new("СТАТОР (неподвижный: фланец, подшипник, площадки фаз)", None); sc.collection.objects.link(STA)
ring = cyl("фланец статора Ø21 × 1 (снизу 6 × М2 на Ø18)", 10.5, Z_RING0, Z_CAP1, M_GRAY, parent=STA)
holes(ring, ring_pts(9.0, 6, 30), 0.8, Z_RING0 - 0.1, Z_CAP1 - 0.3)
hub = cyl("выступ подшипника Ø9.5 × 3.5", 4.75, Z_HUB0 + 1.2, Z_RING0 + 0.01, M_SILVER, parent=STA)
cut(hub, cyl("_hh", 2.0, Z_HUB0, Z_RING0 + 1, M_SILVER, verts=32))
for i, xx in enumerate((-2.2, 0.0, 2.2)):                                            # 3 площадки фаз на нижней стороне фланца (рядом с выступом)
    box("площадка фазы %d" % (i + 1), xx - 0.8, xx + 0.8, -9.6, -6.4, Z_RING0 - 0.15, Z_RING0, M_SILVER, STA)
box("плашка с площадками", -3.4, 3.4, -9.9, -6.0, Z_RING0 - 0.08, Z_RING0, M_CHIP, STA)

# ===== СТАКАН с платой AS5600 (неподвижный, крепится к фланцу 4 винтами) =====
CAP = bpy.data.objects.new("СТАКАН энкодера (снимается: 4 винта М2 снизу)", None); sc.collection.objects.link(CAP)
cap = cyl("стакан Ø22 × 7.5", R, Z_CAP0, Z_CAP1, M_CAP, parent=CAP)
cut(cap, cyl("_in", R - 0.9, Z_CAP0 + 1.0, Z_CAP1 + 0.1, M_CAP))                    # внутри полость, дно 1 мм
holes(cap, ring_pts(9.0, 4, 30 + 30), 1.1, Z_CAP0 - 0.1, Z_CAP0 + 1.1)               # 4 сквозных Ø2.2 на Ø18 (совпадают с 4 из 6 отверстий фланца)
for (x, y) in ring_pts(9.0, 4, 60):                                                   # потай под головки винтов снизу
    cut(cap, cyl("_cs", 1.9, Z_CAP0 - 0.1, Z_CAP0 + 0.5, M_CAP, x, y, 32))
cut(cap, box("_slot", -3.5, 3.5, -R - 1, -R + 1.5, Z_CAP0 + 2.5, Z_CAP0 + 6.0, M_CAP))   # окно для проводов в боковой стенке (≈7 × 3.5)
pcb = cyl("плата AS5600 (Ø~15, винты стакана проходят мимо)", 7.6, Z_CAP0 + 1.0, Z_CAP0 + 2.0, M_PCB, verts=64, parent=CAP)
box("микросхема AS5600 (SOIC-8)", -2.5, 2.5, -2.0, 2.0, Z_CAP0 + 2.0, Z_CAP0 + 2.9, M_CHIP, CAP)
for i, xx in enumerate((-2.6, -1.3, 0.0, 1.3, 2.6)):                                 # 5 площадок I2C/DIR на плате
    box("площадка платы %d" % (i + 1), xx - 0.4, xx + 0.4, 4.5, 5.6, Z_CAP0 + 2.0, Z_CAP0 + 2.05, M_SILVER, CAP)


# ===== ПРОВОДА =====
def wire(name, pts, m, r=0.45, parent=None):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 3
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts): sp.points[i].co = (p[0], p[1], p[2], 1)
    o = bpy.data.objects.new(name, cu); sc.collection.objects.link(o); cu.materials.append(m)
    if parent: o.parent = parent
    return o


def twisted(names_mats, start, length=90.0, sag=6.0, z0=4.2, tw=0.55, parent=None):
    # 3 провода от окна стакана наружу (−Y), скручены
    for j, (nm, m) in enumerate(names_mats):
        pts = []
        sx, sy = start[j]
        pts.append((sx, sy, Z_CAP0 + 2.05))                                          # от платы
        pts.append((sx * 0.6, -R + 0.5, z0))                                         # через окно
        for i in range(0, 61):
            t = i / 60; d = t * length
            a = 2 * math.pi * (d / 6.0) + 2 * math.pi * j / 3
            pts.append((tw * math.cos(a), -R - 1 - d, z0 - sag * math.sin(math.pi * t) * t + tw * math.sin(a)))
        wire(nm, pts, m, parent=parent)


twisted([("провод AS5600 красный (+5V)", M_RED), ("провод AS5600 белый (PWM)", M_WHITE), ("провод AS5600 чёрный (GND)", M_BLK)],
        [(-1.0, -6.0), (0.0, -6.0), (1.0, -6.0)], parent=CAP)
# фазы: пока не припаяны — показываю, куда их паять (оранжевые, короткие, через то же окно)
for i, xx in enumerate((-2.2, 0.0, 2.2)):
    wire("ФАЗА %d — припаять сюда (через окно стакана)" % (i + 1),
         [(xx, -8.0, Z_RING0 - 0.15), (xx * 0.8, -9.5, Z_RING0 - 1.0), (xx * 0.6, -R + 0.3, 5.2), (xx * 0.6 + 0.5, -R - 6, 5.5), (xx + 1.5, -R - 18, 4.5)],
         M_PH, r=0.4, parent=STA)

# ===== помощники =====
ax = bpy.data.objects.new("ось вращения", None); sc.collection.objects.link(ax); ax.empty_display_type = 'SINGLE_ARROW'; ax.empty_display_size = 30
# анимация: ротор крутится (видно, что крутится только колокол с торцом)
for f, ang in ((1, 0.0), (120, 2 * math.pi)):
    ROT.rotation_euler.z = ang; ROT.keyframe_insert("rotation_euler", index=2, frame=f)
for fc in ROT.animation_data.action.fcurves if hasattr(ROT.animation_data.action, "fcurves") else []:
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
sc.frame_start, sc.frame_end = 1, 120
# вид
for scr in bpy.data.screens:
    for ar in scr.areas:
        for sp in ar.spaces:
            if sp.type == 'VIEW_3D':
                sp.shading.type = 'MATERIAL'; sp.clip_start = 0.1; sp.clip_end = 2000
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "GB1806_model.blend")); print("saved GB1806_model.blend")
