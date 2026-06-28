import json

from fastapi.testclient import TestClient

from app.main import app
import app.main as main_module
import app.root_governance as governance_module


client = TestClient(app)


def test_save_standard_roots_adds_metadata_and_history(tmp_path, monkeypatch):
    standard_file = tmp_path / "standard_roots.json"
    monkeypatch.setattr(governance_module, "STANDARD_ROOTS_FILE", str(standard_file))

    governance_module.save_standard_roots([
        {
            "business_domain": "订单",
            "domain_code": "ord",
            "chinese_name": "订单号",
            "full_root": "order_no",
            "abbr_root": "ord_no",
            "recommended_type": "VARCHAR(64)",
        }
    ])

    saved = governance_module.load_standard_roots()
    assert len(saved) == 1
    root = saved[0]
    assert root["root_id"]
    assert root["usage_count"] == 1
    assert root["created_at"]
    assert root["updated_at"]
    assert len(root["change_history"]) == 1
    assert root["change_history"][0]["action"] == "created"


def test_update_standard_root_appends_change_history(tmp_path, monkeypatch):
    standard_file = tmp_path / "standard_roots.json"
    monkeypatch.setattr(governance_module, "STANDARD_ROOTS_FILE", str(standard_file))
    monkeypatch.setattr(main_module, "load_standard_roots", governance_module.load_standard_roots)
    monkeypatch.setattr(main_module, "save_standard_roots", governance_module.save_standard_roots)
    monkeypatch.setattr(main_module, "normalize_standard_root_record", governance_module.normalize_standard_root_record)

    governance_module.save_standard_roots([
        {
            "business_domain": "订单",
            "domain_code": "ord",
            "chinese_name": "订单号",
            "full_root": "order_no",
            "abbr_root": "ord_no",
            "recommended_type": "VARCHAR(64)",
        }
    ])
    current = governance_module.load_standard_roots()[0]

    response = client.put(
        f"/api/standard-roots/{current['root_id']}",
        json={
            "business_domain": "订单",
            "domain_code": "ord",
            "chinese_name": "订单号",
            "full_root": "order_number",
            "abbr_root": "ord_no",
            "recommended_type": "VARCHAR(64)",
            "usage_count": 3,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    updated = body["data"]
    assert updated["usage_count"] == 3
    assert updated["full_root"] == "order_number"
    assert len(updated["change_history"]) == 2
    assert updated["change_history"][-1]["action"] == "edited"
    assert updated["change_history"][-1]["before"]["full_root"] == "order_no"
    assert updated["change_history"][-1]["after"]["full_root"] == "order_number"
