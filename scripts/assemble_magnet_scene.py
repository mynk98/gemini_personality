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

def assemble_magnet_scene():
    blender_code = """
import bpy
import bmesh
import math
import os

# 1. Cleanup Scene (Keep the Magnet)
for obj in bpy.data.objects:
    if "Rope_Magnet" not in obj.name and obj.type != 'LIGHT':
        bpy.data.objects.remove(obj, do_unlink=True)

# 2. Re-create the 'Alive Platform' (Manual precise version)
def create_alive_platform():
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=2.5, depth=0.6, location=(0, 0, 0))
    platform = bpy.context.active_object
    platform.name = "Alive_Platform"
    
    # Bevel
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(platform.data)
    all_edges = [e for e in bm.edges]
    bmesh.ops.bevel(bm, geom=all_edges, offset=0.08, segments=3, profile=0.5)
    bmesh.update_edit_mesh(platform.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    
    # Materials
    rock_mat = bpy.data.materials.new(name="Rock_Texture")
    rock_mat.use_nodes = True
    bsdf = rock_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.03, 1)
    bsdf.inputs['Roughness'].default_value = 0.8
    
    neon_mat = bpy.data.materials.new(name="Neon_Strip")
    neon_mat.use_nodes = True
    n_nodes = neon_mat.node_tree.nodes
    n_nodes.clear()
    n_out = n_nodes.new(type='ShaderNodeOutputMaterial')
    n_emit = n_nodes.new(type='ShaderNodeEmission')
    n_emit.inputs['Color'].default_value = (1.0, 0.0, 0.8, 1.0)
    n_emit.inputs['Strength'].default_value = 20.0
    neon_mat.node_tree.links.new(n_emit.outputs['Emission'], n_out.inputs['Surface'])
    
    platform.data.materials.append(rock_mat)
    platform.data.materials.append(neon_mat)
    
    # Selection for neon
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(platform.data)
    for f in bm.faces:
        if 0.1 < abs(f.normal.z) < 0.9 and any(abs(v.co.z) > 0.25 for v in f.verts):
            f.material_index = 1
    bmesh.update_edit_mesh(platform.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    return platform

platform = create_alive_platform()

# 3. Position the Magnet
magnet = None
for obj in bpy.data.objects:
    if "Rope_Magnet" in obj.name:
        magnet = obj
        break

if magnet:
    magnet.location = (0, 0, 4.0)
    magnet.rotation_euler = (math.radians(90), 0, 0)
    magnet.scale = (1.5, 1.5, 1.5)
    
    # Add Emission to Magnet strips
    for slot in magnet.material_slots:
        if slot.material and slot.material.use_nodes:
            bsdf = slot.material.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                # Set cyan glow
                bsdf.inputs['Emission Color'].default_value = (0.0, 0.8, 1.0, 1.0)
                bsdf.inputs['Emission Strength'].default_value = 10.0

# 4. Create the Rope (Curve)
curve_data = bpy.data.curves.new('Rope', type='CURVE')
curve_data.dimensions = '3D'
curve_obj = bpy.data.objects.new('Rope_Curve', curve_data)
bpy.context.collection.objects.link(curve_obj)

polyline = curve_data.splines.new('POLY')
polyline.points.add(1)
polyline.points[0].co = (0, 0, 4.0, 1)
polyline.points[1].co = (0, 0, 10.0, 1)

curve_data.bevel_depth = 0.05
rope_mat = bpy.data.materials.new(name="Rope_Mat")
rope_mat.use_nodes = True
rope_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.1, 0.1, 0.1, 1)
curve_obj.data.materials.append(rope_mat)

# 5. Scene Setup
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 256
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
bpy.context.scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.002, 0.002, 0.005, 1)

bpy.ops.object.camera_add(location=(10, -10, 6), rotation=(math.radians(65), 0, math.radians(45)))
bpy.context.scene.camera = bpy.context.active_object

# Lighting
bpy.ops.object.light_add(type='AREA', location=(5, -5, 10))
bpy.context.active_object.data.energy = 1000

# Compositor (Fog Glow)
bpy.context.scene.use_nodes = True
c_tree = bpy.context.scene.node_tree
c_tree.nodes.clear()
rl = c_tree.nodes.new(type='CompositorNodeRLayers')
glare = c_tree.nodes.new(type='CompositorNodeGlare')
glare.glare_type = 'FOG_GLOW'
glare.threshold = 0.5
glare.size = 8
comp = c_tree.nodes.new(type='CompositorNodeComposite')
c_tree.links.new(rl.outputs[0], glare.inputs[0])
c_tree.links.new(glare.outputs[0], comp.inputs[0])

# 6. Render
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/magnet_scene.png')
bpy.context.scene.render.filepath = output_path
bpy.context.scene.render.resolution_x = 1080
bpy.context.scene.render.resolution_y = 1080
bpy.ops.render.render(write_still=True)
"""
    print("Assembling the Magnet and Platform scene...")
    result = send_blender_command("execute_code", {"code": blender_code})
    return result

if __name__ == "__main__":
    res = assemble_magnet_scene()
    print(res)
