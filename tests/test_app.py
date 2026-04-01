import importlib
import sys
from pathlib import Path

from fastapi.testclient import TestClient


def load_app(monkeypatch, tmp_path: Path):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("EMAIL_ENABLED", "false")
    monkeypatch.setenv("DEFAULT_RECEIVER_EMAIL", "owner@example.com")
    monkeypatch.setenv("QUOTE_OUTPUT_DIR", str(tmp_path / "quotes"))
    monkeypatch.chdir("/home/fra/Documenti/progetti/automazione-artigiani")

    if "main" in sys.modules:
        del sys.modules["main"]

    import main

    importlib.reload(main)
    return main


def build_tally_payload(response_id: str = "resp_123"):
    return {
        "eventId": f"evt_{response_id}",
        "eventType": "FORM_RESPONSE",
        "data": {
            "formId": "form_abc",
            "responseId": response_id,
            "fields": [
                {"label": "Cliente", "value": "Mario Rossi"},
                {"label": "Email", "value": "mario@example.com"},
                {"label": "Telefono", "value": "+393331234567"},
                {"label": "Lavoro", "value": "Impianto elettrico cucina"},
                {"label": "Ore", "value": "4"},
                {"label": "Costo orario", "value": "45"},
                {"label": "Materiali", "value": "120"},
                {"label": "Nome artigiano", "value": "Demo Artigiano"},
                {"label": "Mestiere", "value": "Elettricista"},
            ],
        },
    }


def test_webhook_with_tally_payload_sets_source_and_creates_new_lead_without_draft_quote(monkeypatch, tmp_path):
    main = load_app(monkeypatch, tmp_path)
    client = TestClient(main.app)

    response = client.post("/webhook", json=build_tally_payload())
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "success"
    assert body["lead_status"] == "new"
    assert body["quote_id"] is None
    assert body["quote_status"] is None
    assert body["suggested_action"] == "run_reviewer"

    leads_response = client.get("/api/leads")
    assert leads_response.status_code == 200
    leads = leads_response.json()["leads"]
    assert len(leads) == 1
    assert leads[0]["client_name"] == "Mario Rossi"
    assert leads[0]["status"] == "new"
    assert leads[0]["latest_quote"] is None
    assert leads[0]["suggested_action"] == "run_reviewer"
    assert leads[0]["source"] == "tally_webhook"

    summary = client.get("/api/dashboard/summary").json()
    assert summary["counts"]["new"] == 1
    assert summary["counts"]["draft_quotes"] == 0


def test_duplicate_webhook_returns_existing_lead_without_creating_duplicate(monkeypatch, tmp_path):
    main = load_app(monkeypatch, tmp_path)
    client = TestClient(main.app)
    payload = build_tally_payload(response_id="resp_dup")

    first = client.post("/webhook", json=payload)
    second = client.post("/webhook", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["status"] == "success"
    assert second.json()["status"] == "duplicate"
    assert second.json()["lead_id"] == first.json()["lead_id"]
    assert second.json()["duplicate"] is True

    leads = client.get("/api/leads").json()["leads"]
    assert len(leads) == 1

    activity = client.get("/api/activity-log").json()["items"]
    assert any(item["event_type"] == "webhook_duplicate" for item in activity)


def test_activity_log_endpoint_and_summary_include_recent_events_and_needs_review(monkeypatch, tmp_path):
    main = load_app(monkeypatch, tmp_path)
    client = TestClient(main.app)

    create_response = client.post("/webhook", json=build_tally_payload(response_id="resp_needs_review"))
    lead_id = create_response.json()["lead_id"]

    review_response = client.patch(
        f"/api/leads/{lead_id}/review",
        json={
            "status": "needs_review",
            "missing_fields": [],
            "review_summary": "Costo orario troppo alto, serve verifica umana.",
            "suggested_action": "human_review",
        },
    )
    assert review_response.status_code == 200

    activity_response = client.get("/api/activity-log?limit=10")
    assert activity_response.status_code == 200
    items = activity_response.json()["items"]
    assert len(items) >= 2
    assert items[0]["event_type"] == "lead_review_updated"
    assert items[0]["actor"] == "hermes"

    summary = client.get("/api/dashboard/summary").json()
    assert summary["counts"]["needs_review"] == 1
    assert len(summary["recent_activity"]) >= 2
    assert summary["recent_activity"][0]["event_type"] == "lead_review_updated"


def test_webhook_with_missing_data_still_saves_new_lead_for_reviewer(monkeypatch, tmp_path):
    main = load_app(monkeypatch, tmp_path)
    client = TestClient(main.app)

    response = client.post(
        "/webhook",
        json={
            "Cliente": "Luca",
            "Lavoro": "Riparazione perdita",
            "Ore": "2",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["lead_status"] == "new"
    assert body["quote_status"] is None
    assert body["missing_fields"] == []
    assert body["suggested_action"] == "run_reviewer"

    leads = client.get("/api/leads").json()["leads"]
    assert leads[0]["status"] == "new"
    assert leads[0]["missing_fields"] == []
    assert leads[0]["suggested_action"] == "run_reviewer"


def test_send_quote_is_blocked_when_email_is_disabled(monkeypatch, tmp_path):
    main = load_app(monkeypatch, tmp_path)
    client = TestClient(main.app)

    create_response = client.post(
        "/webhook",
        json={
            "Cliente": "Mario Rossi",
            "Email": "mario@example.com",
            "Lavoro": "Impianto elettrico cucina",
            "Ore": "4",
            "Costo orario": "45",
            "Materiali": "120",
        },
    )
    lead_id = create_response.json()["lead_id"]

    review_response = client.patch(
        f"/api/leads/{lead_id}/review",
        json={
            "status": "ready_for_quote",
            "missing_fields": [],
            "review_summary": "Lead pronto per bozza.",
            "suggested_action": "generate_quote",
        },
    )
    assert review_response.status_code == 200

    generate_response = client.post(f"/api/leads/{lead_id}/generate-quote")
    assert generate_response.status_code == 200
    quote_id = generate_response.json()["quote"]["id"]

    send_response = client.post(f"/api/quotes/{quote_id}/send")
    assert send_response.status_code == 409
    assert send_response.json()["detail"] == "Email sending is disabled in this environment"
