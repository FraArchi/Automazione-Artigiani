import argparse
import json
import time
from typing import Any
from urllib import error, request


DEFAULT_REVIEWABLE_STATUSES = {"new", "incomplete", "ready_for_quote", "needs_review"}
REQUIRED_FIELDS = ("client_name", "description", "ore", "costo_orario", "materiali")
FIELD_LABELS = {
    "client_name": "cliente",
    "description": "descrizione",
    "ore": "ore",
    "costo_orario": "costo orario",
    "materiali": "materiali",
    "contact": "contatto",
}


def parse_currency(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip().replace("€", "")
    text = text.replace(" ", "")
    if not text:
        return None
    if "," in text and "." not in text:
        text = text.replace(",", ".")
    else:
        text = text.replace(",", "")
    try:
        return float(text)
    except ValueError:
        return None


def _normalized_field(lead: dict[str, Any], field: str) -> Any:
    normalized = lead.get("normalized_payload") or {}
    if field in normalized and normalized.get(field) not in (None, ""):
        return normalized.get(field)
    return lead.get(field)


def review_lead(lead: dict[str, Any]) -> dict[str, Any]:
    missing_fields: list[str] = []

    for field in REQUIRED_FIELDS:
        value = _normalized_field(lead, field)
        if value in (None, ""):
            missing_fields.append(field)

    client_email = _normalized_field(lead, "client_email")
    client_phone = _normalized_field(lead, "client_phone")
    if not client_email and not client_phone:
        missing_fields.append("contact")

    if missing_fields:
        missing_list = ", ".join(FIELD_LABELS.get(field, field) for field in missing_fields)
        return {
            "status": "incomplete",
            "missing_fields": missing_fields,
            "review_summary": f"Richiesta incompleta: manca {missing_list}. Prima recupera questi dati dal cliente.",
            "suggested_action": "request_missing_fields",
        }

    anomalies: list[str] = []
    ore = parse_currency(_normalized_field(lead, "ore"))
    costo_orario = parse_currency(_normalized_field(lead, "costo_orario"))
    materiali = parse_currency(_normalized_field(lead, "materiali"))
    description = str(_normalized_field(lead, "description") or "").strip()

    if ore is None or ore <= 0:
        anomalies.append("ore non valide")
    elif ore > 16:
        anomalies.append("ore stimate fuori scala")

    if costo_orario is None or costo_orario <= 0:
        anomalies.append("costo orario non valido")
    elif costo_orario > 150:
        anomalies.append("costo orario molto alto")

    if materiali is None or materiali < 0:
        anomalies.append("materiali non validi")
    elif materiali > 5000:
        anomalies.append("costo materiali molto alto")

    if len(description) < 12:
        anomalies.append("descrizione troppo vaga")

    if anomalies:
        return {
            "status": "needs_review",
            "missing_fields": [],
            "review_summary": f"Verifica manuale consigliata: {', '.join(anomalies)}.",
            "suggested_action": "human_review",
        }

    latest_quote = lead.get("latest_quote")
    if latest_quote:
        summary = "Lead completo e coerente. Bozza già presente: controlla il preventivo prima dell'invio."
        suggested_action = "review_draft"
    else:
        summary = "Lead completo e coerente. Puoi generare la bozza del preventivo."
        suggested_action = "generate_quote"

    return {
        "status": "ready_for_quote",
        "missing_fields": [],
        "review_summary": summary,
        "suggested_action": suggested_action,
    }


def process_pending_leads(api_client, statuses: set[str] | None = None, limit: int | None = None) -> dict[str, int]:
    reviewable_statuses = statuses or DEFAULT_REVIEWABLE_STATUSES
    leads = api_client.list_leads()
    pending = [lead for lead in leads if lead.get("status") in reviewable_statuses]
    if limit is not None:
        pending = pending[:limit]

    processed = 0
    generated_quotes = 0

    for lead in pending:
        decision = review_lead(lead)
        api_client.update_lead_review(lead["id"], decision)
        processed += 1

        if decision["status"] == "ready_for_quote" and decision["suggested_action"] == "generate_quote":
            api_client.generate_quote(lead["id"])
            api_client.update_lead_review(
                lead["id"],
                {
                    "status": "ready_for_quote",
                    "missing_fields": [],
                    "review_summary": "Bozza generata da Hermes reviewer. Controlla il preventivo prima dell'invio.",
                    "suggested_action": "review_draft",
                },
            )
            generated_quotes += 1

    return {
        "processed": processed,
        "generated_quotes": generated_quotes,
    }


class HttpApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        data = None
        headers = {"Content-Type": "application/json"}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")

        req = request.Request(f"{self.base_url}{path}", data=data, headers=headers, method=method)
        try:
            with request.urlopen(req) as response:
                body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code} su {path}: {body}") from exc
        return json.loads(body) if body else None

    def list_leads(self):
        return self._request("GET", "/api/leads")["leads"]

    def update_lead_review(self, lead_id: int, review: dict[str, Any]):
        return self._request("PATCH", f"/api/leads/{lead_id}/review", review)

    def generate_quote(self, lead_id: int):
        return self._request("POST", f"/api/leads/{lead_id}/generate-quote")


def run_once(base_url: str, limit: int | None = None) -> dict[str, int]:
    client = HttpApiClient(base_url)
    result = process_pending_leads(client, limit=limit)
    print(json.dumps(result, ensure_ascii=False))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Hermes reviewer per lead artigiani")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="URL base dell'API FastAPI")
    parser.add_argument("--limit", type=int, default=None, help="Numero massimo di lead da processare per ciclo")
    parser.add_argument("--watch", type=int, default=0, help="Intervallo in secondi per esecuzione continua")
    args = parser.parse_args()

    if args.watch <= 0:
        run_once(args.base_url, limit=args.limit)
        return 0

    while True:
        run_once(args.base_url, limit=args.limit)
        time.sleep(args.watch)


if __name__ == "__main__":
    raise SystemExit(main())
