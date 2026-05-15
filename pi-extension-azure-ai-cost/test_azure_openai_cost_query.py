import builtins
import json
from types import SimpleNamespace

import pytest

import sys
from pathlib import Path

# Ensure we can import the script module from this directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

import azure_openai_cost_query as mod


def test_reads_config_file_correctly(tmp_path, monkeypatch):
    cfg = tmp_path / "sp.json"
    cfg.write_text(
        json.dumps(
            {
                "tenant": "tenant-123",
                "appId": "client-456",
                "password": "secret-789",
            }
        )
    )

    captured = {}

    class FakeClientSecretCredential:
        def __init__(self, tenant_id, client_id, client_secret):
            captured["tenant_id"] = tenant_id
            captured["client_id"] = client_id
            captured["client_secret"] = client_secret

    monkeypatch.setattr(mod, "ClientSecretCredential", FakeClientSecretCredential)
    monkeypatch.setattr(mod, "DefaultAzureCredential", lambda: (_ for _ in ()).throw(AssertionError("should not be used")))

    cred = mod._credential_from_config(str(cfg))
    assert isinstance(cred, FakeClientSecretCredential)
    assert captured == {
        "tenant_id": "tenant-123",
        "client_id": "client-456",
        "client_secret": "secret-789",
    }


def test_returns_total_from_response_structure(monkeypatch):
    # Verified structure from CostManagement query response:
    # result.columns -> objects with .name
    # result.rows -> list[list[Any]]
    # Use the exact structure observed from a real API call (IDs randomized).
    fake_result = SimpleNamespace(
        columns=[
            SimpleNamespace(name="PreTaxCost", type="Number"),
            SimpleNamespace(name="Currency", type="String"),
        ],
        id="subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.CostManagement/query/11111111-1111-1111-1111-111111111111",
        name="11111111-1111-1111-1111-111111111111",
        rows=[[2.35504815, "USD"]],
        type="Microsoft.CostManagement/query",
    )

    class FakeQueryOps:
        def usage(self, scope, parameters):
            return fake_result

    class FakeCostManagementClient:
        def __init__(self, credential):
            self.query = FakeQueryOps()

    monkeypatch.setattr(mod, "CostManagementClient", FakeCostManagementClient)
    monkeypatch.setattr(mod, "_credential_from_config", lambda _: object())

    cols, rows = mod.query_cost(
        subscription_id="sub",
        resource_id="/subscriptions/sub/resourceGroups/rg/providers/Microsoft.CognitiveServices/accounts/a",
        date_from=mod.date.fromisoformat("2026-05-01"),
        date_to=mod.date.fromisoformat("2026-05-13"),
        config_path="/does/not/matter.json",
    )

    total = mod.extract_total_cost(cols, rows)
    assert total == pytest.approx(2.35504815)


def test_prints_error_on_api_failure(monkeypatch, capsys):
    class FakeQueryOps:
        def usage(self, scope, parameters):
            raise RuntimeError("boom")

    class FakeCostManagementClient:
        def __init__(self, credential):
            self.query = FakeQueryOps()

    monkeypatch.setattr(mod, "CostManagementClient", FakeCostManagementClient)
    monkeypatch.setattr(mod, "_credential_from_config", lambda _: object())

    # Patch parse_args so main() doesn't depend on CLI parsing.
    monkeypatch.setattr(
        mod,
        "parse_args",
        lambda: mod.Args(
            subscription_id="sub",
            resource_group="rg",
            account_name="acct",
            date_from=mod.date.fromisoformat("2026-05-01"),
            date_to=mod.date.fromisoformat("2026-05-13"),
            config="/tmp/sp.json",
        ),
    )

    with pytest.raises(SystemExit):
        mod.main()

    out = capsys.readouterr()
    assert "boom" in out.err
