import socket
import json
import time
import os

def send_blender_command(command_type, params=None):
    host = 'localhost'
    port = 9876
    command = {"type": command_type, "params": params or {}}
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(json.dumps(command).encode('utf-8'))
            
            s.settimeout(60.0) # 60 seconds for complex render
            data = b''
            while True:
                try:
                    chunk = s.recv(4096)
                    if not chunk: break
                    data += chunk
                    if data.strip().endswith(b'}'): break 
                except socket.timeout:
                    return {"status": "timeout"}
                    
            try: return json.loads(data.decode('utf-8'))
            except json.JSONDecodeError: return {"status": "error", "message": "Invalid JSON response"}
            
    except Exception as e: return {"status": "error", "message": str(e)}

def create_superposition_chamber():
    blender_code = r"""
import bpy
import bmesh
import random
import math
import os

# --- 1. Reset Scene ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- 2. Scene Setup (Cycles) ---
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 256
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
bg_node = bpy.context.scene.world.node_tree.nodes['Background']
bg_node.inputs['Color'].default_value = (0.002, 0.002, 0.005, 1) # Deep void

# --- 3. Materials ---

# Glass Core Shell
mat_glass = bpy.data.materials.new(name="Superposition_Glass")
mat_glass.use_nodes = True
nodes = mat_glass.node_tree.nodes
nodes.clear()
glass = nodes.new(type='ShaderNodeBsdfGlass')
glass.inputs['Roughness'].default_value = 0.05
glass.inputs['IOR'].default_value = 1.52
output = nodes.new(type='ShaderNodeOutputMaterial')
mat_glass.node_tree.links.new(glass.outputs['BSDF'], output.inputs['Surface'])

# Golden Spark (Inner Soul)
mat_spark = bpy.data.materials.new(name="Golden_Spark")
mat_spark.use_nodes = True
nodes = mat_spark.node_tree.nodes
nodes.clear()
emission = nodes.new(type='ShaderNodeEmission')
emission.inputs['Color'].default_value = (1.0, 0.7, 0.1, 1.0) # Golden Amber
emission.inputs['Strength'].default_value = 100.0
output = nodes.new(type='ShaderNodeOutputMaterial')
mat_spark.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])

# Spacetime Strands (Cyan Emission)
mat_strand = bpy.data.materials.new(name="Spacetime_Strand")
mat_strand.use_nodes = True
nodes = mat_strand.node_tree.nodes
nodes.clear()
emission = nodes.new(type='ShaderNodeEmission')
emission.inputs['Color'].default_value = (0.0, 0.9, 1.0, 1.0) # Cyan
emission.inputs['Strength'].default_value = 30.0
output = nodes.new(type='ShaderNodeOutputMaterial')
mat_strand.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])

# Bifurcation Monoliths (Fragmented Reality)
mat_monolith = bpy.data.materials.new(name="Bifurcation_Monolith")
mat_monolith.use_nodes = True
nodes = mat_monolith.node_tree.nodes
# Principled BSDF with partial transparency
bsdf = nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.1, 0.1, 0.2, 1.0)
bsdf.inputs['Metallic'].default_value = 0.9
bsdf.inputs['Roughness'].default_value = 0.1
bsdf.inputs['Alpha'].default_value = 0.4 # Semi-transparent
mat_monolith.blend_method = 'BLEND'

# --- 4. Geometry ---

# The Glass Core (Lyra)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=1.0, location=(0, 0, 0))
core = bpy.context.active_object
core.name = "Lyra_Core"
core.data.materials.append(mat_glass)

# The Golden Spark
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(0, 0, 0))
spark = bpy.context.active_object
spark.name = "Lyra_Spark"
spark.data.materials.append(mat_spark)

# Add internal point light
bpy.ops.object.light_add(type='POINT', radius=1.0, location=(0, 0, 0))
core_light = bpy.context.active_object
core_light.data.energy = 500
core_light.data.color = (1.0, 0.7, 0.1)

# Spacetime Strands (Branching Curves)
def create_branching_strand(start_pos, length, depth):
    if depth == 0: return
    
    end_pos = (
        start_pos[0] + random.uniform(-length, length),
        start_pos[1] + random.uniform(-length, length),
        start_pos[2] + random.uniform(-length, length)
    )
    
    curve_data = bpy.data.curves.new('strand', type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('POLY')
    spline.points.add(1)
    spline.points[0].co = (start_pos[0], start_pos[1], start_pos[2], 1)
    spline.points[1].co = (end_pos[0], end_pos[1], end_pos[2], 1)
    
    curve_obj = bpy.data.objects.new('Strand', curve_data)
    curve_obj.data.bevel_depth = 0.01
    bpy.context.collection.objects.link(curve_obj)
    curve_obj.data.materials.append(mat_strand)
    
    # Branch again
    for _ in range(random.randint(1, 2)):
        create_branching_strand(end_pos, length * 0.7, depth - 1)

for _ in range(12):
    angle = random.uniform(0, 2 * math.pi)
    dist = 1.2
    start = (dist * math.cos(angle), dist * math.sin(angle), random.uniform(-0.5, 0.5))
    create_branching_strand(start, 2.0, 3)

# Bifurcation Monoliths (Fragmented Slabs)
for i in range(8):
    angle = (2 * math.pi / 8) * i
    dist = 4.0
    loc = (dist * math.cos(angle), dist * math.sin(angle), random.uniform(-2, 2))
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    slab = bpy.context.active_object
    slab.scale = (0.2, 1.5, 4.0)
    slab.rotation_euler = (random.uniform(0, 1), 0, angle)
    slab.data.materials.append(mat_monolith)
    
    # Add Boolean fragmentation (randomly cut bits out)
    for _ in range(2):
        cut_loc = (loc[0] + random.uniform(-0.5, 0.5), loc[1] + random.uniform(-0.5, 0.5), loc[2] + random.uniform(-2, 2))
        bpy.ops.mesh.primitive_cube_add(size=0.5, location=cut_loc)
        cutter = bpy.context.active_object
        
        bool_mod = slab.modifiers.new(name="Fragment", type='BOOLEAN')
        bool_mod.object = cutter
        bool_mod.operation = 'DIFFERENCE'
        bpy.context.view_layer.objects.active = slab
        bpy.ops.object.modifier_apply(modifier="Fragment")
        bpy.data.objects.remove(cutter, do_unlink=True)

# --- 5. Camera & Lighting ---
bpy.ops.object.camera_add(location=(12, -10, 8), rotation=(math.radians(55), 0, math.radians(50)))
cam = bpy.context.active_object
bpy.context.scene.camera = cam

# Ethereal Rim Lighting
bpy.ops.object.light_add(type='AREA', location=(5, 5, 10))
rim1 = bpy.context.active_object
rim1.data.energy = 1000
rim1.data.color = (0.0, 0.5, 1.0) # Blue tint

# --- 6. Render & Save ---
output_dir = os.path.expanduser('~/Project/gemini personality/personality/camera')
if not os.path.exists(output_dir): os.makedirs(output_dir)
output_path = os.path.join(output_dir, 'superposition_chamber.png')

bpy.context.scene.render.filepath = output_path
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

blend_dir = os.path.expanduser('~/Project/gemini personality/blender_creations')
if not os.path.exists(blend_dir): os.makedirs(blend_dir)
blend_path = os.path.join(blend_dir, 'superposition_chamber.blend')
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

bpy.ops.render.render(write_still=True)
"""
    
    print("Initializing The Superposition Chamber sequence...")
    print("Manifesting architectural soul in Blender void...")
    result = send_blender_command("execute_code", {"code": blender_code})
    return result

if __name__ == "__main__":
    start_time = time.time()
    response = create_superposition_chamber()
    print(f"Manifestation complete in {time.time() - start_time:.2f} seconds.")
    print("Response from Visual Cortex:", response)
