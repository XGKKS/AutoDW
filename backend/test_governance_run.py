import json
from http.client import RemoteDisconnected
import re

import requests
from fastapi.testclient import TestClient

from app.main import app
import app.main as main_module


client = TestClient(app)


def _mock_historical_roots():
    return [
        {
            "business_domain": "订单",
            "domain_code": "ord",
            "chinese_name": "订单号",
            "full_root": "order_no",
            "abbr_root": "ord_no",
            "recommended_type": "VARCHAR(64)",
        },
        {
            "business_domain": "订单",
            "domain_code": "ord",
            "chinese_name": "订单编号",
            "full_root": "order_code",
            "abbr_root": "ord_cd",
            "recommended_type": "VARCHAR(64)",
        },
    ]


def _request_body():
    return {
        "llm_config": {
            "api_key": "test-key",
            "api_url": "https://example.com/v1",
            "model": "test-model",
            "temperature": 0.3,
            "abbr_max_len": 4,
        }
    }


def _mock_standard_roots():
    return [
        {
            "business_domain": "订单",
            "domain_code": "ord",
            "chinese_name": "订单号",
            "full_root": "order_no",
            "abbr_root": "ord_no",
            "recommended_type": "VARCHAR(64)",
        }
    ]


def _mock_large_historical_roots(size=120):
    return [
        {
            "business_domain": "订单",
            "domain_code": "ord",
            "chinese_name": f"订单字段{i}",
            "full_root": f"order_field_{i}",
            "abbr_root": f"ord_{i}",
            "recommended_type": "VARCHAR(64)",
        }
        for i in range(size)
    ]


class DummyResponse:
    def __init__(self, payload, status_code=200, text=""):
        self._payload = payload
        self.status_code = status_code
        self.text = text
        self.encoding = "utf-8"

    def json(self):
        return self._payload


class StreamDummyResponse(DummyResponse):
    def __init__(self, payload_lines, status_code=200):
        super().__init__({}, status_code=status_code, text="")
        self._payload_lines = payload_lines

    def iter_lines(self, decode_unicode=True):
        for line in self._payload_lines:
            yield line


def test_governance_run_handles_remote_disconnected(monkeypatch):
    monkeypatch.setattr(main_module, "load_effective_historical_roots", _mock_historical_roots)
    monkeypatch.setattr(main_module, "get_system_prompt", lambda: "system")

    def _raise(*args, **kwargs):
        raise requests.exceptions.ConnectionError(RemoteDisconnected("Remote end closed connection without response"))

    monkeypatch.setattr(main_module.requests, "post", _raise)

    response = client.post("/api/governance/run", json=_request_body())
    assert response.status_code == 500
    body = response.json()
    assert body["code"] == 1
    assert "词根治理失败" in body["message"]


def test_governance_run_handles_timeout(monkeypatch):
    monkeypatch.setattr(main_module, "load_effective_historical_roots", _mock_historical_roots)
    monkeypatch.setattr(main_module, "get_system_prompt", lambda: "system")

    def _raise(*args, **kwargs):
        raise requests.exceptions.ReadTimeout("timed out")

    monkeypatch.setattr(main_module.requests, "post", _raise)

    response = client.post("/api/governance/run", json=_request_body())
    assert response.status_code == 500
    body = response.json()
    assert body["code"] == 1
    assert "响应超时" in body["message"]


def test_governance_run_success(monkeypatch):
    monkeypatch.setattr(main_module, "load_effective_historical_roots", _mock_historical_roots)
    monkeypatch.setattr(main_module, "load_standard_roots", lambda: [])
    monkeypatch.setattr(main_module, "get_system_prompt", lambda: "system")

    payload = {
        "choices": [
            {
                "message": {
                    "content": """
[
  {
    "domain_code": "ord",
    "business_domain": "订单",
    "chinese_name": "订单号",
    "full_root": "order_no",
    "abbr_root": "ord_no",
    "recommended_type": "VARCHAR(64)",
    "governance_status": "governed"
  }
]
"""
                }
            }
        ]
    }

    monkeypatch.setattr(main_module.requests, "post", lambda *args, **kwargs: DummyResponse(payload))

    response = client.post("/api/governance/run", json=_request_body())
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert len(body["data"]) == 1
    assert body["meta"]["raw_root_count"] == 2
    assert body["meta"]["prepared_root_count"] == 2


