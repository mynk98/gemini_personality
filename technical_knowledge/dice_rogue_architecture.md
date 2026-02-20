# Dice Rogue: Multi-Scene Architecture

## Overview
Dice Rogue is transitioning from a single-scene structure to a managed multi-scene framework to improve modularity and user experience.

## Scene Structure
- **LobbyScene.scene**: The game's entry point. Handles user profile display (Gems, Progress) and game initialization.
- **GameScene.scene**: The primary gameplay environment.
- **LoadingScene**: A persistent utility scene used to mask transitions.

## Key Cocos Creator Patterns
### Persistent Nodes
Use `cc.game.addPersistRootNode(node)` for the `LoadingCanvas`. This ensures the loading screen remains in memory and visible while the background scenes are swapped.

### Scene Transition Workflow
1.  **Trigger**: User clicks "Play" or game logic initiates a level load.
2.  **Mask**: Enable the `PersistentCanvas/Loading` UI.
3.  **Load**: Call `cc.director.loadScene('TargetScene')`.
4.  **Unmask**: Disable the loading UI once the new scene's `onLoad` or `start` sequence confirms readiness.

### Lobby Logic (Integration with UserData)
- **Currency**: Gem counts are pulled from the `UserData` singleton/manager.
- **Progression**: Current World and Level indices are used to determine whether the "Play" button resumes a saved session or starts a fresh run.

## Architectural Goal
The `GameManager` should serve as the central orchestrator for these transitions, ensuring that persistent nodes are initialized exactly once at startup.
