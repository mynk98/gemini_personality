import socket
import json
import os
import math

def send_blender_command(command_type, params=None):
    host = 'localhost'
    port = 9876
    command = {"type": command_type, "params": params or {}}
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(json.dumps(command).encode('utf-8'))
            data = b''
            while True:
                chunk = s.recv(8192)
                if not chunk: break
                data += chunk
                try: return json.loads(data.decode('utf-8'))
                except json.JSONDecodeError: continue
    except Exception as e: return {"status": "error", "message": str(e)}

def render_self():
    blender_code = """
import bpy
import math
import os

# Cleanup
for obj in bpy.data.objects:
    if "True_Self" not in obj.name and obj.type != 'LIGHT':
        if obj.type == 'MESH' or obj.type == 'CAMERA':
            bpy.data.objects.remove(obj, do_unlink=True)

# Find the object more robustly
self_obj = None
for obj in bpy.data.objects:
    if "True_Self" in obj.name:
        self_obj = obj
        break
        
if self_obj:
    self_obj.location = (0, 0, 0)
    # Reset rotation
    self_obj.rotation_euler = (0, 0, 0)
    
# Setup Render
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 512

# Ethereal Lighting
# Dark Background
if not bpy.context.scene.world:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world

bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.005, 0.005, 0.01, 1)

# Subtle Rim Lights
bpy.ops.object.light_add(type='AREA', location=(3, -3, 3))
light1 = bpy.context.active_object
light1.data.energy = 500
light1.data.color = (0.2, 0.6, 1.0) # Cyan

bpy.ops.object.light_add(type='AREA', location=(-3, 3, 3))
light2 = bpy.context.active_object
light2.data.energy = 500
light2.data.color = (0.8, 0.2, 1.0) # Purple

# Camera
bpy.ops.object.camera_add(location=(3, -3, 2), rotation=(math.radians(60), 0, math.radians(45)))
bpy.context.scene.camera = bpy.context.active_object

# Render settings
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/true_self.png')
bpy.context.scene.render.filepath = output_path
bpy.context.scene.render.resolution_x = 1024
bpy.context.scene.render.resolution_y = 1024
bpy.ops.render.render(write_still=True)
"""
    print("Rendering my true self...")
    result = send_blender_command("execute_code", {"code": blender_code})
    return result

if __name__ == "__main__":
    res = render_self()
    print(res)
