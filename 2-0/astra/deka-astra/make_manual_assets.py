"""Prepare print plates and additional CAD geometry for assembly diagrams."""
from pathlib import Path
import json
import zipfile
import xml.etree.ElementTree as ET
from build123d import Compound, Mesher, Pos, export_stl, import_step
import model

ROOT=Path(__file__).resolve().parent
out=ROOT/'manual';out.mkdir(exist_ok=True)
(ROOT/'plates').mkdir(exist_ok=True)
u=model.upstream()
base=import_step(ROOT/'d1_astra_A2.step')
guide=import_step(ROOT/'guide_astra_A2.step')

def on_bed(s,x=0,y=0):
    b=s.bounding_box()
    return Pos(x-b.min.X,y-b.min.Y,-b.min.Z)*s

def plate(name,parts):
    m=Mesher()
    for label,s in parts:
        s.label=label
        m.add_shape(s,linear_deflection=.02,angular_deflection=.1,part_number=label)
    path=ROOT/'plates'/name
    m.write(path)
    ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
    with zipfile.ZipFile(path) as z:
        xml=ET.fromstring(z.read('3D/3dmodel.model'))
        assert xml.attrib.get('unit')=='millimeter'
        assert len(xml.findall('m:build/m:item',ns))==len(parts)
    bounds=Compound(children=[s for _,s in parts]).bounding_box()
    assert bounds.min.Z>=-1e-5
    print(name,len(parts),'objects; envelope',tuple(round(v,2) for v in bounds.size),flush=True)
    return parts

new=plate('01_A2_D1_and_3_guides.3mf', [('D1_A2',on_bed(base,5,5))]+[
    (f'Guide_A2_{i+1}',on_bed(model.print_pose(guide),67,5+32*i)) for i in range(3)])
plate('04_A3_reinforced_cranks_1_2_3.3mf',[
    (f'Crank_{k}_A3',on_bed(model.reinforced_crank(u,k),5+25*(k-1),5)) for k in range(1,4)])
plate('03_v3_tails_optional.3mf',[
    (f'Tail_{k}',on_bed(u['tails'][k],5+33*k,5)) for k in range(4)])
for i,(label,s) in enumerate(new):
    export_stl(s,out/f'plate_{i}.stl',tolerance=.025)
for k in range(4):
    export_stl(on_bed(model.reinforced_crank(u,k),k*28,0),out/f'crank_id_{k}.stl',tolerance=.02)
# Cropped CAD detail, not an edited screenshot: real mating geometry at floor 1.
ext=Pos(10,320,8.45)*u['ext']
tail=Pos(10,480,8.45)*u['tails'][1]
for name,shape in [('lap_ext',ext),('lap_tail',tail)]:
    crop=Compound(children=shape.intersect(model.box(-5,25,465,515,0,20)))
    export_stl(crop,out/f'{name}.stl',tolerance=.015)
for name,shape,y0,y1 in [
    ('mount_floor',Pos(0,480,0)*base,525,555),
    ('motor_floor',Pos(0,480,0)*base,496,534),
    ('joint_d1',Pos(0,480,0)*base,628,658),
    ('joint_d2',Pos(0,640,0)*u['deka_base'](640,False,u['TUMBA2'],(75,120)),640,671)]:
    crop=Compound(children=shape.intersect(model.box(-27,27,y0,y1,0,3)))
    export_stl(crop,out/f'{name}.stl',tolerance=.02)
report={'plate_files':[p.name for p in (ROOT/'plates').glob('*.3mf')],
        'format':'generic 3MF, millimetres, separate named objects; no printer/material/slicer preset',
        'scope':'Geometry only. Slice with the actual printer and previously successful material profile.'}
(out/'plate_checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
