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

def create_reference_platform():
    blender_code = """
import bpy
import bmesh
import math
import os

# 1. Cleanup
for obj in bpy.data.objects:
    bpy.data.objects.remove(obj, do_unlink=True)
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat, do_unlink=True)

# 2. Setup Render & World
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 512
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.005, 0.005, 0.01, 1)

# 3. Create Materials FIRST (to ensure they exist)
# Neon Material
neon_mat = bpy.data.materials.new(name="Neon_Light")
neon_mat.use_nodes = True
n_nodes = neon_mat.node_tree.nodes
n_nodes.clear()
n_out = n_nodes.new(type='ShaderNodeOutputMaterial')
n_emit = n_nodes.new(type='ShaderNodeEmission')
n_emit.inputs['Color'].default_value = (1.0, 0.0, 0.8, 1.0) # Magenta
n_emit.inputs['Strength'].default_value = 30.0
neon_mat.node_tree.links.new(n_emit.outputs['Emission'], n_out.inputs['Surface'])

# Rock Material (Using downloaded texture)
rock_mat = bpy.data.materials.get('aerial_rocks_02')
if not rock_mat:
    # Fallback if texture download failed
    rock_mat = bpy.data.materials.new(name="Dark_Rock_Fallback")
    rock_mat.use_nodes = True
    bsdf = rock_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.06, 1)
    bsdf.inputs['Roughness'].default_value = 0.9

# 4. Create Geometry (The "Reference" Shape)
# Base Hexagon (Thick foundation)
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=2.5, depth=0.5, location=(0, 0, -0.25))
base = bpy.context.active_object
base.name = "Platform_Base"

# Light Strip Layer (Slightly smaller, glowing)
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=2.45, depth=0.1, location=(0, 0, 0.05))
light_strip = bpy.context.active_object
light_strip.name = "Platform_Light"

# Top Pad (The walking surface, smaller again)
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=2.3, depth=0.2, location=(0, 0, 0.2))
top_pad = bpy.context.active_object
top_pad.name = "Platform_Top"

# Join them into one object for cleaner management
if bpy.app.version >= (3, 2, 0):
    with bpy.context.temp_override(active_object=base, selected_editable_objects=[base, light_strip, top_pad]):
        bpy.ops.object.join()
else:
    ctx = bpy.context.copy()
    ctx['active_object'] = base
    ctx['selected_editable_objects'] = [base, light_strip, top_pad]
    bpy.ops.object.join(ctx)
platform = base # Now merged

# 5. Apply Materials to Faces
# We need to re-assign materials because joining might have messed them up
platform.data.materials.clear()
platform.data.materials.append(rock_mat) # Slot 0: Rock
platform.data.materials.append(neon_mat) # Slot 1: Neon

bpy.context.view_layer.objects.active = platform
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(platform.data)
bm.faces.ensure_lookup_table()

# Logic: 
# The "Light Strip" faces are the vertical faces between Z=0 and Z=0.1 roughly.
# The "Rock" faces are everything else.
for f in bm.faces:
    f.material_index = 0 # Default to Rock
    
    # Check if this face belongs to the light strip layer
    # It will be a side face (normal Z close to 0)
    # And its Z position will be around 0.05
    z_avg = sum([v.co.z for v in f.verts]) / len(f.verts)
    if abs(f.normal.z) < 0.1 and 0.0 < z_avg < 0.1:
        f.material_index = 1

bmesh.update_edit_mesh(platform.data)

# Bevel the Rock Edges (for realism)
# Select non-neon edges
rock_edges = [e for e in bm.edges if e.verts[0].co.z > 0.15 or e.verts[0].co.z < 0]
bmesh.ops.bevel(bm, geom=rock_edges, offset=0.05, segments=2)
bmesh.update_edit_mesh(platform.data)

bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.shade_smooth()

# 6. Texturing (UV Unwrap & Load Texture)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')

# 7. Compositor (Bloom)
bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree
tree.nodes.clear()
rl = tree.nodes.new('CompositorNodeRLayers')
glare = tree.nodes.new('CompositorNodeGlare')
glare.glare_type = 'FOG_GLOW'
glare.threshold = 0.5
glare.size = 9
comp = tree.nodes.new('CompositorNodeComposite')
tree.links.new(rl.outputs[0], glare.inputs[0])
tree.links.new(glare.outputs[0], comp.inputs[0])

# 8. Camera & Lighting
bpy.ops.object.camera_add(location=(7, -9, 7), rotation=(math.radians(60), 0, math.radians(40)))
bpy.context.scene.camera = bpy.context.active_object

bpy.ops.object.light_add(type='AREA', location=(5, -5, 5))
bpy.context.active_object.data.energy = 500
bpy.context.active_object.data.color = (0.8, 0.8, 1.0) # Cool fill

# 9. Render
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/reference_platform.png')
bpy.context.scene.render.filepath = output_path
bpy.context.scene.render.resolution_x = 1080
bpy.context.scene.render.resolution_y = 1080
bpy.ops.render.render(write_still=True)
"""
    print("Generating the Reference Platform...")
    result = send_blender_command("execute_code", {"code": blender_code})
    return result

if __name__ == "__main__":
    # Note: We will attempt to apply the downloaded texture in a separate step 
    # to keep the logic robust if the download fails.
    # First, run the geometry/material setup.
    res = create_reference_platform()
    print(res)
