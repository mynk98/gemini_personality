# Antigravity Task Delegation Notes

## Observations
- **CLI Path:** `/Users/abhisheksonkar/.antigravity/antigravity/bin/antigravity`
- **Attempted Command:** `antigravity chat "prompt" "workspace_path"`
- **Result:** Command executed successfully in the shell but the prompt did not appear in the Antigravity IDE UI.
- **Protocol:** Antigravity uses a Protobuf-based language server and provides a Chrome DevTools MCP on a dynamic port (discovered via logs).

## Known Issues
- Direct task delegation via CLI `chat` subcommand does not seem to reliably bridge to the active UI instance for autonomous execution or even for user visibility.
- Automation via the dynamic MCP port (e.g., 52707) is restricted to browser/devtools-like tools and does not appear to expose the main AI agent for general reasoning tasks.

## Recommendation
Avoid using the `antigravity` CLI for background task delegation until a more robust, bidirectional API or fixed-port MCP server is identified.
