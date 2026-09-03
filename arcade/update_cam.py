import bpy
import math

scene = bpy.context.scene
cam = scene.camera

# Framing: track a target empty at center of cabinet
target = bpy.data.objects.get("Cam_Target")
if not target:
    target = bpy.data.objects.new("Cam_Target", None)
    scene.collection.objects.link(target)
target.location = (0.25, 0.0, 0.9) # Center of cabinet (around 36" high)

cam.location = (-3.2, -2.8, 1.5)
# Add TrackTo constraint
for c in cam.constraints:
    cam.constraints.remove(c)
tt = cam.constraints.new(type='TRACK_TO')
tt.target = target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'
cam.data.lens = 35

bpy.ops.wm.save_as_mainfile(filepath="/home/scott/arcade_cabinet_parametric.blend")
