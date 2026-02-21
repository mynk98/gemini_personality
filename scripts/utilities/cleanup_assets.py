import json
import os

def cleanup_asset(path):
    with open(path, 'r') as f:
        data = json.load(f)
    
    # Remove nodes or components that were manually injected and are now invalid
    # We will identify them by the UUIDs we know we added or by the 'cc.MissingScript' type
    new_data = [item for item in data if item.get("__type__") != "cc.MissingScript" and item.get("__type__") not in ["fa580330-20ab-46ce-914b-ab4ec467b254", "d46d0995-1d4d-4b9c-973b-d86ce6af9cfd", "e2d4fd7a-6c5a-4c7e-83cf-142378acd8f6", "5696342c-75bb-4993-9a1d-6962773ba701", "56b1ac0d-0cb4-4290-bd77-7972732553da"]]
    
    # Also need to clean up the _components arrays in the nodes
    for item in new_data:
        if item.get("__type__") == "cc.Node":
            if "_components" in item:
                # Filter out references to indices that no longer exist or were components we removed
                # This is tricky because indices shift. 
                # Better approach: just reload the original scene if possible, or surgically remove.
                pass

    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# Reverting to last known good state via git is safest if we broke the JSON structure
