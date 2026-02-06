#!/usr/bin/env python3

import argparse
import sys

from screen_lib import create_screen_session


def main():
    parser = argparse.ArgumentParser(
        description='Create a screen session with predefined settings'
    )
    parser.add_argument(
        'session_name',
        help='Name for the screen session'
    )
    args = parser.parse_args()

    if create_screen_session(args.session_name):
        print(f"Created screen session: {args.session_name}")
    else:
        print(f"Failed to create screen session: {args.session_name}",
              file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
