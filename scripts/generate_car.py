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

def generate_car():
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
if bpy.context.preferences.addons.get('cycles'):
    bpy.context.scene.cycles.device = 'GPU'

# 3. Advanced Modeling (Better Proportions)
# Create a cube as the base for the main body
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
body = bpy.context.active_object
body.name = "Car_Body"
body.scale = (4.5, 2.0, 0.8) # Proportions: Length, Width, Height
bpy.ops.object.transform_apply(scale=True)

# Add Mirror Modifier for symmetry along the Y-axis
mirror = body.modifiers.new(name="Mirror", type='MIRROR')
mirror.use_axis[0] = False
mirror.use_axis[1] = True

# Shape the body with BMesh
bm = bmesh.new()
bm.from_mesh(body.data)

# Move the front down for an aerodynamic slope
front_verts = [v for v in bm.verts if v.co.x > 2.0]
for v in front_verts:
    v.co.z -= 0.3
    v.co.x += 0.5 # Sharper front

# Define the cockpit area (extrude a cabin)
cabin_faces = [f for f in bm.faces if abs(sum((v.co.x for v in f.verts)) / len(f.verts)) < 1.0 and f.normal.z > 0.9]
if cabin_faces:
    res = bmesh.ops.extrude_discrete_faces(bm, faces=cabin_faces)
    for f in res['faces']:
        bmesh.ops.translate(bm, vec=(-0.2, 0, 0.6), verts=f.verts)
        bmesh.ops.scale(bm, vec=(0.8, 0.7, 1.0), verts=f.verts)

# Create wheel wells (Boolean subtraction or manual bmesh?)
# Let's use BMesh to cut out wheel areas for a better silhouette
for x_dir in [1, -1]:
    for y_dir in [1, -1]:
        # Approximate wheel well positions
        well_verts = [v for v in bm.verts if abs(v.co.x - (x_dir * 1.8)) < 0.6 and abs(v.co.y - (y_dir * 0.9)) < 0.5 and v.co.z < 0.5]
        for v in well_verts:
            v.co.z += 0.2

bm.to_mesh(body.data)
bm.free()

# Add Subdivision Surface for smoothness
subsurf = body.modifiers.new(name="Subsurface", type='SUBSURF')
subsurf.levels = 3
subsurf.render_levels = 4

# Smooth shading
for poly in body.data.polygons:
    poly.use_smooth = True

# 4. Refined Wheels
def create_wheel(name, loc):
    # Add a torus for the tire and a cylinder for the rim
    bpy.ops.mesh.primitive_torus_add(align='WORLD', location=loc, rotation=(math.radians(90), 0, 0), major_radius=0.45, minor_radius=0.15)
    tire = bpy.context.active_object
    tire.name = f"{name}_Tire"
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.2, location=loc, rotation=(math.radians(90), 0, 0))
    rim = bpy.context.active_object
    rim.name = f"{name}_Rim"
    return tire, rim

wheels = [
    create_wheel("FR", (1.8, 1.1, 0.45)),
    create_wheel("FL", (1.8, -1.1, 0.45)),
    create_wheel("RR", (-1.8, 1.1, 0.45)),
    create_wheel("RL", (-1.8, -1.1, 0.45))
]

# 5. Materials
# Sleek Carbon Fiber / Metallic Paint
paint_mat = bpy.data.materials.new(name="Car_Paint")
paint_mat.use_nodes = True
p_nodes = paint_mat.node_tree.nodes
p_nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.1, 0.1, 0.2, 1) # Dark Metallic Blue
p_nodes["Principled BSDF"].inputs['Metallic'].default_value = 1.0
p_nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.05
body.data.materials.append(paint_mat)

# Tire (Rubber)
tire_mat = bpy.data.materials.new(name="Tire_Material")
tire_mat.use_nodes = True
tire_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1)
tire_mat.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.9

# Rim (Chrome)
rim_mat = bpy.data.materials.new(name="Rim_Material")
rim_mat.use_nodes = True
rim_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1)
rim_mat.node_tree.nodes["Principled BSDF"].inputs['Metallic'].default_value = 1.0
rim_mat.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.1

for tire, rim in wheels:
    tire.data.materials.append(tire_mat)
    rim.data.materials.append(rim_mat)

# 6. Scene and Lighting
# Ground with Reflection
bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))
ground = bpy.context.active_object
ground_mat = bpy.data.materials.new(name="Ground")
ground_mat.use_nodes = True
ground_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1)
ground_mat.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.2
ground.data.materials.append(ground_mat)

# 3-Point Studio Lighting
bpy.ops.object.light_add(type='AREA', location=(10, -10, 10))
bpy.context.active_object.data.energy = 8000
bpy.ops.object.light_add(type='AREA', location=(-10, 10, 5))
bpy.context.active_object.data.energy = 3000
bpy.ops.object.light_add(type='AREA', location=(0, 0, 15))
bpy.context.active_object.data.energy = 10000

# 7. Camera and Render
bpy.ops.object.camera_add(location=(10, -12, 6), rotation=(math.radians(68), 0, math.radians(40)))
bpy.context.scene.camera = bpy.context.active_object

output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/refined_car.png')
bpy.context.scene.render.filepath = output_path
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.cycles.samples = 512
bpy.ops.render.render(write_still=True)
print(f"Refined car saved to {output_path}")
"""
    print("Refining the car model to eliminate the 'sausage' look...")
    result = send_blender_command("execute_code", {"code": blender_code})
    if result.get("status") == "success":
        print("Success! The refined car has been created.")
        print(result.get('result'))
    else:
        print(f"Error: {result.get('message')}")
    print("Visualizing and building the dashing car...")
    result = send_blender_command("execute_code", {"code": blender_code})
    if result.get("status") == "success":
        print("Success! The car has been created and rendered.")
        print(result.get('result'))
    else:
        print(f"Error: {result.get('message')}")

if __name__ == "__main__":
    generate_car()
