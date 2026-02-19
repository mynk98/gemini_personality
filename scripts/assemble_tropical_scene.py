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

def assemble_scene():
    blender_code = """
import bpy
import math
import os

# Setup Render
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 256

# 1. Position Models
hut = bpy.data.objects.get('Tropical_Hut')
if hut:
    hut.location = (0, 0, 1.5)
    hut.scale = (2, 2, 2)
    hut.rotation_euler = (math.radians(90), 0, 0)

pool = bpy.data.objects.get('Swimming_Pool')
if pool:
    pool.location = (5, 0, 0.05)
    pool.scale = (4, 4, 4)
    pool.rotation_euler = (math.radians(90), 0, 0)

tree = bpy.data.objects.get('Banana_Tree')
if tree:
    tree.location = (-3, -3, 1.8)
    tree.scale = (2, 2, 2)
    tree.rotation_euler = (math.radians(90), 0, 0)

# 2. Create Fencing (Manual)
fence_mat = bpy.data.materials.new(name="Fence_Mat")
fence_mat.use_nodes = True
fence_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.3, 0.2, 0.1, 1)

def create_fence_post(loc):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=1.5, location=loc)
    post = bpy.context.active_object
    post.data.materials.append(fence_mat)

# Create a square fence around the scene
for x in [-8, 8]:
    for y in range(-8, 9, 2):
        create_fence_post((x, y, 0.75))
for y in [-8, 8]:
    for x in range(-8, 9, 2):
        create_fence_post((x, y, 0.75))

# 3. Ground and Lighting
bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))
ground = bpy.context.active_object
ground_mat = bpy.data.materials.new(name="Sand")
ground_mat.use_nodes = True
ground_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.9, 0.8, 0.6, 1)
ground.data.materials.append(ground_mat)

# HDRI (Cape Hill) should already be there from previous step
# If not, add a sun
bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
bpy.context.active_object.data.energy = 5

# 4. Camera
bpy.ops.object.camera_add(location=(20, -20, 15), rotation=(math.radians(60), 0, math.radians(45)))
bpy.context.scene.camera = bpy.context.active_object

# Render settings
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/tropical_scene.png')
bpy.context.scene.render.filepath = output_path
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.ops.render.render(write_still=True)
"""
    print("Assembling and rendering the tropical scene...")
    result = send_blender_command("execute_code", {"code": blender_code})
    return result

if __name__ == "__main__":
    res = assemble_scene()
    print(res)
