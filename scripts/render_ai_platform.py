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

def render_ai_platform():
    blender_code = """
import bpy
import math
import os

# Cleanup manual platforms
for obj in bpy.data.objects:
    if "Platform_" in obj.name:
        bpy.data.objects.remove(obj, do_unlink=True)

ai_platform = bpy.data.objects.get('AI_Platform')
if ai_platform:
    ai_platform.location = (0, 0, 0.6)
    ai_platform.rotation_euler = (math.radians(90), 0, 0)
    ai_platform.scale = (2, 2, 2)

# Setup Render
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 256

# Lighting
bpy.ops.object.light_add(type='AREA', location=(5, -5, 5))
light1 = bpy.context.active_object
light1.data.energy = 1000

# Camera
bpy.ops.object.camera_add(location=(8, -8, 6), rotation=(math.radians(60), 0, math.radians(45)))
bpy.context.scene.camera = bpy.context.active_object

# Render settings
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/ai_platform_render.png')
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)
"""
    print("Rendering the AI-generated platform...")
    result = send_blender_command("execute_code", {"code": blender_code})
    return result

if __name__ == "__main__":
    res = render_ai_platform()
    print(res)
