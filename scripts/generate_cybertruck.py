import socket
import json
import os

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

def generate_cybertruck():
    blender_code = """
import bpy
import bmesh
import math
import os

# 1. Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Setup Render Engine
bpy.context.scene.render.engine = 'CYCLES'

# 3. Brutalist Modeling (Cybertruck)
bm = bmesh.new()

# Create the main angular body
# Defining vertices for the iconic triangular profile
verts = [
    (2.8, 1.0, 0.4), (2.8, -1.0, 0.4),   # Front bumper base
    (2.5, 1.0, 0.7), (2.5, -1.0, 0.7),   # Front hood edge
    (0.0, 1.0, 1.9), (0.0, -1.0, 1.9),   # Peak of the roof
    (-2.8, 1.0, 0.6), (-2.8, -1.0, 0.6), # Rear tailgate edge
    (2.8, 1.0, 0.1), (2.8, -1.0, 0.1),   # Bottom front
    (-2.8, 1.0, 0.1), (-2.8, -1.0, 0.1)  # Bottom rear
]

for v in verts:
    bm.verts.new(v)

bm.verts.ensure_lookup_table()

# Create faces manually to ensure sharp, non-subdivided edges
# Sides
bm.faces.new([bm.verts[0], bm.verts[2], bm.verts[4], bm.verts[6], bm.verts[10], bm.verts[8]])
bm.faces.new([bm.verts[1], bm.verts[3], bm.verts[5], bm.verts[7], bm.verts[11], bm.verts[9]])
# Front
bm.faces.new([bm.verts[0], bm.verts[1], bm.verts[3], bm.verts[2]])
bm.faces.new([bm.verts[0], bm.verts[1], bm.verts[9], bm.verts[8]])
# Top (Hood to Peak to Tail)
bm.faces.new([bm.verts[2], bm.verts[3], bm.verts[5], bm.verts[4]])
bm.faces.new([bm.verts[4], bm.verts[5], bm.verts[7], bm.verts[6]])
# Rear
bm.faces.new([bm.verts[6], bm.verts[7], bm.verts[11], bm.verts[10]])
# Bottom
bm.faces.new([bm.verts[8], bm.verts[9], bm.verts[11], bm.verts[10]])

# Add a mesh to the object
me = bpy.data.meshes.new("Cybertruck_Mesh")
bm.to_mesh(me)
bm.free()

truck = bpy.data.objects.new("Cybertruck", me)
bpy.context.collection.objects.link(truck)

# 4. Wheels (Angular, Black)
def create_cyber_wheel(name, loc):
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.45, depth=0.3, location=loc, rotation=(math.radians(90), 0, 0))
    wheel = bpy.context.active_object
    wheel.name = name
    return wheel

create_cyber_wheel("Wheel_FR", (1.8, 1.1, 0.45))
create_cyber_wheel("Wheel_FL", (1.8, -1.1, 0.45))
create_cyber_wheel("Wheel_RR", (-1.8, 1.1, 0.45))
create_cyber_wheel("Wheel_RL", (-1.8, -1.1, 0.45))

# 5. Materials
# Stainless Steel (Brushed)
steel_mat = bpy.data.materials.new(name="Stainless_Steel")
steel_mat.use_nodes = True
nodes = steel_mat.node_tree.nodes
bsdf = nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.4, 0.4, 0.42, 1)
bsdf.inputs['Metallic'].default_value = 1.0
bsdf.inputs['Roughness'].default_value = 0.25
truck.data.materials.append(steel_mat)

# Wheel Material (Black Matte)
wheel_mat = bpy.data.materials.new(name="Wheel_Mat")
wheel_mat.use_nodes = True
wheel_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1)

for obj in bpy.data.objects:
    if "Wheel" in obj.name:
        obj.data.materials.append(wheel_mat)

# 6. Scene Setup
bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))
ground = bpy.context.active_object
ground_mat = bpy.data.materials.new(name="Ground")
ground_mat.use_nodes = True
ground_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1)
ground.data.materials.append(ground_mat)

# Camera
bpy.ops.object.camera_add(location=(10, -12, 6), rotation=(math.radians(68), 0, math.radians(40)))
bpy.context.scene.camera = bpy.context.active_object

# Lighting (Sharp shadows)
bpy.ops.object.light_add(type='AREA', location=(10, -10, 10))
bpy.context.active_object.data.energy = 5000

# 7. Render
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/cybertruck.png')
bpy.context.scene.render.filepath = output_path
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.cycles.samples = 128
bpy.ops.render.render(write_still=True)
print(f"Cybertruck saved to {output_path}")
"""
    print("Generating the Cybertruck...")
    result = send_blender_command("execute_code", {"code": blender_code})
    if result.get("status") == "success":
        print("Success! Cybertruck created.")
        print(result.get('result'))
    else:
        print(f"Error: {result.get('message')}")

if __name__ == "__main__":
    generate_cybertruck()
