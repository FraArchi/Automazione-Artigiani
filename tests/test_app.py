import importlib
import json
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient


class FakeSMTP:
    sent_messages = []

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def login(self, username, password):
        self.username = username
        self.password = password

    def send_message(self, message):
        FakeSMTP.sent_messages.append(message)


def load_app(monkeypatch, tmp_path: Path):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("ENVIRONMENT", "test")
    if "EMAIL_ENABLED" not in os.environ:
        monkeypatch.setenv("EMAIL_ENABLED", "false")
    if "DEFAULT_RECEIVER_EMAIL" not in os.environ:
        monkeypatch.setenv("DEFAULT_RECEIVER_EMAIL", "owner@example.com")
    if "QUOTE_OUTPUT_DIR" not in os.environ:
        monkeypatch.setenv("QUOTE_OUTPUT_DIR", str(tmp_path / "quotes"))

    project_root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(project_root)

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


def load_json_fixture(name: str):
    fixture_path = Path(__file__).resolve().parent / "fixtures" / name
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def build_real_tally_payload(response_id: str = "resp_real"):
    payload = load_json_fixture("tally_real_payload_anonymized.json")
    payload["eventId"] = f"evt_{response_id}"
    payload["data"]["responseId"] = response_id
    return payload


def test_webhook_endpoint_accepts_get_and_options_for_external_validation(monkeypatch, tmp_path):
    main = load_app(monkeypatch, tmp_path)
    client = TestClient(main.app)

    get_response = client.get("/webhook")
    assert get_response.status_code == 200
    assert "POST" in get_response.json()["message"]

    options_response = client.options("/webhook")
    assert options_response.status_code == 204


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


def test_real_tally_labels_are_normalized_correctly(monkeypatch, tmp_path):
    main = load_app(monkeypatch, tmp_path)
    client = TestClient(main.app)

    response = client.post("/webhook", json=build_real_tally_payload())
    assert response.status_code == 200

    lead = client.get("/api/leads").json()["leads"][0]
    normalized = lead["normalized_payload"]

    assert lead["source"] == "tally_webhook"
    assert lead["client_name"] == "Cliente Tally Reale"
    assert normalized["artisan_name"] == "Artigiano Test Hermes"
    assert normalized["artisan_email"] == "artigiano.test@example.com"
    assert normalized["job_type"] == "Elettricista"
    assert normalized["description"] == "Installazione plafoniera e controllo impianto cucina"
    assert normalized["materiali"] == "60"
    assert normalized["notes"] == "Test Tally reale anonimizzato"
    assert normalized["client_address"] == "Via Roma 123, Milano"
    assert normalized["urgency"] == "Media"


def test_mapping_debug_endpoint_returns_unmapped_fields_for_review(monkeypatch, tmp_path):
    main = load_app(monkeypatch, tmp_path)
    client = TestClient(main.app)

    payload = build_real_tally_payload(response_id="resp_debug")
    payload["data"]["fields"].append({"label": "Budget massimo", "value": "2000"})
    payload["data"]["fields"].append({"label": "Disponibilità", "value": "Sabato mattina"})

    create_response = client.post("/webhook", json=payload)
    assert create_response.status_code == 200
    lead_id = create_response.json()["lead_id"]

    debug_response = client.get(f"/api/leads/{lead_id}/mapping-debug")
    assert debug_response.status_code == 200
    debug = debug_response.json()

    assert debug["source"] == "tally_webhook"
    assert debug["normalized_payload"]["client_name"] == "Cliente Tally Reale"
    assert debug["mapped_labels_by_field"]["client_name"] == "Nome del Cliente"
    assert debug["unmapped_fields"] == {
        "Budget massimo": "2000",
        "Disponibilità": "Sabato mattina",
    }
    assert debug["missing_critical_fields"] == ["contact"]

    activity = client.get("/api/activity-log?limit=10").json()["items"]
    assert any(item["event_type"] == "webhook_unmapped_fields" for item in activity)


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


def test_generate_quote_notifies_artisan_and_download_endpoint_works(monkeypatch, tmp_path):
    monkeypatch.setenv("EMAIL_ENABLED", "true")
    monkeypatch.setenv("SENDER_EMAIL", "noreply@example.com")
    monkeypatch.setenv("SENDER_PASSWORD", "secret-password")
    monkeypatch.setenv("PUBLIC_BASE_URL", "https://app.example.com")
    main = load_app(monkeypatch, tmp_path)
    FakeSMTP.sent_messages.clear()
    monkeypatch.setattr(main.smtplib, "SMTP_SSL", FakeSMTP)
    client = TestClient(main.app)

    create_response = client.post("/webhook", json=build_real_tally_payload(response_id="resp_notify"))
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
    quote = generate_response.json()["quote"]

    assert len(FakeSMTP.sent_messages) == 1
    message = FakeSMTP.sent_messages[0]
    text_part = message.get_payload()[0].get_payload(decode=True).decode()
    assert message["To"] == "artigiano.test@example.com"
    assert "Bozza preventivo pronta" in message["Subject"]
    assert f"/api/quotes/{quote['id']}/download" in text_part
    assert quote["status"] == "draft"

    download_response = client.get(f"/api/quotes/{quote['id']}/download")
    assert download_response.status_code == 200
    assert "attachment; filename=" in download_response.headers["content-disposition"]

    activity = client.get("/api/activity-log?limit=10").json()["items"]
    assert any(item["event_type"] == "quote_ready_notified" for item in activity)


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
