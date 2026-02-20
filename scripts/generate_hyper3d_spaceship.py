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
            # Standard socket read for small responses
            data = s.recv(16384).decode('utf-8')
            try: return json.loads(data)
            except: return {'status': 'error', 'message': f'Invalid JSON: {data}'}
    except Exception as e: return {"status": "error", "message": str(e)}

def generate_hyper3d_spaceship():
    print("--- Initiating Hyper3D (Rodin) Generation ---")
    
    # 1. Create Job
    # Using 'text_prompt' as discovered via grep
    res = send_blender_command('create_rodin_job', {
        'text_prompt': 'realistic high-detail industrial sci-fi spaceship, cinematic lighting, greebles, pbr materials, 8k textures', 
        'images': []
    })
    
    if res.get('status') != 'success':
        print(f"Failed to create job: {res}")
        return
    
    # Extract Job ID (Handling multi-job response)
    try:
        # Hyper3D returns a list of job UUIDs for variations. We pick the first one.
        job_id = res['result']['jobs']['uuids'][0]
        print(f"Job Created. Monitoring UUID: {job_id}")
    except KeyError:
        print(f"Unexpected response format: {res}")
        return

    # 2. Poll Status
    print("Polling status (this may take 2-3 minutes)...")
    for i in range(60): # Wait up to 10 mins
        status_res = send_blender_command('poll_rodin_job_status', {'job_id': job_id})
        
        # Handle potential nested result structure
        if status_res.get('status') == 'success':
            # The actual status string might be deeper depending on the addon's wrapper
            # Let's assume the addon returns the raw Rodin API response in 'result'
            current_status = status_res['result'].get('status', 'unknown')
        else:
            current_status = 'error'
            
        print(f"Status (Attempt {i+1}): {current_status}")
        
        if current_status == 'succeed': # Rodin API often uses 'succeed' or 'completed'
            print("Generation Complete! Importing asset...")
            
            # 3. Import
            import_res = send_blender_command('import_generated_asset', {'job_id': job_id})
            print(f"Import Result: {import_res}")
            
            # 4. Optimize & Render
            print("Optimizing Poly Count and Rendering...")
            optimization_script = r"""
import bpy
import os

# Identify the imported spaceship (active object)
obj = bpy.context.active_object

if obj and obj.type == 'MESH':
    # 1. Decimate (Lower poly count)
    decimate = obj.modifiers.new(name='Decimate', type='DECIMATE')
    decimate.ratio = 0.3  # 70% reduction
    decimate.use_collapse_triangulate = True
    
    # 2. Smooth Surface (No holes, maintain normals)
    obj.data.use_auto_smooth = True
    weighted = obj.modifiers.new(name='WeightedNormal', type='WEIGHTED_NORMAL')
    weighted.keep_sharp = True
    
    bpy.ops.object.shade_smooth()
    
    # 3. Render
    output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/hyper3d_spaceship_final.png')
    bpy.context.scene.render.filepath = output_path
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080
    
    # Ensure Cycles
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128
    
    bpy.ops.render.render(write_still=True)
"""
            exec_res = send_blender_command('execute_code', {'code': optimization_script})
            print(f"Optimization/Render Result: {exec_res}")
            break
            
        elif current_status in ['failed', 'error']:
            print("Job Failed.")
            break
            
        time.sleep(10)

if __name__ == "__main__":
    generate_hyper3d_spaceship()
