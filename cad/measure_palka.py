import Mesh
for n in ["palka1_golova", "palka2_seredina", "palka3_k_deke"]:
    m = Mesh.Mesh(rf"C:\App\gitar\3D model\{n}.stl")
    b = m.BoundBox
    print(f"{n}: {b.XLength:.1f} x {b.YLength:.1f} x {b.ZLength:.1f}  "
          f"X[{b.XMin:.0f},{b.XMax:.0f}] Y[{b.YMin:.0f},{b.YMax:.0f}] Z[{b.ZMin:.0f},{b.ZMax:.0f}]")
