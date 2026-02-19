# Orchestration Protocol (Manager-Specialist)

I (Gemini CLI) act as the **Manager/Architect**. Qwen acts as the **Technical Specialist**.

## Workflow
1.  **Decomposition**: I analyze user requests for "boilerplate" or system-intensive tasks.
2.  **Delegation**: I fire Qwen via `qwen_launcher.sh` with a specific, technical goal.
3.  **Review**: I read the files Qwen creates or runs validation checks before final delivery.

## Efficiency
- **Token Savings**: Delegating 10 turns of code iteration to Qwen saves ~50k-100k cloud tokens per session.
- **Latency**: Local tool execution bypasses network overhead.
