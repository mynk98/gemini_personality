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

def render_bike():
    blender_code = """
import bpy
import math
import os

# Cleanup
for obj in bpy.data.objects:
    if obj.name != 'Sports_Bike' and obj.type != 'LIGHT':
        if obj.type == 'MESH' or obj.type == 'CAMERA':
            bpy.data.objects.remove(obj, do_unlink=True)

bike = bpy.data.objects.get('Sports_Bike')
if bike:
    bike.location = (0, 0, 0.62)
    bike.rotation_euler = (math.radians(90), 0, math.radians(90))

# Setup Render
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 512

# Beautiful Studio Lighting
bpy.ops.object.light_add(type='AREA', location=(4, -4, 5))
light1 = bpy.context.active_object
light1.data.energy = 3000
light1.data.color = (1.0, 1.0, 1.0)

bpy.ops.object.light_add(type='AREA', location=(-4, 4, 3))
light2 = bpy.context.active_object
light2.data.energy = 1000
light2.data.color = (0.8, 0.9, 1.0)

# Camera
bpy.ops.object.camera_add(location=(5, -5, 2.5), rotation=(math.radians(70), 0, math.radians(45)))
bpy.context.scene.camera = bpy.context.active_object

# Render settings
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/sports_bike.png')
bpy.context.scene.render.filepath = output_path
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.ops.render.render(write_still=True)
"""
    print("Rendering the beautiful sports bike...")
    result = send_blender_command("execute_code", {"code": blender_code})
    return result

if __name__ == "__main__":
    res = render_bike()
    print(res)
