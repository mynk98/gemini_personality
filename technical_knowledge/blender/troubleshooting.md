# Blender Troubleshooting

## Common Errors
- **NoneType object has no attribute 'use_nodes'**: Occurs when `bpy.context.scene.world` is None. Fix: Create a new world if missing.
- **name 'os' is not defined**: Always import `os`, `math`, `bpy`, and `bmesh` *inside* the string sent to `execute_code`.
- **Holes in Mesh**: Decimate ratio too low (e.g., 0.1). Use 0.5 or higher for complex organic models.
- **Command Unknown**: Ensure the `addon.py` in `~/Library/Application Support/Blender/4.1/scripts/addons/` matches the latest source.

## Connection Issues
- Ensure Blender is open and "Connect to Claude" is clicked in the Sidebar > BlenderMCP tab.
- Check if port 9876 is listening: `lsof -i :9876`.
