"""Final lane for the 52 mm neck: moving-magnet U carriage (3 magnets 15x10x5 N52 per side,
pole pitch 10), fixed ironless coil blade (3 coils 15 mm wide, legs 5 mm, 3 mm thick), slot 4 mm.
Force per sqrt(W) vs carriage position, coils driven independently (best case) and as 2 phases."""
import numpy as np, magpylib as magpy
BR=1.43; RHO=1.72e-8; FF=0.55
TAU,T,H,G,TC=10.0,5.0,15.0,4.0,3.0
COILS=[-15.0,0.0,15.0]; LEG=5.0; SPAN=10.0
def carriage(X):
    c=magpy.Collection()
    for side in (-1,1):
        for p in range(3):
            s=1 if p%2==0 else -1
            c.add(magpy.magnet.Cuboid(polarization=(0,s*BR,0),dimension=(TAU*1e-3,T*1e-3,H*1e-3),
                  position=((X+(p-1)*TAU)*1e-3, side*(G/2+T/2)*1e-3,0)))
    return c
def leg_B(col,x0,x1):
    xs=np.linspace(x0,x1,6); ys=np.linspace(-TC/2,TC/2,3); zs=np.linspace(-H/2,H/2,7)
    P=np.stack(np.meshgrid(xs,ys,zs,indexing='ij'),-1).reshape(-1,3)*1e-3
    return col.getB(P)[:,1].mean()
l_turn=(2*SPAN+2*(H+LEG))*1e-3; area=LEG*TC*1e-6
wire=0.25; aw=np.pi*(wire/2)**2*1e-6; N=int(FF*area/aw); R=RHO*N*l_turn/aw
print(f"coil: N={N} turns of {wire} mm, R={R:.1f} Ohm, Cu {8960*FF*area*l_turn*1e3:.1f} g each")
for X in (0,5,10,15,22):
    col=carriage(X)
    k=[]
    for xc in COILS:
        bl=leg_B(col,xc-SPAN/2-LEG/2,xc-SPAN/2+LEG/2); br=leg_B(col,xc+SPAN/2-LEG/2,xc+SPAN/2+LEG/2)
        k.append(N*H*1e-3*(bl-br))
    k=np.array(k); Km=np.sqrt((k**2).sum()/R)
    P=(0.5*9.81/Km)**2
    # current per coil for 500 g with optimal split
    I=k/R*(0.5*9.81)/((k**2).sum()/R)
    print(f"X={X:4.0f} mm  k={np.round(k,2)} N/A  Km={Km:.2f} N/sqrtW  P(500g)={P:5.1f} W  I={np.round(I,2)} A  P(150g)={(0.15*9.81/Km)**2:.2f} W")
