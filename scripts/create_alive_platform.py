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

def create_alive_platform():
    blender_code = """
import bpy
import bmesh
import math
import os

# 1. Clear All
for obj in bpy.data.objects:
    bpy.data.objects.remove(obj, do_unlink=True)
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat, do_unlink=True)

# 2. Setup Cycles & World
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 512
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
bpy.context.scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.001, 0.001, 0.002, 1)

# 3. Create "Rock" Procedural Material
rock_mat = bpy.data.materials.new(name="Procedural_Rock")
rock_mat.use_nodes = True
nodes = rock_mat.node_tree.nodes
links = rock_mat.node_tree.links
nodes.clear()

node_output = nodes.new(type='ShaderNodeOutputMaterial')
node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
node_noise = nodes.new(type='ShaderNodeTexNoise')
node_noise.inputs['Scale'].default_value = 20.0
node_noise.inputs['Detail'].default_value = 15.0

node_color_ramp = nodes.new(type='ShaderNodeValToRGB')
node_color_ramp.color_ramp.elements[0].color = (0.02, 0.02, 0.03, 1) # Dark base
node_color_ramp.color_ramp.elements[1].color = (0.05, 0.05, 0.07, 1) # Lighter highlights

node_bump = nodes.new(type='ShaderNodeBump')
node_bump.inputs['Strength'].default_value = 2.0

links.new(node_noise.outputs['Fac'], node_color_ramp.inputs['Fac'])
links.new(node_color_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])
links.new(node_noise.outputs['Fac'], node_bump.inputs['Height'])
links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])
links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])

# 4. Create "Neon" Material
neon_mat = bpy.data.materials.new(name="Neon_Edge")
neon_mat.use_nodes = True
n_nodes = neon_mat.node_tree.nodes
n_nodes.clear()
n_out = n_nodes.new(type='ShaderNodeOutputMaterial')
n_emit = n_nodes.new(type='ShaderNodeEmission')
n_emit.inputs['Color'].default_value = (1.0, 0.0, 0.5, 1.0) # Vibrant Magenta
n_emit.inputs['Strength'].default_value = 25.0
neon_mat.node_tree.links.new(n_emit.outputs['Emission'], n_out.inputs['Surface'])

# 5. Build Hexagonal Platform (Reference Proportions)
# Create the base structure
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=2.5, depth=0.6, location=(0, 0, 0))
platform = bpy.context.active_object
platform.name = "Alive_Platform"

# Beveling for the "Techno-Rock" look
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(platform.data)
bm.edges.ensure_lookup_table()

# Bevel all edges to create detailed facets
all_edges = [e for e in bm.edges]
bmesh.ops.bevel(bm, geom=all_edges, offset=0.08, segments=3, profile=0.5)

bmesh.update_edit_mesh(platform.data)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.shade_smooth()

# 6. Apply Materials
platform.data.materials.append(rock_mat)
platform.data.materials.append(neon_mat) # Index 1

# Logic: Apply Neon to the specific edges
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(platform.data)
bm.faces.ensure_lookup_table()

for f in bm.faces:
    # Select faces that are likely part of the top/bottom rim bevels
    if 0.1 < abs(f.normal.z) < 0.9: # Slanted bevel faces
        if any(abs(v.co.z) > 0.25 for v in f.verts):
            f.material_index = 1

bmesh.update_edit_mesh(platform.data)
bpy.ops.object.mode_set(mode='OBJECT')

# 7. Compositor (Glow Effect)
bpy.context.scene.use_nodes = True
c_tree = bpy.context.scene.node_tree
c_tree.nodes.clear()
render_layers = c_tree.nodes.new(type='CompositorNodeRLayers')
glare = c_tree.nodes.new(type='CompositorNodeGlare')
glare.glare_type = 'FOG_GLOW'
glare.threshold = 0.5
glare.size = 9
composite = c_tree.nodes.new(type='CompositorNodeComposite')
c_tree.links.new(render_layers.outputs['Image'], glare.inputs['Image'])
c_tree.links.new(glare.outputs['Image'], composite.inputs['Image'])

# 8. Camera & Lighting
bpy.ops.object.camera_add(location=(8, -10, 6), rotation=(math.radians(65), 0, math.radians(40)))
bpy.context.scene.camera = bpy.context.active_object

# Area light to highlight the rock bumps
bpy.ops.object.light_add(type='AREA', location=(5, -5, 10))
light1 = bpy.context.active_object
light1.data.energy = 1500
light1.data.color = (0.8, 0.9, 1.0)

# 9. Render
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/alive_platform.png')
bpy.context.scene.render.filepath = output_path
bpy.context.scene.render.resolution_x = 1080
bpy.context.scene.render.resolution_y = 1080
bpy.ops.render.render(write_still=True)
"""
    print("Generating the Alive Platform with procedural rock and glowing neon...")
    result = send_blender_command("execute_code", {"code": blender_code})
    return result

if __name__ == "__main__":
    res = create_alive_platform()
    print(res)
