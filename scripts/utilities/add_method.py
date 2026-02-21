import sys
import os

path = '../untitled folder/yahtzee/yatzee-frontend/extensions/cocos-mcp-server/source/scene.ts'
with open(path, 'r') as f:
    content = f.read()

index = content.rfind('};')
if index != -1:
    new_method = """
    ,
    /**
     * Add component by class name string
     */
    addComponentByName(nodeUuid: string, className: string) {
        try {
            const { director } = require('cc');
            const scene = director.getScene();
            if (!scene) return { success: false, error: 'No active scene' };

            const node = scene.getChildByUuid(nodeUuid);
            if (!node) return { success: false, error: `Node ${nodeUuid} not found` };

            // Direct call as requested by user
            const component = node.addComponent(className);
            return { 
                success: true, 
                message: `Component ${className} added to node ${node.name}`,
                data: { componentUuid: component.uuid }
            };
        } catch (error: any) {
            return { success: false, error: error.message };
        }
    }
"""
    new_content = content[:index] + new_method + content[index:]
    with open(path, 'w') as f:
        f.write(new_content)
    print("Added addComponentByName to scene.ts")
