## Screen MCP

When interacting with screen sessions:
* "send" a command = use `mcp__screen__send_command` (does NOT wait for
  completion)
* "execute" or "run" a command = use `mcp__screen__execute_command` (waits
  for completion and returns output)

### Prompt Verification

Use `prompt_verify_string` to verify the terminal state before executing
commands:

* **kubectl context**: The prompt includes the current kubectl context.
  Before running kubectl commands, use `prompt_verify_string` with the
  expected context name (e.g., `"prod10"`) to ensure you're targeting
  the correct cluster
* **Safety first**: When executing `kubectl`, `helm` or any other
  command using a kubernetes context, make sure to use the
  `prompt_verify_string` with the expected context. If the user did not
  provide a context, remind them.
* If verification fails, the tool returns `"prompt_mismatch"` instead
  of executing
