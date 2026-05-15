# pi-extension-azure-ai-cost

Shows the last-7-days Azure OpenAI (Cognitive Services) cost in the pi status bar.

## Requirements

- Python 3
- `azure-identity`, `azure-mgmt-costmanagement`
- Service principal config at `~/.azure/sp/sp-aoai-cost-query.json` (created earlier)
- `AZURE_SUBSCRIPTION_ID` set in the environment where `pi` runs

Optional env vars (defaults match your test resource):
- `AZURE_AOAI_RESOURCE_GROUP` (default: `rg-pi-openai-test`)
- `AZURE_AOAI_ACCOUNT_NAME` (default: `pi-openai-test-1`)

## Install globally

Create a symlink into pi’s global extensions folder:

```bash
mkdir -p ~/.pi/agent/extensions/azure-ai-cost
ln -sf ~/workspace/scripts/pi-extension-azure-ai-cost/index.ts ~/.pi/agent/extensions/azure-ai-cost/index.ts
ln -sf ~/workspace/scripts/pi-extension-azure-ai-cost/azure_openai_cost_query.py ~/.pi/agent/extensions/azure-ai-cost/azure_openai_cost_query.py
```

Then in pi:
- run `/reload`

## Manual refresh

In pi, run:
- `/update-azure-cost`

## Refresh interval

- Runs at session start and then every 15 minutes.
