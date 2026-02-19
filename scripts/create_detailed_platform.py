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

def create_detailed_platform():
    blender_code = """
import bpy
import bmesh
import math
import os

# 1. Cleanup
for obj in bpy.data.objects:
    bpy.data.objects.remove(obj, do_unlink=True)
for mesh in bpy.data.meshes:
    bpy.data.meshes.remove(mesh, do_unlink=True)
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat, do_unlink=True)

# 2. Setup Render Engine
bpy.context.scene.render.engine = 'CYCLES'
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
bpy.context.scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.002, 0.002, 0.005, 1)

# 3. Create Geometry (Hexagonal Tiered Structure)
def create_hexagon_tier(name, radius, height, location):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=radius, depth=height, location=location)
    tier = bpy.context.active_object
    tier.name = name
    return tier

# Base Tier (Magenta Neon)
base = create_hexagon_tier("Platform_Base", 2.2, 0.2, (0, 0, 0.1))
# Middle Tier (Dark Metal)
mid = create_hexagon_tier("Platform_Mid", 2.0, 0.4, (0, 0, 0.3))
# Top Tier (Patterned Metal with Magenta Rim)
top = create_hexagon_tier("Platform_Top", 1.8, 0.1, (0, 0, 0.55))

# Detailing the top with BMesh
bpy.context.view_layer.objects.active = top
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(top.data)
bm.faces.ensure_lookup_table()

# Recess the center
top_face = [f for f in bm.faces if f.normal.z > 0.9][0]
res = bmesh.ops.inset_region(bm, faces=[top_face], thickness=0.2)
for f in res['faces']:
    bmesh.ops.translate(bm, vec=(0, 0, -0.05), verts=f.verts)

bmesh.update_edit_mesh(top.data)
bpy.ops.object.mode_set(mode='OBJECT')

# 4. Materials
# Neon Magenta
magenta_mat = bpy.data.materials.new(name="Neon_Magenta")
magenta_mat.use_nodes = True
nodes = magenta_mat.node_tree.nodes
nodes.clear()
output = nodes.new(type='ShaderNodeOutputMaterial')
emission = nodes.new(type='ShaderNodeEmission')
emission.inputs['Color'].default_value = (1.0, 0.0, 0.8, 1.0) # Vibrant Magenta
emission.inputs['Strength'].default_value = 20.0
magenta_mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])

# Dark Brushed Metal
metal_mat = bpy.data.materials.new(name="Dark_Metal")
metal_mat.use_nodes = True
bsdf = metal_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.08, 1)
bsdf.inputs['Metallic'].default_value = 1.0
bsdf.inputs['Roughness'].default_value = 0.2

# Assign Materials
base.data.materials.append(magenta_mat)
mid.data.materials.append(metal_mat)
top.data.materials.append(metal_mat)
top.data.materials.append(magenta_mat) # Index 1

# Apply magenta to the top rim
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(top.data)
bm.faces.ensure_lookup_table()
for f in bm.faces:
    if f.normal.z < 0.1: # Vertical faces of the top disc
        f.material_index = 1
bmesh.update_edit_mesh(top.data)
bpy.ops.object.mode_set(mode='OBJECT')

# 5. Scene Setup
bpy.ops.object.camera_add(location=(8, -8, 6), rotation=(math.radians(60), 0, math.radians(45)))
bpy.context.scene.camera = bpy.context.active_object

# Lighting
bpy.ops.object.light_add(type='POINT', location=(5, 5, 5))
bpy.context.active_object.data.energy = 1000

# 6. Render
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/detailed_platform.png')
bpy.context.scene.render.filepath = output_path
bpy.context.scene.render.resolution_x = 1080
bpy.context.scene.render.resolution_y = 1080
bpy.ops.render.render(write_still=True)
"""
    print("Creating the Detailed Hexagonal Platform...")
    result = send_blender_command("execute_code", {"code": blender_code})
    return result

if __name__ == "__main__":
    res = create_detailed_platform()
    print(res)
