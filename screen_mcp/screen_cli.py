#!/usr/bin/env python3

import argparse
import inspect
import sys

import screen_lib


TESTABLE_FUNCTIONS = [
    'capture_screen',
    'get_n_last_lines',
    'send_to_terminal',
    'execute_in_terminal',
    'get_last_command',
]


def cmd_new(args):
    """Create a new screen session."""
    if screen_lib.create_screen_session(args.session_name):
        print(f"Created screen session: {args.session_name}")
    else:
        print(f"Failed to create screen session: {args.session_name}",
              file=sys.stderr)
        sys.exit(1)


def cmd_test(args):
    """Test a screen_lib function."""
    func_name = args.function
    if func_name not in TESTABLE_FUNCTIONS:
        print(f"Unknown function: {func_name}", file=sys.stderr)
        print(f"Available functions: {', '.join(TESTABLE_FUNCTIONS)}",
              file=sys.stderr)
        sys.exit(1)

    func = getattr(screen_lib, func_name)
    sig = inspect.signature(func)
    params = list(sig.parameters.keys())

    # Parse arguments based on function signature
    func_args = args.args
    kwargs = {}

    for i, param_name in enumerate(params):
        param = sig.parameters[param_name]
        if i < len(func_args):
            value = func_args[i]
            # Type conversion based on annotation
            if param.annotation == int:
                value = int(value)
            elif param.annotation == float:
                value = float(value)
            elif param.annotation == bool:
                value = value.lower() in ('true', '1', 'yes')
            kwargs[param_name] = value
        elif param.default is not inspect.Parameter.empty:
            continue  # Use default
        else:
            print(f"Missing required argument: {param_name}", file=sys.stderr)
            sys.exit(1)

    result = func(**kwargs)
    if result is not None:
        print(result)


def main():
    parser = argparse.ArgumentParser(
        description='Screen session management CLI'
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # new subcommand
    new_parser = subparsers.add_parser(
        'new',
        help='Create a new screen session'
    )
    new_parser.add_argument(
        'session_name',
        help='Name for the screen session'
    )
    new_parser.set_defaults(func=cmd_new)

    # test subcommand
    test_parser = subparsers.add_parser(
        'test',
        help='Test a screen_lib function'
    )
    test_parser.add_argument(
        'function',
        help=f'Function to test: {", ".join(TESTABLE_FUNCTIONS)}'
    )
    test_parser.add_argument(
        'args',
        nargs='*',
        help='Arguments to pass to the function'
    )
    test_parser.set_defaults(func=cmd_test)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
