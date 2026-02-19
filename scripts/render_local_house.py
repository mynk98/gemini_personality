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

def render_house():
    blender_code = """
import bpy
import math
import os

# Cleanup older test cats
for obj in bpy.data.objects:
    if "Local_Hunyuan_Cat" in obj.name:
        bpy.data.objects.remove(obj, do_unlink=True)

# Find newest mesh (the house)
newest_obj = None
for obj in bpy.data.objects:
    if obj.type == 'MESH' and 'Platform' not in obj.name and 'House' not in obj.name:
        newest_obj = obj

if newest_obj:
    newest_obj.name = "Local_Hunyuan_House"
    newest_obj.location = (0, 0, 0)
    newest_obj.scale = (3, 3, 3)
    mat = bpy.data.materials.new(name="House_Clay")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1)
    newest_obj.data.materials.append(mat)

# Setup Render
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

# Lighting
bpy.ops.object.light_add(type='AREA', location=(5, -5, 8))
bpy.context.active_object.data.energy = 1000

# Camera
bpy.ops.object.camera_add(location=(8, -8, 5), rotation=(math.radians(65), 0, math.radians(45)))
bpy.context.scene.camera = bpy.context.active_object

# Render settings
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/local_house_test.png')
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)
"""
    print("Rendering the locally generated house...")
    result = send_blender_command("execute_code", {"code": blender_code})
    return result

if __name__ == "__main__":
    res = render_house()
    print(res)
