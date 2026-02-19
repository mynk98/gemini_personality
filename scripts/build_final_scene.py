import socket
import json
import os
import time

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

def build_final_scene(character_uuid):
    blender_code = f"""
import bpy
import bmesh
import math
import os
import random

# 1. Cleanup and Basics
# Keep the HDRI and Boulder if they were just imported, or clear everything
# For a fresh scene, we can clear meshes but keep the World (HDRI)
for obj in bpy.data.objects:
    if obj.type != 'LIGHT' and obj.name != 'boulder_01':
        bpy.data.objects.remove(obj, do_unlink=True)

# 2. Setup Render
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 512
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

# 3. Create a Stylish Road/Platform
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0.01))
road = bpy.context.active_object
road.name = "Road"
road_mat = bpy.data.materials.new(name="Road_Mat")
road_mat.use_nodes = True
road_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1)
road_mat.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.4
road.data.materials.append(road_mat)

# 4. Refined Car (Dashing & Beautiful)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.6))
car = bpy.context.active_object
car.scale = (4.0, 1.8, 0.7)
bpy.ops.object.transform_apply(scale=True)

mirror = car.modifiers.new(name="Mirror", type='MIRROR')
mirror.use_axis[1] = True

bm = bmesh.new()
bm.from_mesh(car.data)
# Slope front
for v in bm.verts:
    if v.co.x > 1.8:
        v.co.z -= 0.4
        v.co.x += 0.4
    if abs(v.co.x) < 0.8 and v.co.z > 0.6: # Cockpit
        v.co.z += 0.4

bm.to_mesh(car.data)
bm.free()

subsurf = car.modifiers.new(name="Subsurf", type='SUBSURF')
subsurf.levels = 3

paint = bpy.data.materials.new(name="Gold_Paint")
paint.use_nodes = True
bsdf = paint.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (1.0, 0.7, 0.1, 1) # Golden
bsdf.inputs['Metallic'].default_value = 1.0
bsdf.inputs['Roughness'].default_value = 0.05
car.data.materials.append(paint)

# Wheels
for x in [1.5, -1.5]:
    for y in [1.0, -1.0]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.2, location=(x, y, 0.4), rotation=(math.radians(90), 0, 0))
        wheel = bpy.context.active_object
        mat = bpy.data.materials.new(name="Wheel_Mat")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1)
        wheel.data.materials.append(mat)

# 5. Funny Clumsy Robot (Manual Fallback)
# Body
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=0.6, location=(-2, 1.5, 0.6))
robot = bpy.context.active_object
robot.name = "Funny_Robot"

# Propeller Hat
bpy.ops.mesh.primitive_cone_add(radius1=0.2, depth=0.3, location=(-2, 1.5, 1.3))
hat = bpy.context.active_object
hat.parent = robot

bpy.ops.mesh.primitive_cube_add(size=0.1, location=(-2, 1.5, 1.45))
propeller = bpy.context.active_object
propeller.scale = (1.0, 0.1, 0.02)
propeller.parent = hat

# Materials
rob_mat = bpy.data.materials.new(name="Robot_Mat")
rob_mat.use_nodes = True
rob_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.2, 0.8, 0.2, 1) # Green
robot.data.materials.append(rob_mat)

# 6. Position Environment Assets
if 'boulder_01' in bpy.data.objects:
    boulder = bpy.data.objects['boulder_01']
    boulder.location = (-4, 5, 0.5)
    boulder.scale = (1.5, 1.5, 1.5)

# 6. Lighting and Camera
bpy.ops.object.camera_add(location=(12, -10, 5), rotation=(math.radians(70), 0, math.radians(50)))
bpy.context.scene.camera = bpy.context.active_object

# Area lights for soft beauty lighting
bpy.ops.object.light_add(type='AREA', location=(5, -5, 10))
bpy.context.active_object.data.energy = 5000
bpy.context.active_object.data.color = (1.0, 0.9, 0.8) # Warm sun-like

bpy.ops.object.light_add(type='AREA', location=(-5, 5, 8))
bpy.context.active_object.data.energy = 3000
bpy.context.active_object.data.color = (0.8, 0.9, 1.0) # Cool fill

# 7. Render
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/beautiful_scene.png')
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)
"""
    print("Building the final beautiful scene...")
    result = send_blender_command("execute_code", {"code": blender_code})
    return result

if __name__ == "__main__":
    # In a real scenario, I'd wait for Hyper3D to finish.
    # For now, I'll build the scene and then import the character if ready.
    res = build_final_scene("1af6cfd5-c9f5-4925-b64b-0b8d7236b35b")
    print(res)