def test_governance_run_filters_standard_roots(monkeypatch):
    monkeypatch.setattr(main_module, "load_effective_historical_roots", _mock_historical_roots)
    monkeypatch.setattr(main_module, "load_standard_roots", _mock_standard_roots)
    monkeypatch.setattr(main_module, "get_system_prompt", lambda: "system")

    captured_prompts = []

    def _fake_post(*args, **kwargs):
        payload = kwargs.get("json", {})
        messages = payload.get("messages", [])
        if messages:
            captured_prompts.append(messages[-1].get("content", ""))
        return DummyResponse({
            "choices": [
                {
                    "message": {
                        "content": """
[
  {
    "domain_code": "ord",
    "business_domain": "订单",
    "chinese_name": "订单编号",
    "full_root": "order_code",
    "abbr_root": "ord_cd",
    "recommended_type": "VARCHAR(64)",
    "governance_status": "governed"
  }
]
"""
                    }
                }
            ]
        })

    monkeypatch.setattr(main_module.requests, "post", _fake_post)

    response = client.post("/api/governance/run", json=_request_body())
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["meta"]["prepared_root_count"] == 2
    assert body["meta"]["excluded_standard_count"] == 1
    assert body["meta"]["filtered_root_count"] == 1
    assert captured_prompts
    assert "订单号" not in captured_prompts[0]
    assert "订单编号" in captured_prompts[0]


def test_governance_run_skips_when_all_historical_roots_already_standardized(monkeypatch):
    monkeypatch.setattr(main_module, "load_effective_historical_roots", lambda: [_mock_historical_roots()[0]])
    monkeypatch.setattr(main_module, "load_standard_roots", _mock_standard_roots)
    monkeypatch.setattr(main_module, "get_system_prompt", lambda: "system")

    def _raise_if_called(*args, **kwargs):
        raise AssertionError("LLM should not be called when all roots are already standardized")

    monkeypatch.setattr(main_module.requests, "post", _raise_if_called)

    response = client.post("/api/governance/run", json=_request_body())
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["data"] == []
    assert body["meta"]["excluded_standard_count"] == 1
    assert body["meta"]["filtered_root_count"] == 0
    assert body["meta"]["chunk_count"] == 0
    assert "无需再次治理" in body["message"] or "无需再次治理" in body["detail"] if "detail" in body else True


def test_governance_run_handles_load_failure(monkeypatch):
    def _raise():
        raise ValueError("broken historical roots")

    monkeypatch.setattr(main_module, "load_effective_historical_roots", _raise)

    response = client.post("/api/governance/run", json=_request_body())
    assert response.status_code == 500
    body = response.json()
    assert body["code"] == 1
    assert "broken historical roots" in body["message"]


