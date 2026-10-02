import bpy, numpy as np
D='D:/Retirement/assets_blender/logo/'; O='D:/Retirement/assets_blender/trailer/'
img=bpy.data.images.load(D+'logo_aquarium_simulator.png'); W,H=img.size
p=np.empty(W*H*4,np.float32); img.pixels.foreach_get(p); S=p.reshape(H,W,4)
lum=S[...,:3].mean(-1); a=np.clip((.93-lum)/.8,0,1)
def save(arr,path):
    h,w=arr.shape[:2]; r=bpy.data.images.new('o',w,h,alpha=True); r.pixels.foreach_set(np.ascontiguousarray(arr,np.float32).reshape(-1)); r.filepath_raw=path; r.file_format='PNG'; r.save(); print('SAVED',path,w,h)
out=np.zeros_like(S); out[...,:3]=1; out[...,3]=a
# keep the fish readable: inside the ring, the fish body has light parts (silver) -> keep them as they are (white on dark looks right when inverted? no: keep original look inside the disc)
ys,xs=np.nonzero(a>.05); crop=out[ys.min():ys.max()+1, xs.min():xs.max()+1]   # blender rows are bottom-up; crop works the same
save(crop, O+'logo_white.png')
