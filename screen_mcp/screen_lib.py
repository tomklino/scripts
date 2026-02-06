#!/usr/bin/env python3

import os
import subprocess
import sys
import tempfile
from typing import NamedTuple

PROMPT_ARROW = '__>'


class CommandOutput(NamedTuple):
    prompt: str
    command: str
    output: str


SCREEN_SETTINGS = [
    'termcapinfo xterm* ti@:te@',
    'defscrollback 250000',
    'defutf8 on',
]

# PS1 prompt with kube_ps1 and the special arrow
SCREEN_PS1 = r"$(kube_ps1)%(?:%{%}%1{__>%} :%{%}%1{>%} ) %{%}%c%{%} "


def create_screen_session(session_name: str) -> bool:
    """
    Create a new attached screen session with predefined settings and PS1.

    Args:
        session_name: Name for the screen session

    Returns:
        True if session was created successfully, False otherwise
    """
    import threading
    import time

    # Create temporary screenrc with settings
    screenrc_content = '\n'.join(SCREEN_SETTINGS)

    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.screenrc', delete=False
    ) as f:
        f.write(screenrc_content)
        tmp_screenrc = f.name

    def stuff_ps1():
        """Wait for session to start, then stuff the PS1 export."""
        time.sleep(0.5)
        ps1_export = f"export PS1='{SCREEN_PS1}'\n"
        subprocess.run(
            ['screen', '-S', session_name, '-X', 'stuff', ps1_export],
            capture_output=True,
            text=True
        )

    try:
        # Start thread to stuff PS1 after session starts
        stuff_thread = threading.Thread(target=stuff_ps1)
        stuff_thread.start()

        # Create attached session (blocks until user exits)
        result = subprocess.run(
            ['screen', '-c', tmp_screenrc, '-S', session_name]
        )

        stuff_thread.join()
        return result.returncode == 0
    finally:
        os.unlink(tmp_screenrc)


def get_last_command(terminal_output: str) -> CommandOutput | None:
    """
    Extract the last command and its output from terminal output.

    Args:
        terminal_output: Raw terminal output string

    Returns:
        CommandOutput with prompt, command, and output, or None if not found
    """
    lines = terminal_output.strip().split('\n')

    # Find all prompt line indices (lines containing the prompt arrow)
    prompt_indices = []
    for i, line in enumerate(lines):
        if PROMPT_ARROW not in line:
            continue
        # Split on the arrow and take everything after it
        parts = line.split(PROMPT_ARROW, 1)
        after_arrow = parts[1] if len(parts) > 1 else ''
        # Extract prompt (directory/git info) and command
        tokens = after_arrow.strip().split()
        if not tokens:
            prompt_indices.append((i, '', ''))
            continue
        # Find where command starts (after dir and optional git:(branch))
        cmd_start = 1
        if len(tokens) > 1 and tokens[1].startswith('git:('):
            cmd_start = 2
        prompt = PROMPT_ARROW + ' ' + ' '.join(tokens[:cmd_start])
        command = ' '.join(tokens[cmd_start:])
        prompt_indices.append((i, prompt, command))

    if not prompt_indices:
        return None

    # If the last prompt has no command, the terminal is idle - use second-to-last
    # If the last prompt has a command, it's still running - use the last one
    last_idx, last_prompt, last_command = prompt_indices[-1]
    if last_command:
        idx, prompt, command = last_idx, last_prompt, last_command
    elif len(prompt_indices) < 2:
        return None
    else:
        idx, prompt, command = prompt_indices[-2]

    # Output is everything from this prompt line to the end
    output_lines = lines[idx:]
    output = '\n'.join(output_lines)

    return CommandOutput(prompt=prompt, command=command, output=output)


def main():
    if len(sys.argv) < 2:
        print("Usage: terminal_parser.py <file> | -", file=sys.stderr)
        sys.exit(1)

    source = sys.argv[1]
    if source == '-':
        terminal_output = sys.stdin.read()
    else:
        with open(source, encoding='utf-8', errors='replace') as f:
            terminal_output = f.read()

    result = get_last_command(terminal_output)
    if result is None:
        print("No command found", file=sys.stderr)
        sys.exit(1)

    print(result.output)


if __name__ == '__main__':
    main()
