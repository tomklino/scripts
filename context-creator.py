#!/usr/bin/env python3
import os
import sys
import stat
from typing import Any, Dict, List

try:
    import yaml
except Exception as exc:  # pragma: no cover
    print("Error: PyYAML is required (pip install pyyaml)", file=sys.stderr)
    raise


def read_yaml_file(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Source kubeconfig not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def list_to_name_map(items: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    result: Dict[str, Dict[str, Any]] = {}
    for item in items or []:
        name = item.get("name")
        if name:
            result[name] = item
    return result


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_secure_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)


def sanitize_filename(name: str) -> str:
    # Replace path separators and unsafe characters
    sanitized = name.replace(os.sep, "_")
    for ch in ("\0", "\n", "\r"):
        sanitized = sanitized.replace(ch, "_")
    return sanitized


def build_single_context_kubeconfig(
    source: Dict[str, Any], context_entry: Dict[str, Any]
) -> Dict[str, Any]:
    context_name = context_entry.get("name")
    if not context_name:
        raise ValueError("Context entry missing name")

    ctx = context_entry.get("context", {})
    cluster_name = ctx.get("cluster")
    user_name = ctx.get("user")

    clusters_map = list_to_name_map(source.get("clusters", []))
    users_map = list_to_name_map(source.get("users", []))

    cluster_entry = clusters_map.get(cluster_name)
    user_entry = users_map.get(user_name)

    if cluster_name and not cluster_entry:
        raise ValueError(f"Cluster '{cluster_name}' for context '{context_name}' not found")
    if user_name and not user_entry:
        raise ValueError(f"User '{user_name}' for context '{context_name}' not found")

    result: Dict[str, Any] = {
        "apiVersion": source.get("apiVersion", "v1"),
        "kind": source.get("kind", "Config"),
        # Preserve minimal preferences if present
        "preferences": source.get("preferences", {}),
        "current-context": context_name,
        "clusters": [cluster_entry] if cluster_entry else [],
        "users": [user_entry] if user_entry else [],
        "contexts": [
            {
                "name": context_name,
                "context": {
                    **({"cluster": cluster_name} if cluster_name else {}),
                    **({"user": user_name} if user_name else {}),
                    **({"namespace": ctx["namespace"]} if "namespace" in ctx else {}),
                },
            }
        ],
    }
    return result


def main() -> int:
    source_path = "/tmp/origin"
    output_dir = os.path.expanduser("~/.kubeconfigs")

    try:
        source_cfg = read_yaml_file(source_path)
    except Exception as exc:
        print(f"Failed to read source kubeconfig: {exc}", file=sys.stderr)
        return 1

    contexts = source_cfg.get("contexts", [])
    if not contexts:
        print("No contexts found in source kubeconfig", file=sys.stderr)
        return 1

    ensure_dir(output_dir)

    errors: List[str] = []
    for context_entry in contexts:
        name = context_entry.get("name") or "unnamed"
        try:
            cfg = build_single_context_kubeconfig(source_cfg, context_entry)
            content = yaml.safe_dump(cfg, default_flow_style=False, sort_keys=False)
            filename = sanitize_filename(name)
            target_path = os.path.join(output_dir, filename)
            write_secure_file(target_path, content)
            print(f"Wrote {target_path}")
        except Exception as exc:  # Keep going, collect errors
            errors.append(f"{name}: {exc}")

    if errors:
        print("Some contexts failed:", file=sys.stderr)
        for e in errors:
            print(f" - {e}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())


