## Screen MCP

When interacting with screen sessions:
* "send" a command = use `mcp__screen__send_command` (does NOT wait for
  completion)
* "execute" or "run" a command = use `mcp__screen__execute_command` (waits
  for completion and returns output)
