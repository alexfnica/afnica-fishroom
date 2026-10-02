import bpy,sys,numpy as np
a=sys.argv[sys.argv.index('--')+1:]
im=bpy.data.images.load(a[0]);W,H=im.size;p=np.empty(W*H*4,np.float32);im.pixels.foreach_get(p);S=p.reshape(H,W,4)
k=4;S=S.repeat(k,0).repeat(k,1);bg=np.array([.16,.42,.5],np.float32)
o=np.concatenate([S[...,:3]*S[...,3:4]+bg*(1-S[...,3:4]),np.ones_like(S[...,:1])],-1)
r=bpy.data.images.new('p',W*k,H*k,alpha=True);r.pixels.foreach_set(o.reshape(-1));r.filepath_raw=a[1];r.file_format='PNG';r.save()
