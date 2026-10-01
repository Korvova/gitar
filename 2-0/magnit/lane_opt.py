import numpy as np, magpylib as magpy
from lane_final import carriage, leg_B, RHO, FF, TC, H
def evaluate(wc, n, wire=0.25, Xs=np.arange(0,22.1,1.0)):
    p=wc; COILS=[(i-(n-1)/2)*p for i in range(n)]
    LEG=wc/3; SPAN=wc-LEG
    l_turn=(2*SPAN+2*(H+LEG))*1e-3; area=LEG*TC*1e-6
    aw=np.pi*(wire/2)**2*1e-6; N=int(FF*area/aw); R=RHO*N*l_turn/aw
    kms=[]
    for X in Xs:
        col=carriage(X); k=[]
        for xc in COILS:
            bl=leg_B(col,xc-SPAN/2-LEG/2,xc-SPAN/2+LEG/2); br=leg_B(col,xc+SPAN/2-LEG/2,xc+SPAN/2+LEG/2)
            k.append(N*H*1e-3*(bl-br))
        kms.append(np.sqrt((np.array(k)**2).sum()/R))
    kms=np.array(kms); F=0.5*9.81
    return dict(wc=wc,n=n,N=N,R=round(R,1),Km_min=round(kms.min(),2),Km_mean=round(kms.mean(),2),
                Pmax500=round((F/kms.min())**2,1),Pmean500=round((F/kms.mean())**2,1),P150=round((0.15*9.81/kms.mean())**2,2))
if __name__=="__main__":
    for wc,n in ((13.0,4),(10.4,5),(8.6,6),(7.4,7)):
        print(evaluate(wc,n))
