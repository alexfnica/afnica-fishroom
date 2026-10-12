import sys,numpy as np
from PIL import Image
rgb=np.asarray(Image.open(sys.argv[1]).convert('RGB'),np.float32)/255
H,W,_=rgb.shape;lum=rgb.mean(-1)
diff=np.max(np.abs(rgb-1),-1);alpha=np.clip((diff-.02)*3.2,0,1);alpha[alpha<.02]=0
a3=alpha[...,None];col=np.clip((rgb-(1-a3))/np.maximum(a3,1e-3),0,1);col=np.where(a3>.97,rgb,col)
Y,X=np.mgrid[0:H,0:W]
def opaque(m,a=.93):
    alpha[m]=np.maximum(alpha[m],a);col[m]=rgb[m]
hooks=((X>=290)&(X<=345)|(X>=680)&(X<=735))&(Y>=36)&(Y<=140)&(lum<.93)
rim=(Y>=80)&(Y<=112)&(X>=37)&(X<=986)
opaque(hooks);opaque(rim,.9)
grate=(Y>=438)&(Y<=488)&(X>=62)&(X<=958)
ga=.3+.62*np.clip((lum-.5)/(.98-.5),0,1);alpha[grate]=ga[grate];col[grate]=np.clip(rgb[grate]*1.02,0,1)
out=np.concatenate([col,alpha[...,None]],-1)
inner=(X>=62)&(X<=958)&(Y>=113)&(Y<=488)&~hooks
back=out.copy();back[...,3]*=inner;front=out.copy();front[...,3]*=~inner
x0,x1,y0,y1=30,996,34,519
for nm,arr in [('box_back.png',back),('box_front.png',front),('box_full.png',out)]:
    im=Image.fromarray((arr[y0:y1,x0:x1]*255+.5).astype(np.uint8),'RGBA');im=im.resize((640,round(im.height*640/im.width)),Image.LANCZOS);im.save('scratchpad/'+nm);print(nm,im.size)
