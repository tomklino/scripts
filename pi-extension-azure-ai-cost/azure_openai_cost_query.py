#!/usr/bin/env python3
"""Query Azure Cost Management for spend attributable to a specific Azure OpenAI
(Cognitive Services OpenAI kind) resource.

Notes
-----
- Cost Management data is not real-time (often hours to 1-2 days delayed).
- Azure Cost Management typically cannot break down cost by Azure OpenAI *deployment*
  name. This script outputs the total cost for an Azure OpenAI *resource*.

Usage
-----
1) Ensure you're authenticated (one of):
   - az login (for local dev)
   - managed identity / workload identity in CI

2) Install deps:
   pip install azure-identity azure-mgmt-costmanagement

3) Run:
   python azure_openai_cost_query.py \
     --subscription-id <sub> \
     --resource-group rg-pi-openai-test \
     --account-name pi-openai-test-1 \
     --from 2026-05-01 --to 2026-05-13

Environment variables
---------------------
- AZURE_SUBSCRIPTION_ID can be used instead of --subscription-id

Service principal config
------------------------
If --config points at a JSON file produced by:
  az ad sp create-for-rbac --output json > file.json
this script will read tenant/appId/password from it and authenticate using a
ClientSecretCredential (no need to export env vars).
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.mgmt.costmanagement import CostManagementClient


@dataclass(frozen=True)
class Args:
    subscription_id: str
    resource_group: str
    account_name: str
    date_from: date
    date_to: date
    config: str


def parse_args() -> Args:
    p = argparse.ArgumentParser(description="Query cost for an Azure OpenAI resource via Azure Cost Management")
    p.add_argument("--subscription-id", default=os.getenv("AZURE_SUBSCRIPTION_ID"), help="Azure subscription id")
    p.add_argument(
        "--config",
        default=os.path.expanduser("~/.azure/sp/sp-aoai-cost-query.json"),
        help="Path to service principal JSON config (default: ~/.azure/sp/sp-aoai-cost-query.json)",
    )
    p.add_argument("--resource-group", required=True, help="Resource group containing the AOAI account")
    p.add_argument("--account-name", required=True, help="Cognitive Services account name (Azure OpenAI resource)")
    p.add_argument("--from", dest="date_from", required=True, help="Start date (YYYY-MM-DD)")
    p.add_argument("--to", dest="date_to", required=True, help="End date (YYYY-MM-DD), inclusive-ish per API")
    # This script is total-only, so granularity is fixed to None.

    ns = p.parse_args()
    if not ns.subscription_id:
        raise SystemExit("Missing subscription id. Provide --subscription-id or set AZURE_SUBSCRIPTION_ID")

    return Args(
        subscription_id=ns.subscription_id,
        resource_group=ns.resource_group,
        account_name=ns.account_name,
        date_from=date.fromisoformat(ns.date_from),
        date_to=date.fromisoformat(ns.date_to),
        config=ns.config,
    )


def aoai_resource_id(subscription_id: str, resource_group: str, account_name: str) -> str:
    return (
        f"/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group}"
        f"/providers/Microsoft.CognitiveServices/accounts/{account_name}"
    )


def _credential_from_config(config_path: str):
    """Return an Azure credential.

    Preference order:
    1) If config JSON exists and contains tenant/appId/password, use ClientSecretCredential.
    2) Otherwise fall back to DefaultAzureCredential.
    """

    p = Path(config_path).expanduser()
    if p.exists():
        data = json.loads(p.read_text())
        tenant = data.get("tenant")
        client_id = data.get("appId") or data.get("clientId")
        secret = data.get("password") or data.get("clientSecret")
        if tenant and client_id and secret:
            return ClientSecretCredential(tenant_id=tenant, client_id=client_id, client_secret=secret)

    return DefaultAzureCredential()


def query_cost(
    *,
    subscription_id: str,
    resource_id: str,
    date_from: date,
    date_to: date,
    config_path: str = os.path.expanduser("~/.azure/sp/sp-aoai-cost-query.json"),
) -> tuple[list[str], list[list[Any]]]:
    credential = _credential_from_config(config_path)
    client = CostManagementClient(credential)

    scope = f"/subscriptions/{subscription_id}"

    # The CostManagement QueryDefinition model expects full ISO-8601 datetimes.
    # Use date boundaries in UTC.
    parameters: dict[str, Any] = {
        "type": "ActualCost",
        "timeframe": "Custom",
        "timePeriod": {
            "from": f"{date_from.isoformat()}T00:00:00Z",
            "to": f"{date_to.isoformat()}T23:59:59Z",
        },
        "dataset": {
            "granularity": "None",
            "aggregation": {"cost": {"name": "PreTaxCost", "function": "Sum"}},
            # No grouping: return a single total row for the period.
            "filter": {
                "dimensions": {
                    "name": "ResourceId",
                    "operator": "In",
                    "values": [resource_id],
                }
            },
        },
    }

    result = client.query.usage(scope=scope, parameters=parameters)

    columns = [c.name for c in result.columns]
    rows = list(result.rows or [])
    return columns, rows


def extract_total_cost(columns: list[str], rows: list[list[Any]]) -> float:
    """Extract summed cost from CostManagement query response."""
    if not rows:
        return 0.0

    # Aggregation name is "cost"; the column can be "PreTaxCost" in some shapes,
    # but typically comes back as "Cost" or the aggregation name.
    preferred_names = ["cost", "Cost", "PreTaxCost"]
    col_idx = None
    for name in preferred_names:
        if name in columns:
            col_idx = columns.index(name)
            break
    if col_idx is None:
        # Fallback: find first numeric-looking column
        for i, c in enumerate(columns):
            if c.lower().endswith("cost"):
                col_idx = i
                break
    if col_idx is None:
        raise RuntimeError(f"Couldn't locate cost column. Columns: {columns}")

    # With no grouping + granularity None, expect a single row.
    # But just in case, sum all rows.
    total = 0.0
    for r in rows:
        try:
            total += float(r[col_idx])
        except Exception:
            pass
    return total


def main() -> None:
    args = parse_args()
    rid = aoai_resource_id(args.subscription_id, args.resource_group, args.account_name)

    try:
        cols, rows = query_cost(
            subscription_id=args.subscription_id,
            resource_id=rid,
            date_from=args.date_from,
            date_to=args.date_to,
            config_path=args.config,
        )
        total = extract_total_cost(cols, rows)
        print(total)
    except Exception as e:
        # Print error to stderr and exit non-zero
        import sys

        print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()

