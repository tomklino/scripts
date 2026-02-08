#!/usr/bin/env python3

import os
import re
import subprocess
import sys
import tempfile
import time
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


def capture_screen(session_name: str, timeout: float = 2.0) -> str:
    """
    Capture the current screen content using hardcopy.

    Args:
        session_name: Name of the screen session
        timeout: Max time to wait for hardcopy file (seconds)

    Returns:
        The captured screen content as a string
    """
    tmp_file = f"/tmp/screen_hardcopy_{os.getpid()}.txt"

    if os.path.exists(tmp_file):
        os.unlink(tmp_file)

    try:
        subprocess.run(
            ['screen', '-S', session_name, '-X', 'hardcopy', '-h', tmp_file],
            capture_output=True,
            text=True
        )

        # Wait for file size to stabilize
        start = time.time()
        last_size = -1
        while time.time() - start < timeout:
            if os.path.exists(tmp_file):
                current_size = os.path.getsize(tmp_file)
                if current_size > 0 and current_size == last_size:
                    break
                last_size = current_size
            time.sleep(0.05)

        with open(tmp_file, encoding='utf-8', errors='replace') as f:
            raw = f.read()

        # Strip null bytes
        return raw #.replace("\x00", "")
    finally:
        blah = 1
        # if os.path.exists(tmp_file):
        #     os.unlink(tmp_file)


def get_n_last_lines(session_name: str, lines: int = 10) -> str:
    """
    Get the last N lines from the terminal.

    Args:
        session_name: Name of the screen session
        lines: Number of lines to return (default: 10)

    Returns:
        The last N lines as a string
    """
    content = capture_screen(session_name)
    content_lines = content.split('\n')

    # Strip control characters from each line
    cleaned_lines = []
    for line in content_lines:
        cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', line)
        cleaned_lines.append(cleaned)

    # Find first and last non-empty lines to trim padding
    first_content = 0
    for i, line in enumerate(cleaned_lines):
        if line.strip():
            first_content = i
            break

    last_content = len(cleaned_lines) - 1
    for i in range(len(cleaned_lines) - 1, -1, -1):
        if cleaned_lines[i].strip():
            last_content = i
            break

    # Get content between first and last non-empty lines (inclusive)
    trimmed = cleaned_lines[first_content:last_content + 1]

    return '\n'.join(trimmed[-lines:])


def send_to_terminal(
    session_name: str,
    command: str,
    prompt_verify_string: str | None = None
) -> bool:
    """
    Send a command to the terminal without waiting for completion.

    Args:
        session_name: Name of the screen session
        command: Command to send
        prompt_verify_string: If provided, only send if prompt contains this

    Returns:
        True if command was sent, False if prompt verification failed
    """
    if prompt_verify_string is not None:
        content = capture_screen(session_name)
        lines = content.rstrip('\n').split('\n')
        # Check the last non-empty line for prompt
        last_line = ''
        for line in reversed(lines):
            if line.strip():
                last_line = line
                break
        if prompt_verify_string not in last_line:
            return False

    subprocess.run(
        ['screen', '-S', session_name, '-X', 'stuff', f'{command}'],
        capture_output=True,
        text=True
    )
    return True


def execute_in_terminal(
    session_name: str,
    command: str,
    prompt_verify_string: str | None = None,
    sync: bool = True,
    timeout: float = 30.0,
    poll_interval: float = 0.001
) -> str | None:
    """
    Execute a command in the terminal.

    Args:
        session_name: Name of the screen session
        command: Command to execute
        prompt_verify_string: If provided, only execute if prompt contains this
        sync: If True, wait for command to finish and return output
        timeout: Maximum time to wait for command completion (seconds)
        poll_interval: How often to check for completion (seconds)

    Returns:
        If sync=True: Full output including prompts, or None if verification
            failed or timeout
        If sync=False: Empty string on success, None if verification failed
    """
    subprocess.run(
        ['screen', '-S', session_name, '-X', 'stuff', f'{command}\n'],
        capture_output=True,
        text=True
    )
    if not sync:
        return ''

    # Wait for command to complete by watching for a new prompt
    start_time = time.time()
    while time.time() - start_time < timeout:
        time.sleep(poll_interval)
        content = capture_screen(session_name)
        result = get_last_command(content)
        if result is None:
            continue
        # Check if command finished (new prompt appeared with no command)
        lines = content.rstrip('\n').split('\n')
        for line in reversed(lines):
            if not line.strip():
                continue
            # If last non-empty line has prompt arrow but no command after it,
            # the command has completed
            if PROMPT_ARROW in line:
                parts = line.split(PROMPT_ARROW, 1)
                after_arrow = parts[1].strip() if len(parts) > 1 else ''
                tokens = after_arrow.split()
                # Skip directory and optional git info
                cmd_start = 1
                if len(tokens) > 1 and tokens[1].startswith('git:('):
                    cmd_start = 2
                remaining = tokens[cmd_start:] if len(tokens) > cmd_start else []
                if not remaining:
                    # Command finished, return output
                    return result.output
            break

    return None  # Timeout


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
