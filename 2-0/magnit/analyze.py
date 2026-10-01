import json, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
d=json.load(open("energies.json")); G=0.4
names={"flat":"Плоская пластина","wedge":"Ваш клин","comb":"Гребёнка (3 зубца)","comb_wedge":"Гребёнка из клиньев"}
fig,ax=plt.subplots(1,2,figsize=(12,4.5))
summ={}
for s,rows in d.items():
    r=np.array(rows); m=np.isclose(r[:,1],G); a=r[m]; a=a[a[:,0].argsort()]
    X,W=a[:,0],a[:,2]; Fx=-np.gradient(W,X*1e-3)*-1  # F = +dW'/dx
    Fx=np.gradient(W,X*1e-3)
    fy=[]
    for x in X[::2]:
        lo=r[np.isclose(r[:,0],x)&np.isclose(r[:,1],G-0.05)][0,2]; hi=r[np.isclose(r[:,0],x)&np.isclose(r[:,1],G+0.05)][0,2]
        fy.append(-(hi-lo)/0.1e-3)   # pull down (positive = attraction)
    ax[0].plot(X,np.abs(Fx)*102,label=names[s]); ax[1].plot(X[::2],np.array(fy)*102,label=names[s])
    summ[s]=dict(Fx_max_g=float(np.abs(Fx).max()*102),Fy_max_g=float(max(fy)*102),Fy_at_Fxmax_g=float(fy[int(np.abs(Fx).argmax()//2)]*102))
for a_,t in zip(ax,["Тянет ВДОЛЬ грифа (полезная), г","Прижимает ВНИЗ к катушкам (трение), г"]):
    a_.set_title(t);a_.set_xlabel("сдвиг тележки от катушки, мм");a_.grid(alpha=.3);a_.legend()
fig.suptitle("1 катушка, 300 А·витков, зазор 0.4 мм, ширина 10 мм");fig.tight_layout();fig.savefig("forces.png",dpi=110)
print(json.dumps(summ,indent=1,ensure_ascii=False))
