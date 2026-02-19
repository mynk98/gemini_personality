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

def create_beveled_rock_platform():
    blender_code = """
import bpy
import bmesh
import math
import os

# 1. Cleanup
for obj in bpy.data.objects:
    bpy.data.objects.remove(obj, do_unlink=True)

# 2. Setup Render Engine
bpy.context.scene.render.engine = 'CYCLES'
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
bpy.context.scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.002, 0.002, 0.005, 1)

# 3. Create Geometry (Detailed Hexagon)
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=2.5, depth=0.6, location=(0, 0, 0))
platform = bpy.context.active_object
platform.name = "Rock_Platform"

# Beveling the edges for detail
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(platform.data)
bm.edges.ensure_lookup_table()

# Bevel all edges
all_edges = [e for e in bm.edges]
bmesh.ops.bevel(bm, geom=all_edges, offset=0.05, segments=3, profile=0.5)

bmesh.update_edit_mesh(platform.data)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.shade_smooth()

# 4. Materials
# Rock Material (Using PolyHaven texture)
rock_mat = bpy.data.materials.get('aerial_rocks_02')
if not rock_mat:
    rock_mat = bpy.data.materials.new(name="Rock_Fallback")
    rock_mat.use_nodes = True

# Neon Magenta
magenta_mat = bpy.data.materials.new(name="Neon_Magenta")
magenta_mat.use_nodes = True
nodes = magenta_mat.node_tree.nodes
nodes.clear()
output = nodes.new(type='ShaderNodeOutputMaterial')
emission = nodes.new(type='ShaderNodeEmission')
emission.inputs['Color'].default_value = (1.0, 0.0, 0.8, 1.0)
emission.inputs['Strength'].default_value = 30.0
magenta_mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])

# Assign Materials
platform.data.materials.append(rock_mat)
platform.data.materials.append(magenta_mat) # Index 1

# Apply magenta to the bevels/edges
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(platform.data)
bm.faces.ensure_lookup_table()

# Selection logic: Select faces that are part of the side-bevels
for f in bm.faces:
    # Use normal and position to find edge/bevel faces
    if abs(f.normal.z) < 0.8: # Sideway or beveled faces
        if any(v.co.z > 0.25 or v.co.z < -0.25 for v in f.verts):
             f.material_index = 1

bmesh.update_edit_mesh(platform.data)
bpy.ops.object.mode_set(mode='OBJECT')

# 5. Scene Setup
bpy.ops.object.camera_add(location=(10, -10, 8), rotation=(math.radians(55), 0, math.radians(45)))
bpy.context.scene.camera = bpy.context.active_object

# Lighting (Accent lights to pop the rock texture)
bpy.ops.object.light_add(type='AREA', location=(5, -5, 10))
light1 = bpy.context.active_object
light1.data.energy = 2000
light1.data.color = (0.8, 0.9, 1.0) # Cool rim light

# 6. Render
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/rock_platform_detailed.png')
bpy.context.scene.render.filepath = output_path
bpy.context.scene.render.resolution_x = 1080
bpy.context.scene.render.resolution_y = 1080
bpy.ops.render.render(write_still=True)
"""
    print("Creating the Beveled Rock Platform with Neon Edges...")
    result = send_blender_command("execute_code", {"code": blender_code})
    return result

if __name__ == "__main__":
    res = create_beveled_rock_platform()
    print(res)
