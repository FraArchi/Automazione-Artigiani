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


def test_webhook_with_complete_data_creates_new_lead_without_draft_quote(monkeypatch, tmp_path):
    main = load_app(monkeypatch, tmp_path)
    client = TestClient(main.app)

    payload = {
        "Cliente": "Mario Rossi",
        "Email": "mario@example.com",
        "Telefono": "+393331234567",
        "Lavoro": "Impianto elettrico cucina",
        "Ore": "4",
        "Costo orario": "45",
        "Materiali": "120",
        "Nome artigiano": "Demo Artigiano",
        "Mestiere": "Elettricista",
    }

    response = client.post("/webhook", json=payload)
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

    summary = client.get("/api/dashboard/summary").json()
    assert summary["counts"]["new"] == 1
    assert summary["counts"]["draft_quotes"] == 0


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
