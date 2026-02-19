# Blender Python Scripting for AI

When using `execute_code`, use these patterns for best results:

## Core Patterns
- **Cleanup**: Always clear existing objects if starting a fresh scene.
  ```python
  import bpy
  bpy.ops.object.select_all(action='SELECT')
  bpy.ops.object.delete()
  ```
- **Render Setup**: Cycles is preferred for realism.
  ```python
  bpy.context.scene.render.engine = 'CYCLES'
  bpy.context.scene.cycles.samples = 512
  ```
- **Robust Pathing**: Use `os.path.expanduser` for saving renders.
  ```python
  import os
  output_path = os.path.expanduser('~/Project/path/to/save.png')
  bpy.context.scene.render.filepath = output_path
  ```

## Modeling Tips
- Use `bmesh` for direct vertex/face manipulation.
- Apply `Mirror` and `Subsurface` modifiers for symmetrical, organic shapes.
- Use `Decimate` (Ratio ~0.5) for optimization, followed by `Smooth`.
