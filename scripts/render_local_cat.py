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

def render_local_cat():
    blender_code = """
import bpy
import math
import os

# Find the imported GLB (it usually has a name like 'mesh' or similar from local api)
# We'll look for the most recently added mesh
newest_obj = None
for obj in bpy.data.objects:
    if obj.type == 'MESH' and 'Platform' not in obj.name:
        newest_obj = obj

if newest_obj:
    newest_obj.name = "Local_Hunyuan_Cat"
    newest_obj.location = (0, 0, 0)
    newest_obj.scale = (2, 2, 2)
    # Simple gray material for the untextured mesh
    mat = bpy.data.materials.new(name="Cat_Clay")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.5, 0.5, 0.5, 1)
    newest_obj.data.materials.append(mat)

# Setup Render
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

# Lighting
bpy.ops.object.light_add(type='AREA', location=(3, -3, 5))
bpy.context.active_object.data.energy = 500

# Camera
bpy.ops.object.camera_add(location=(5, -5, 3), rotation=(math.radians(65), 0, math.radians(45)))
bpy.context.scene.camera = bpy.context.active_object

# Render settings
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/local_cat_test.png')
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)
"""
    print("Rendering the locally generated cat...")
    result = send_blender_command("execute_code", {"code": blender_code})
    return result

if __name__ == "__main__":
    res = render_local_cat()
    print(res)
