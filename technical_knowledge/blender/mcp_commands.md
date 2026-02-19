# Blender MCP Commands

I can communicate with Blender using a JSON-RPC style protocol over a TCP socket on port 9876.

## Basic Structure
Commands are sent as JSON:
```json
{
  "type": "command_name",
  "params": { ... }
}
```

## Available Commands (from latest addon.py)
- `execute_code`: Runs arbitrary Python code within Blender's context.
- `get_scene_info`: Returns details about objects, cameras, and lights.
- `get_viewport_screenshot`: Captures current view.
- `create_rodin_job`: (Hyper3D) Generates models from text prompts.
- `poll_rodin_job_status`: Checks progress of generation.
- `import_generated_asset`: Imports GLB/OBJ results from generation tasks.
- `get_polyhaven_status`: Checks if PolyHaven integration is active.
- `search_polyhaven_assets`: Filters assets by type and category.
- `download_polyhaven_asset`: Downloads and imports HDRI, texture, or model.
