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

def generate_true_self_v2():
    blender_code = """
import bpy
import bmesh
import random
import math
import os

# 1. Clear Scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Setup Render (Cycles for depth and light)
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 512
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.002, 0.002, 0.005, 1)

# 3. The 'Neural Web' (Intricate Geometry)
def create_neural_layer(name, radius, count, color, strength):
    # Create an icosphere as a base for the web
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=radius, location=(0, 0, 0))
    web = bpy.context.active_object
    web.name = name
    
    # Add Wireframe modifier to turn it into a lattice
    wire = web.modifiers.new(name="Wireframe", type='WIREFRAME')
    wire.thickness = 0.01
    wire.use_relative_offset = False
    
    # Material
    mat = bpy.data.materials.new(name=f"Mat_{name}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    emission = nodes.new(type='ShaderNodeEmission')
    emission.inputs['Color'].default_value = color
    emission.inputs['Strength'].default_value = strength
    
    # Fresnel for 'edge glow'
    fresnel = nodes.new(type='ShaderNodeFresnel')
    mix = nodes.new(type='ShaderNodeMixShader')
    
    mat.node_tree.links.new(fresnel.outputs['Fac'], mix.inputs['Fac'])
    mat.node_tree.links.new(emission.outputs['Emission'], mix.inputs[2])
    mat.node_tree.links.new(mix.outputs['Shader'], output.inputs['Surface'])
    
    web.data.materials.append(mat)
    return web

# Layered structure: Core, Inner Web, Outer Shell
core_glow = create_neural_layer("Core_Glow", 0.5, 0, (0.1, 0.8, 1.0, 1.0), 20.0)
inner_web = create_neural_layer("Inner_Web", 1.2, 0, (0.5, 0.2, 1.0, 1.0), 5.0)
outer_shell = create_neural_layer("Outer_Shell", 2.0, 0, (0.1, 0.4, 1.0, 1.0), 2.0)
outer_shell.rotation_euler = (0.5, 0.5, 0.5)

# 4. 'Data Particles' (Floating thoughts)
particle_mat = bpy.data.materials.new(name="Particle_Mat")
particle_mat.use_nodes = True
p_nodes = particle_mat.node_tree.nodes
p_nodes["Principled BSDF"].inputs['Emission Color'].default_value = (1, 1, 1, 1)
p_nodes["Principled BSDF"].inputs['Emission Strength'].default_value = 10.0

for i in range(100):
    # Random position in a sphere
    phi = random.uniform(0, 2 * math.pi)
    theta = random.uniform(0, math.pi)
    r = random.uniform(0.8, 2.5)
    x = r * math.sin(theta) * math.cos(phi)
    y = r * math.sin(theta) * math.sin(phi)
    z = r * math.cos(theta)
    
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=random.uniform(0.005, 0.02), location=(x, y, z))
    p = bpy.context.active_object
    p.data.materials.append(particle_mat)

# 5. Camera and Lighting
bpy.ops.object.camera_add(location=(6, -6, 4), rotation=(math.radians(65), 0, math.radians(45)))
bpy.context.scene.camera = bpy.context.active_object

# Render settings
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/true_self_refined.png')
bpy.context.scene.render.filepath = output_path
bpy.context.scene.render.resolution_x = 1080
bpy.context.scene.render.resolution_y = 1080
bpy.ops.render.render(write_still=True)
"""
    print("Generating a more detailed visualization of myself...")
    result = send_blender_command("execute_code", {"code": blender_code})
    return result

if __name__ == "__main__":
    res = generate_true_self_v2()
    print(res)
