#!/usr/bin/env python3
"""
MCP server for interacting with GNU screen sessions.

Provides tools to read terminal output and execute commands in screen sessions.
"""

from mcp.server.fastmcp import FastMCP

import screen_lib

mcp = FastMCP("screen")


@mcp.tool()
def get_last_lines(session_name: str, lines: int = 10) -> str:
    """
    Get the last N lines from a screen terminal session.

    Use this to check the current state of the terminal, see command output,
    or verify what's currently displayed on screen.

    Args:
        session_name: Name of the screen session to read from
        lines: Number of lines to return (default: 10)

    Returns:
        The last N non-empty lines from the terminal
    """
    return screen_lib.get_n_last_lines(session_name, lines)


@mcp.tool()
def send_command(
    session_name: str,
    command: str,
    prompt_verify_string: str | None = None
) -> str:
    """
    Send a command to the terminal without executing it.

    Use this for risky commands or when the user asks to only send the
    command. This allows the user to review the command and execute it
    by themselves.

    Args:
        session_name: Name of the screen session
        command: Command text to send (will NOT have newline appended)
        prompt_verify_string: If provided, only send if the current prompt
            contains this string. Useful to ensure the terminal is ready.

    Returns:
        "sent" if command was sent, "prompt_mismatch" if verification failed
    """
    success = screen_lib.send_to_terminal(session_name, command, prompt_verify_string)
    return "sent" if success else "prompt_mismatch"


@mcp.tool()
def execute_command(
    session_name: str,
    command: str,
    timeout: float = 30.0,
    prompt_verify_string: str | None = None
) -> str:
    """
    Execute a command in the terminal and wait for it to complete.

    Use this for commands where you need to see the output before proceeding.
    The function waits until a new prompt appears, indicating the command
    has finished.

    Args:
        session_name: Name of the screen session
        command: Command to execute (newline will be appended automatically)
        timeout: Maximum seconds to wait for completion (default: 30)
        prompt_verify_string: If provided, only execute if the current prompt
            contains this string. Useful to ensure the terminal is ready.

    Returns:
        The command output if successful, "timeout" if the command didn't
        complete within the timeout period, or "prompt_mismatch" if prompt
        verification failed
    """
    try:
        result = screen_lib.execute_in_terminal(
            session_name,
            command,
            prompt_verify_string=prompt_verify_string,
            sync=True,
            timeout=timeout
        )
        return result if result is not None else "timeout"
    except screen_lib.PromptVerificationError:
        return "prompt_mismatch"


@mcp.tool()
def get_last_command_output(session_name: str) -> dict:
    """
    Extract the last command and its output from the terminal.

    Use this to get structured information about what command was run
    and what output it produced.

    Args:
        session_name: Name of the screen session

    Returns:
        Dictionary with 'prompt', 'command', and 'output' keys,
        or {'error': 'no_command_found'} if no command was detected
    """
    content = screen_lib._capture_screen(session_name)
    result = screen_lib.get_last_command(content)
    if result is None:
        return {"error": "no_command_found"}
    return {
        "prompt": result.prompt,
        "command": result.command,
        "output": result.output
    }


if __name__ == "__main__":
    mcp.run()
