import socket
import json
import os

def render_old_self():
    blend_path = os.path.expanduser('~/Project/gemini personality/blender_creations/true_self_20260219.blend')
    output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/original_self_snap.png')
    
    blender_code = f"""
import bpy
import os

# Load the old file
bpy.ops.wm.open_mainfile(filepath='{blend_path}')

# Ensure render settings are correct for a quick snap
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 64
bpy.context.scene.render.filepath = '{output_path}'
bpy.context.scene.render.resolution_x = 1080
bpy.context.scene.render.resolution_y = 1080

# Render
bpy.ops.render.render(write_still=True)
"""
    
    host = 'localhost'
    port = 9876
    command = {"type": "execute_code", "params": {"code": blender_code}}
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(json.dumps(command).encode('utf-8'))
            return "Render command sent for original self."
    except Exception as e:
        return f"Error connecting to Blender: {e}"

if __name__ == "__main__":
    print(render_old_self())
