# Encode the composed frames + the music into the final MP4 (H.264 high quality, AAC), 1080x1920 @ 30 fps.
# Run: D:\Blender\blender.exe -b -P encode.py -- <frames_dir> <music.wav> <out.mp4>
import bpy, os, sys
a = sys.argv[sys.argv.index('--') + 1:]
FR, WAV, OUT = a[0], a[1], a[2]
files = sorted(f for f in os.listdir(FR) if f.endswith('.jpg'))
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1920, 100
sc.render.fps, sc.render.fps_base = 30, 1
sc.frame_start, sc.frame_end = 1, len(files)
if not sc.sequence_editor: sc.sequence_editor_create()
se = sc.sequence_editor
coll = se.strips if hasattr(se, 'strips') else se.sequences
im = coll.new_image('frames', os.path.join(FR, files[0]), 1, 1)
for f in files[1:]: im.elements.append(f)
im.frame_final_duration = len(files)
snd = coll.new_sound('music', WAV, 2, 1)
if hasattr(sc.render.image_settings, 'media_type'): sc.render.image_settings.media_type = 'VIDEO'
sc.render.image_settings.file_format = 'FFMPEG'
ff = sc.render.ffmpeg
ff.format = 'MPEG4'; ff.codec = 'H264'; ff.constant_rate_factor = 'PERC_LOSSLESS' if False else 'HIGH'
ff.ffmpeg_preset = 'GOOD'; ff.gopsize = 30; ff.use_max_b_frames = False
ff.audio_codec = 'AAC'; ff.audio_bitrate = 256; ff.audio_channels = 'STEREO'; ff.audio_mixrate = 44100
sc.render.filepath = OUT
sc.view_settings.view_transform = 'Standard'
bpy.ops.render.render(animation=True)
print('ENCODED', OUT, len(files), 'frames')
