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
            s.settimeout(300.0) # Maximum time for Hyper3D generation + render
            data = b''
            while True:
                try:
                    chunk = s.recv(16384)
                    if not chunk: break
                    data += chunk
                    if data.strip().endswith(b'}'): break 
                except socket.timeout:
                    return {"status": "timeout"}
            return json.loads(data.decode('utf-8'))
    except Exception as e: return {"status": "error", "message": str(e)}

def generate_ultimate_hyper3d():
    print("--- Initiating Ultimate Hyper3D (Rodin) Starship Generation ---")
    
    # 1. Create Job
    prompt = "high-detail realistic industrial sci-fi starship, cinematic lighting, greebles, 8k textures"
    res = send_blender_command('create_rodin_job', {'text_prompt': prompt, 'images': []})
    
    if res.get('status') != 'success':
        print(f"Failed to create job: {res}")
        return
    
    # Extract Potential IDs
    root_uuid = res['result'].get('uuid')
    child_uuid = None
    try: child_uuid = res['result']['jobs']['uuids'][0]
    except: pass
    
    print(f"Job Created. Root UUID: {root_uuid}, Child UUID: {child_uuid}")
    
    # 2. Polling Loop
    job_id = child_uuid if child_uuid else root_uuid
    print(f"Starting Poll on ID: {job_id}")
    
    for i in range(60): # 10 minutes total
        status_res = send_blender_command('poll_rodin_job_status', {'job_id': job_id})
        current_status = status_res.get('result', {}).get('status', 'unknown')
        
        # Fallback if first ID fails
        if current_status in ['error', 'failed', 'unknown'] and root_uuid and job_id != root_uuid:
            print(f"Poll failed for {job_id}, falling back to Root UUID: {root_uuid}")
            job_id = root_uuid
            continue
            
        print(f"Status (Attempt {i+1}): {current_status}")
        
        if current_status == 'succeed':
            print("Generation Succeeded! Importing...")
            send_blender_command('import_generated_asset', {'job_id': job_id})
            
            # 3. Optimize & Render
            print("Applying Low-Poly Optimization and Rendering...")
            opt_script = r"""
import bpy
import os

obj = bpy.context.active_object
if obj and obj.type == 'MESH':
    # 1. Low-Poly Reduction (Decimate)
    dec = obj.modifiers.new(name='DecimateLowPoly', type='DECIMATE')
    dec.ratio = 0.25 # Substantial reduction
    dec.use_collapse_triangulate = True
    
    # 2. Smooth & Intact Surface (Weighted Normal)
    obj.data.use_auto_smooth = True
    wn = obj.modifiers.new(name='WeightedNormalSmooth', type='WEIGHTED_NORMAL')
    wn.keep_sharp = True
    
    bpy.ops.object.shade_smooth()
    
    # 3. Final Cinematic Render
    output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/hyper3d_ultimate_starship.png')
    bpy.context.scene.render.filepath = output_path
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 256
    bpy.ops.render.render(write_still=True)
"""
            send_blender_command('execute_code', {'code': opt_script})
            print("Final Optimized Render Complete!")
            break
        elif current_status in ['failed', 'error']:
            print("Job failed persistently.")
            break
            
        time.sleep(15)

if __name__ == "__main__":
    generate_ultimate_hyper3d()
