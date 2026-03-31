from fastapi.testclient import TestClient

from tests.test_app import load_app


class ApiClientDouble:
    def __init__(self, client: TestClient):
        self.client = client

    def list_leads(self):
        response = self.client.get("/api/leads")
        assert response.status_code == 200
        return response.json()["leads"]

    def update_lead_review(self, lead_id: int, review: dict):
        response = self.client.patch(f"/api/leads/{lead_id}/review", json=review)
        assert response.status_code == 200
        return response.json()

    def generate_quote(self, lead_id: int):
        response = self.client.post(f"/api/leads/{lead_id}/generate-quote")
        assert response.status_code == 200
        return response.json()


def create_manual_lead(main, normalized_payload: dict, status: str = "new") -> int:
    db = main.SessionLocal()
    try:
        lead = main.Lead(
            source="manual-test",
            client_name=normalized_payload.get("client_name"),
            client_email=normalized_payload.get("client_email"),
            client_phone=normalized_payload.get("client_phone"),
            job_type=normalized_payload.get("job_type"),
            description=normalized_payload.get("description"),
            raw_payload=main.dumps_json(normalized_payload),
            normalized_payload=main.dumps_json(normalized_payload),
            status=status,
            missing_fields=main.dumps_json([]),
            review_summary=None,
            suggested_action=None,
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)
        return lead.id
    finally:
        db.close()


def test_review_lead_marks_implausible_values_as_needs_review():
    from hermes_reviewer import review_lead

    decision = review_lead(
        {
            "id": 1,
            "client_name": "Mario Rossi",
            "client_email": "mario@example.com",
            "client_phone": "+393331234567",
            "description": "Installazione impianto elettrico cucina",
            "normalized_payload": {
                "client_name": "Mario Rossi",
                "client_email": "mario@example.com",
                "client_phone": "+393331234567",
                "description": "Installazione impianto elettrico cucina",
                "ore": "30",
                "costo_orario": "400",
                "materiali": "20",
            },
            "latest_quote": None,
        }
    )

    assert decision["status"] == "needs_review"
    assert decision["suggested_action"] == "human_review"
    assert "verifica" in decision["review_summary"].lower()


def test_process_pending_leads_generates_quote_for_new_ready_lead(monkeypatch, tmp_path):
    main = load_app(monkeypatch, tmp_path)
    client = TestClient(main.app)

    lead_id = create_manual_lead(
        main,
        {
            "client_name": "Anna Bianchi",
            "client_email": "anna@example.com",
            "client_phone": "+393339998888",
            "description": "Sostituzione rubinetto cucina con montaggio",
            "ore": "2",
            "costo_orario": "45",
            "materiali": "35",
            "job_type": "Idraulico",
        },
        status="new",
    )

    from hermes_reviewer import process_pending_leads

    stats = process_pending_leads(ApiClientDouble(client))
    lead = client.get(f"/api/leads/{lead_id}").json()

    assert stats["processed"] == 1
    assert stats["generated_quotes"] == 1
    assert lead["status"] == "ready_for_quote"
    assert lead["suggested_action"] == "review_draft"
    assert lead["latest_quote"]["status"] == "draft"


def test_process_pending_leads_marks_missing_contact(monkeypatch, tmp_path):
    main = load_app(monkeypatch, tmp_path)
    client = TestClient(main.app)

    response = client.post(
        "/webhook",
        json={
            "Cliente": "Luca",
            "Lavoro": "Riparazione perdita bagno",
            "Ore": "2",
            "Costo orario": "40",
            "Materiali": "15",
        },
    )
    assert response.status_code == 200
    lead_id = response.json()["lead_id"]

    from hermes_reviewer import process_pending_leads

    stats = process_pending_leads(ApiClientDouble(client))
    lead = client.get(f"/api/leads/{lead_id}").json()

    assert stats["processed"] == 1
    assert lead["status"] == "incomplete"
    assert "contact" in lead["missing_fields"]
    assert lead["suggested_action"] == "request_missing_fields"
    assert "contatto" in lead["review_summary"].lower()
