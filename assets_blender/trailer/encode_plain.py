# Encode a frame folder to a silent H.264 MP4 (review clips). Run:
# D:\Blender\blender.exe -b -P encode_plain.py -- <frames_dir> <out.mp4> <width> <height> [fps]
import bpy, os, sys
a = sys.argv[sys.argv.index('--') + 1:]
FR, OUT, W, H = a[0], a[1], int(a[2]), int(a[3]); FPS = int(a[4]) if len(a) > 4 else 30
files = sorted(f for f in os.listdir(FR) if f.endswith('.jpg'))
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, H, 100
sc.render.fps, sc.render.fps_base = FPS, 1
sc.frame_start, sc.frame_end = 1, len(files)
if not sc.sequence_editor: sc.sequence_editor_create()
se = sc.sequence_editor
coll = se.strips if hasattr(se, 'strips') else se.sequences
im = coll.new_image('frames', os.path.join(FR, files[0]), 1, 1)
for f in files[1:]: im.elements.append(f)
im.frame_final_duration = len(files)
if hasattr(sc.render.image_settings, 'media_type'): sc.render.image_settings.media_type = 'VIDEO'
sc.render.image_settings.file_format = 'FFMPEG'
ff = sc.render.ffmpeg
ff.format = 'MPEG4'; ff.codec = 'H264'; ff.constant_rate_factor = 'HIGH'
ff.ffmpeg_preset = 'GOOD'; ff.gopsize = 30; ff.use_max_b_frames = False; ff.audio_codec = 'NONE'
sc.render.filepath = OUT
sc.view_settings.view_transform = 'Standard'
bpy.ops.render.render(animation=True)
print('ENCODED', OUT, len(files), 'frames')
