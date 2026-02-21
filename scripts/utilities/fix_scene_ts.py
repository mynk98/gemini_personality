import sys
import os

path = '../untitled folder/yahtzee/yatzee-frontend/extensions/cocos-mcp-server/source/scene.ts'
if not os.path.exists(path):
    print(f"File not found: {path}")
    sys.exit(1)

with open(path, 'r') as f:
    content = f.read()

# Remove any previous broken injections of attachScript
# We look for the last occurrence of setComponentProperty's final brace
search_str = "return { success: false, error: error.message };"
last_error_msg = content.rfind(search_str)

if last_error_msg == -1:
    print("Could not find standard method structure")
    sys.exit(1)

# Find the brace that closes that method
# It should be after the error message's block
method_end = content.find("}", last_error_msg)
method_end = content.find("}", method_end + 1) # Close the catch
method_end = content.find("}", method_end + 1) # Close the method

if method_end == -1:
    print("Could not find method end brace")
    sys.exit(1)

base_content = content[:method_end + 1]

new_content = base_content + """
    ,
    /**
     * Attach a script to a node
     */
    async attachScript(nodeUuid: string, scriptPath: string) {
        try {
            const { director } = require('cc');
            const scene = director.getScene();
            if (!scene) {
                return { success: false, error: 'No active scene' };
            }

            const node = scene.getChildByUuid(nodeUuid);
            if (!node) {
                return { success: false, error: `Node with UUID ${nodeUuid} not found` };
            }

            // Get script asset info
            const assetInfo = await Editor.Message.request('asset-db', 'query-asset-info', scriptPath);
            if (!assetInfo) {
                return { success: false, error: `Script asset not found at path: ${scriptPath}` };
            }

            const scriptUuid = assetInfo.uuid;
            
            // Add component using script UUID
            const component = node.addComponent(scriptUuid);
            
            return { 
                success: true, 
                message: `Script at ${scriptPath} attached successfully`,
                data: { componentId: component.uuid, scriptUuid: scriptUuid }
            };
        } catch (error: any) {
            return { success: false, error: error.message };
        }
    }
};"""

with open(path, 'w') as f:
    f.write(new_content)
print("Successfully reconstructed scene.ts")