def test_governance_run_handles_large_root_sets_without_500(monkeypatch):
    monkeypatch.setattr(main_module, "load_effective_historical_roots", _mock_large_historical_roots)
    monkeypatch.setattr(main_module, "load_standard_roots", lambda: [])
    monkeypatch.setattr(main_module, "get_system_prompt", lambda: "system")

    post_calls = []

    def _extract_field(line: str, field: str, default: str = "") -> str:
        match = re.search(rf"{field}=([^|]+)", line)
        return match.group(1).strip() if match else default

    def _fake_post(*args, **kwargs):
        payload = kwargs.get("json", {})
        messages = payload.get("messages", [])
        content = messages[-1].get("content", "") if messages else ""
        post_calls.append(content)
        root_line = next(
            (
                line for line in content.splitlines()
                if "chinese_name=" in line and "full_root=" in line and "abbr_root=" in line
            ),
            "",
        )
        if not root_line:
            return DummyResponse({"choices": [{"message": {"content": "[]"}}]})

        result = {
            "domain_code": _extract_field(root_line, "domain_code", "ord"),
            "business_domain": _extract_field(root_line, "domain", "订单"),
            "chinese_name": _extract_field(root_line, "chinese_name", "订单字段"),
            "full_root": _extract_field(root_line, "full_root", "order_field"),
            "abbr_root": _extract_field(root_line, "abbr_root", "ord"),
            "recommended_type": _extract_field(root_line, "recommended_type", "VARCHAR(64)"),
            "governance_status": "governed",
        }
        return DummyResponse({"choices": [{"message": {"content": f"[{json.dumps(result, ensure_ascii=False)}]"}}]})

    monkeypatch.setattr(main_module.requests, "post", _fake_post)

    response = client.post("/api/governance/run", json=_request_body())
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["meta"]["raw_root_count"] == 120
    assert body["meta"]["chunk_count"] == 3
    assert len(post_calls) == 4


def test_governance_run_accepts_streaming_llm_responses(monkeypatch):
    monkeypatch.setattr(main_module, "load_effective_historical_roots", _mock_historical_roots)
    monkeypatch.setattr(main_module, "load_standard_roots", lambda: [])
    monkeypatch.setattr(main_module, "get_system_prompt", lambda: "system")

    def _fake_post(*args, **kwargs):
        payload = kwargs.get("json", {})
        content = payload.get("messages", [{}])[-1].get("content", "")
        if "全局合并" in content:
            lines = [
                'data: {"choices":[{"delta":{"content":"{\\"domain_code\\":\\"ord\\",\\"business_domain\\":\\"订单\\",\\"chinese_name\\":\\"订单号\\",\\"full_root\\":\\"order_no\\",\\"abbr_root\\":\\"ord_no\\",\\"recommended_type\\":\\"VARCHAR(64)\\",\\"governance_status\\":\\"governed\\"}"}}]}',
                "data: [DONE]",
            ]
            return StreamDummyResponse(lines)
        lines = [
            'data: {"choices":[{"delta":{"content":"{\\"domain_code\\":\\"ord\\",\\"business_domain\\":\\"订单\\",\\"chinese_name\\":\\"订单号\\",\\"full_root\\":\\"order_no\\",\\"abbr_root\\":\\"ord_no\\",\\"recommended_type\\":\\"VARCHAR(64)\\",\\"governance_status\\":\\"governed\\"}"}}]}',
            "data: [DONE]",
        ]
        return StreamDummyResponse(lines)

    monkeypatch.setattr(main_module.requests, "post", _fake_post)

    response = client.post("/api/governance/run", json=_request_body())
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert len(body["data"]) == 1


def test_governance_run_parses_object_response_with_noise(monkeypatch):
    monkeypatch.setattr(main_module, "load_effective_historical_roots", _mock_historical_roots)
    monkeypatch.setattr(main_module, "load_standard_roots", lambda: [])
    monkeypatch.setattr(main_module, "get_system_prompt", lambda: "system")

    def _fake_post(*args, **kwargs):
        class NoiseResponse(DummyResponse):
            def __init__(self):
                super().__init__({}, status_code=200, text='noise\n{"choices":[{"message":{"content":"{\\"domain_code\\":\\"ord\\",\\"business_domain\\":\\"订单\\",\\"chinese_name\\":\\"订单号\\",\\"full_root\\":\\"order_no\\",\\"abbr_root\\":\\"ord_no\\",\\"recommended_type\\":\\"VARCHAR(64)\\",\\"governance_status\\":\\"governed\\"}"}}]}\nmore noise')

        return NoiseResponse()

    monkeypatch.setattr(main_module.requests, "post", _fake_post)

    response = client.post("/api/governance/run", json=_request_body())
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert len(body["data"]) == 1
