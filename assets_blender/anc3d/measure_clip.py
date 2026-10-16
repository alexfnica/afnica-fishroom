# Measure a clip's log: female snout step per frame (game px, 1 unit = 32.5 px), backward frames (moving against the
# facing), lowest point (sinking under the sand), and the worst intrusion of either fish into the clay.
# Run: python measure_clip.py <frames_dir>
import sys, os, json, math, glob
L = []
for f in sorted(glob.glob(os.path.join(sys.argv[1], 'log_*.json'))): L += json.load(open(f))
L.sort(key=lambda r: r['fr']); PX = 32.5
mx = 0; at = None; back = 0
for a, b in zip(L, L[1:]):
    dx, dy = b['female_snout'][0] - a['female_snout'][0], b['female_snout'][1] - a['female_snout'][1]
    st = math.hypot(dx, dy) * PX
    if st > mx: mx, at = st, b['fr']
    if st > .05 and dx * math.cos(b['yaw']) + dy * math.sin(b['yaw']) < -1e-4: back += 1
print('frames', len(L))
print('female snout: max step %.2f game px/frame at frame %s, backward frames %d' % (mx, at, back))
print('female lowest point z = %.3f units (< 0 = under the sand)' % min(r['female_minz'] for r in L))
print('worst clay intrusion: male %.3f, female %.3f (> 0 = a point inside the clay)' % (max(r['male_clay'] for r in L), max(r['female_clay'] for r in L)))
print('tail bend range %.2f .. %.2f rad' % (min(r['bend'] for r in L), max(r['bend'] for r in L)))
