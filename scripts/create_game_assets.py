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

def create_basic_platform():
    blender_code = """
import bpy
import bmesh
import math
import os

# 1. Cleanup
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Setup Render Engine (Cycles for Neon Glow)
bpy.context.scene.render.engine = 'CYCLES'
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
bpy.context.scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.005, 0.005, 0.01, 1)

# 3. Create Geometry (Circular Disc with Bevel)
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=2, depth=0.4, location=(0, 0, 0))
platform = bpy.context.active_object
platform.name = "Basic_Platform"

# Bevel the top edge
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(platform.data)
bm.edges.ensure_lookup_table()

# Find the top rim edges
top_edges = [e for e in bm.edges if all(v.co.z > 0.19 for v in e.verts)]
bmesh.ops.bevel(bm, geom=top_edges, offset=0.1, segments=3, profile=0.5)

bmesh.update_edit_mesh(platform.data)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.shade_smooth()

# 4. Materials
# Base Material (Dark Matte Metal)
base_mat = bpy.data.materials.new(name="Platform_Base")
base_mat.use_nodes = True
bsdf = base_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.05, 1)
bsdf.inputs['Roughness'].default_value = 0.2
bsdf.inputs['Metallic'].default_value = 0.8

# Neon Rim Material (Electric Cyan)
neon_mat = bpy.data.materials.new(name="Neon_Rim")
neon_mat.use_nodes = True
n_nodes = neon_mat.node_tree.nodes
n_nodes.clear()
n_out = n_nodes.new(type='ShaderNodeOutputMaterial')
n_emit = n_nodes.new(type='ShaderNodeEmission')
n_emit.inputs['Color'].default_value = (0.0, 0.8, 1.0, 1.0) # Electric Cyan
n_emit.inputs['Strength'].default_value = 15.0
neon_mat.node_tree.links.new(n_emit.outputs['Emission'], n_out.inputs['Surface'])

# Assign materials
platform.data.materials.append(base_mat)
platform.data.materials.append(neon_mat)

# Assign Neon to the beveled rim faces
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(platform.data)
bm.faces.ensure_lookup_table()
for f in bm.faces:
    # Select faces that are part of the outer vertical edge or bevel
    if any(v.co.z > 0.1 for v in f.verts) and f.normal.z < 0.9:
        f.material_index = 1
bmesh.update_edit_mesh(platform.data)
bpy.ops.object.mode_set(mode='OBJECT')

# 5. Scene Setup (Camera & Light)
bpy.ops.object.camera_add(location=(6, -6, 4), rotation=(math.radians(60), 0, math.radians(45)))
bpy.context.scene.camera = bpy.context.active_object

# Subtle rim light
bpy.ops.object.light_add(type='POINT', location=(3, 3, 5))
bpy.context.active_object.data.energy = 500

# 6. Render
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/basic_platform.png')
bpy.context.scene.render.filepath = output_path
bpy.context.scene.render.resolution_x = 1024
bpy.context.scene.render.resolution_y = 1024
bpy.ops.render.render(write_still=True)
"""
    print("Creating the Basic Platform model...")
    result = send_blender_command("execute_code", {"code": blender_code})
    return result

if __name__ == "__main__":
    res = create_basic_platform()
    print(res)
