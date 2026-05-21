#!/usr/bin/env python3
"""Convert a JSON log line (stdin or file arg) to YAML, using >- for strings
containing embedded newlines."""

import json
import sys

import yaml


class Folded(str):
    pass


def _folded_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=">")


yaml.add_representer(Folded, _folded_representer)


def _wrap(obj):
    if isinstance(obj, dict):
        return {k: _wrap(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_wrap(v) for v in obj]
    if isinstance(obj, str) and "\n" in obj:
        return Folded(obj.rstrip("\n"))
    return obj


def main():
    src = open(sys.argv[1]) if len(sys.argv) > 1 else sys.stdin
    data = json.load(src)
    sys.stdout.write(
        yaml.dump(
            _wrap(data),
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            width=10_000,
        )
    )


if __name__ == "__main__":
    main()
