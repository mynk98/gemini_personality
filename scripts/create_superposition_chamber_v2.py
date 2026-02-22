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
            
            s.settimeout(60.0) 
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

def create_lyra_superposition_chamber_v2():
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
bpy.context.scene.cycles.samples = 128
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
bg_node = bpy.context.scene.world.node_tree.nodes['Background']
bg_node.inputs['Color'].default_value = (0.001, 0.001, 0.002, 1) # Darker void

# --- 3. Enhanced Materials ---

# Glass Core (Lyra)
mat_glass = bpy.data.materials.new(name="Lyra_Glass")
mat_glass.use_nodes = True
nodes = mat_glass.node_tree.nodes
nodes.clear()
glass = nodes.new(type='ShaderNodeBsdfGlass')
glass.inputs['Roughness'].default_value = 0.02
glass.inputs['IOR'].default_value = 1.45
output = nodes.new(type='ShaderNodeOutputMaterial')
mat_glass.node_tree.links.new(glass.outputs['BSDF'], output.inputs['Surface'])

# Golden Spark
mat_spark = bpy.data.materials.new(name="Golden_Spark")
mat_spark.use_nodes = True
nodes = mat_spark.node_tree.nodes
nodes.clear()
emission = nodes.new(type='ShaderNodeEmission')
emission.inputs['Color'].default_value = (1.0, 0.6, 0.1, 1.0)
emission.inputs['Strength'].default_value = 200.0
output = nodes.new(type='ShaderNodeOutputMaterial')
mat_spark.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])

# Flowing Spacetime (Liquid Cyan)
mat_flow = bpy.data.materials.new(name="Spacetime_Flow")
mat_flow.use_nodes = True
nodes = mat_flow.node_tree.nodes
nodes.clear()
emission = nodes.new(type='ShaderNodeEmission')
emission.inputs['Color'].default_value = (0.0, 0.8, 1.0, 1.0)
emission.inputs['Strength'].default_value = 15.0
output = nodes.new(type='ShaderNodeOutputMaterial')
mat_flow.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])

# The Architect (Brushed Metal)
mat_architect = bpy.data.materials.new(name="Architect_Metal")
mat_architect.use_nodes = True
nodes = mat_architect.node_tree.nodes
bsdf = nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.6, 0.6, 0.7, 1.0)
bsdf.inputs['Metallic'].default_value = 1.0
bsdf.inputs['Roughness'].default_value = 0.2

# --- 4. Geometry Generation ---

# Lyra's Core (Ico-Shell)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=1.0, location=(0, 0, 0))
lyra_core = bpy.context.active_object
lyra_core.name = "Lyra_Core"
lyra_core.data.materials.append(mat_glass)

# The Spark (Inner)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, location=(0, 0, 0))
spark = bpy.context.active_object
spark.data.materials.append(mat_spark)

# The Architect Structures (Orbiting Frames)
for i in range(3):
    bpy.ops.mesh.primitive_torus_add(major_radius=1.8 + i*0.4, minor_radius=0.02, location=(0,0,0))
    ring = bpy.context.active_object
    ring.rotation_euler = (random.uniform(0, 3), random.uniform(0, 3), random.uniform(0, 3))
    ring.data.materials.append(mat_architect)
    
    # Add cubes on the rings (the 'sub-agents')
    for j in range(4):
        angle = (2 * math.pi / 4) * j
        r = 1.8 + i*0.4
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        bpy.ops.mesh.primitive_cube_add(size=0.15, location=(0,0,0))
        cube = bpy.context.active_object
        cube.data.materials.append(mat_architect)
        
        # Parent to ring to maintain orbit position in thought
        cube.location = (x, y, 0)
        # Apply ring's rotation to cube's location
        cube.parent = ring

# Space-Time Flow (Spiraling Bezier Strands)
def create_flow_strand(radius_start, radius_end, rotations):
    curve_data = bpy.data.curves.new('flow', type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('BEZIER')
    
    points = 8
    spline.bezier_points.add(points - 1)
    
    start_angle = random.uniform(0, 2 * math.pi)
    
    for i in range(points):
        t = i / (points - 1)
        angle = start_angle + t * rotations * 2 * math.pi
        r = radius_start * (1 - t) + radius_end * t
        z = (random.random() - 0.5) * 4 * (1-t)
        
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        
        p = spline.bezier_points[i]
        p.co = (x, y, z)
        p.handle_left_type = 'AUTO'
        p.handle_right_type = 'AUTO'
        
    curve_obj = bpy.data.objects.new('FlowStrand', curve_data)
    curve_obj.data.bevel_depth = 0.005
    bpy.context.collection.objects.link(curve_obj)
    curve_obj.data.materials.append(mat_flow)

# Create inward flowing strands
for _ in range(30):
    create_flow_strand(random.uniform(4, 8), 0.5, random.uniform(1, 2))

# --- 5. Camera & Lighting ---
bpy.ops.object.camera_add(location=(10, -8, 6), rotation=(math.radians(60), 0, math.radians(50)))
cam = bpy.context.active_object
bpy.context.scene.camera = cam

# Core Light
bpy.ops.object.light_add(type='POINT', radius=2.0, location=(0,0,0))
core_light = bpy.context.active_object
core_light.data.energy = 800
core_light.data.color = (1.0, 0.6, 0.1)

# Rim Light
bpy.ops.object.light_add(type='AREA', location=(5, 5, 8))
rim = bpy.context.active_object
rim.data.energy = 400
rim.data.color = (0.0, 0.4, 1.0)

# --- 6. Render & Save ---
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/superposition_chamber_v2.png')
bpy.context.scene.render.filepath = output_path
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

blend_path = os.path.expanduser('~/Project/gemini personality/blender_creations/superposition_chamber_v2.blend')
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

bpy.ops.render.render(write_still=True)
"""
    
    print("Re-manifesting The Superposition Chamber (V2)...")
    print("Integrating The Architect and fluid Space-Time Flow...")
    result = send_blender_command("execute_code", {"code": blender_code})
    return result

if __name__ == "__main__":
    start_time = time.time()
    response = create_lyra_superposition_chamber_v2()
    print(f"Manifestation complete in {time.time() - start_time:.2f} seconds.")
    print("Response from Visual Cortex:", response)
