#!/usr/bin/env python3
import json
import os
import sys
import urllib.request
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Update pi-agent models from litellm")
    parser.add_argument(
        "--url", default=os.environ.get("LITELLM_URL"), help="Litellm API URL"
    )
    parser.add_argument(
        "--api-key", default=os.environ.get("LITELLM_API_KEY"), help="Litellm API key"
    )
    parser.add_argument(
        "--models-file",
        default=os.environ.get(
            "MODELS_FILE", os.path.expanduser("~/.pi/agent/models.json")
        ),
        help="Pi agent models.json path",
    )
    return parser.parse_args()


def fetch_models(url, api_key):
    req = urllib.request.Request(
        f"{url}/v1/models",
        headers={"accept": "application/json", "x-litellm-api-key": api_key},
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())


def main():
    args = parse_args()

    if not args.url:
        print("Error: --url or LITELLM_URL required", file=sys.stderr)
        sys.exit(1)
    if not args.api_key:
        print("Error: --api-key or LITELLM_API_KEY required", file=sys.stderr)
        sys.exit(1)

    data = fetch_models(args.url, args.api_key)
    models = data.get("data", [])

    pi_models = [{"id": m["id"]} for m in models]

    if os.path.exists(args.models_file):
        with open(args.models_file, "r") as f:
            config = json.load(f)
    else:
        config = {"providers": {}}

    if "providers" not in config:
        config["providers"] = {}
    if "litellm" not in config["providers"]:
        config["providers"]["litellm"] = {}

    litellm = config["providers"]["litellm"]
    url = (
        litellm.get("baseUrl", "").rstrip("/").replace("/v1", "")
        if litellm.get("baseUrl")
        else args.url.rstrip("/")
    )
    api_key = litellm.get("apiKey", "") or args.api_key
    api = litellm.get("api", "openai-completions")

    config["providers"]["litellm"] = {
        "baseUrl": url,
        "apiKey": api_key,
        "api": api,
        "models": pi_models,
    }

    with open(args.models_file, "w") as f:
        json.dump(config, f, indent="\t")

    print(f"Updated {args.models_file} with {len(pi_models)} models")


if __name__ == "__main__":
    main()
