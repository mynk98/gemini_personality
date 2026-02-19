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

def create_perfect_platform():
    blender_code = """
import bpy
import bmesh
import math
import os

# 1. Cleanup everything
for obj in bpy.data.objects:
    bpy.data.objects.remove(obj, do_unlink=True)
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat, do_unlink=True)

# 2. Setup Scene & Render
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 512
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.001, 0.001, 0.003, 1) # Deep space dark

# 3. Create Geometry (Detailed Hexagon)
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=2.5, depth=0.8, location=(0, 0, 0))
platform = bpy.context.active_object
platform.name = "Perfect_Platform"

# Beveling logic
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(platform.data)
bm.edges.ensure_lookup_table()

# Bevel only top and bottom rims first
rim_edges = [e for e in bm.edges if all(abs(v.co.z) > 0.39 for v in e.verts)]
bmesh.ops.bevel(bm, geom=rim_edges, offset=0.1, segments=2, profile=0.5)

# Update and Unwrap
bmesh.update_edit_mesh(platform.data)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.shade_smooth()
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project()
bpy.ops.object.mode_set(mode='OBJECT')

# 4. Materials
# Rock Material (Dark and Rugged)
rock_mat = bpy.data.materials.get('aerial_rocks_02')
if not rock_mat:
    rock_mat = bpy.data.materials.new(name="Dark_Rock")
    rock_mat.use_nodes = True
    bsdf = rock_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1) # Very dark rock
    bsdf.inputs['Roughness'].default_value = 0.8

# Neon Magenta (Corrected for non-washout)
neon_mat = bpy.data.materials.new(name="True_Neon")
neon_mat.use_nodes = True
nodes = neon_mat.node_tree.nodes
nodes.clear()
output = nodes.new(type='ShaderNodeOutputMaterial')
emission = nodes.new(type='ShaderNodeEmission')
# A deep, saturated magenta
emission.inputs['Color'].default_value = (1.0, 0.0, 0.5, 1.0)
emission.inputs['Strength'].default_value = 15.0 # High but not infinite
neon_mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])

# Assign Materials
platform.data.materials.append(rock_mat)
platform.data.materials.append(neon_mat) # Index 1

# 5. Precise Face Selection for Neon Strips
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(platform.data)
bm.faces.ensure_lookup_table()

for f in bm.faces:
    # Select only the narrow bevel faces created at the rims
    if 0.1 < abs(f.normal.z) < 0.9: # Slanted faces (bevels)
        if any(abs(v.co.z) > 0.35 for v in f.verts):
            f.material_index = 1

bmesh.update_edit_mesh(platform.data)
bpy.ops.object.mode_set(mode='OBJECT')

# 6. Compositing (Crucial for Neon Glow)
bpy.context.scene.use_nodes = True
c_nodes = bpy.context.scene.node_tree.nodes
c_links = bpy.context.scene.node_tree.links
c_nodes.clear()

render_layers = c_nodes.new(type='CompositorNodeRLayers')
glare = c_nodes.new(type='CompositorNodeGlare')
glare.glare_type = 'FOG_GLOW'
glare.size = 8
glare.threshold = 0.5
composite = c_nodes.new(type='CompositorNodeComposite')

c_links.new(render_layers.outputs['Image'], glare.inputs['Image'])
c_links.new(glare.outputs['Image'], composite.inputs['Image'])

# 7. Scene Setup
bpy.ops.object.camera_add(location=(8, -10, 6), rotation=(math.radians(65), 0, math.radians(40)))
bpy.context.scene.camera = bpy.context.active_object

# Lighting
bpy.ops.object.light_add(type='AREA', location=(5, 5, 10))
bpy.context.active_object.data.energy = 1000
bpy.context.active_object.data.color = (0.7, 0.8, 1.0) # Subtle blue fill

# 8. Render
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/perfect_platform.png')
bpy.context.scene.render.filepath = output_path
bpy.context.scene.render.resolution_x = 1080
bpy.context.scene.render.resolution_y = 1080
bpy.ops.render.render(write_still=True)
"""
    print("Generating the Perfect Platform with realistic neon and rock...")
    result = send_blender_command("execute_code", {"code": blender_code})
    return result

if __name__ == "__main__":
    res = create_perfect_platform()
    print(res)
