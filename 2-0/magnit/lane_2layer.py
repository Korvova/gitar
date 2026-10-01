import numpy as np
from lane_final import carriage, leg_B, RHO, FF, TC, H
def ev(wc, wire=0.2, Xs=np.arange(0,22.1,0.5)):
    LEG=wc/3; SPAN=wc-LEG
    n1=int(52//wc); L1=[(i-(n1-1)/2)*wc for i in range(n1)]
    L2=[x+wc/2 for x in L1 if abs(x+wc/2)+wc/2<=26.01]+[L1[0]-wc/2] if L1[0]-wc/2-wc/2>=-26.01 else [x+wc/2 for x in L1 if abs(x+wc/2)+wc/2<=26.01]
    coils=L1+L2
    l_turn=(2*SPAN+2*(H+LEG))*1e-3; area=LEG*(TC/2)*1e-6
    aw=np.pi*(wire/2)**2*1e-6; N=int(FF*area/aw); R=RHO*N*l_turn/aw
    kms=[]
    for X in Xs:
        col=carriage(X)
        k=[N*H*1e-3*(leg_B(col,xc-SPAN/2-LEG/2,xc-SPAN/2+LEG/2)-leg_B(col,xc+SPAN/2-LEG/2,xc+SPAN/2+LEG/2)) for xc in coils]
        kms.append(np.sqrt((np.array(k)**2).sum()/R))
    kms=np.array(kms); F=0.5*9.81
    return dict(wc=wc,coils=len(coils),N=N,R=round(R,1),Pmax500=round((F/kms.min())**2,1),Pmean500=round((F/kms.mean())**2,1),P150=round((0.15*9.81/kms.mean())**2,2))
if __name__=="__main__":
    for wc in (10.0,11.0,12.0,13.0,14.0,15.0,16.0):
        print(ev(wc))
