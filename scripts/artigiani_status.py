#!/usr/bin/env python3
import argparse
import json
import sys
from urllib import error, request


def fetch_json(url: str):
    req = request.Request(url, headers={"Accept": "application/json"})
    try:
        with request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code} su {url}: {body}") from exc
    except Exception as exc:
        raise SystemExit(f"Errore chiamando {url}: {exc}") from exc


def format_lead(lead: dict) -> str:
    latest_quote = lead.get("latest_quote") or {}
    quote_status = latest_quote.get("status") or "none"
    missing = ", ".join(lead.get("missing_fields") or []) or "-"
    return (
        f"[{lead['id']}] {lead.get('client_name') or 'cliente sconosciuto'} | "
        f"status={lead.get('status')} | action={lead.get('suggested_action')} | "
        f"missing={missing} | quote={quote_status}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Mostra stato lead e reviewer di Automazione Artigiani")
    parser.add_argument("--base-url", default="http://127.0.0.1:8010")
    parser.add_argument("--lead-id", type=int)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")

    if args.lead_id:
        lead = fetch_json(f"{base}/api/leads/{args.lead_id}")
        if args.json:
            print(json.dumps(lead, ensure_ascii=False, indent=2))
            return 0
        print(format_lead(lead))
        print(f"review_summary={lead.get('review_summary') or '-'}")
        normalized = lead.get("normalized_payload") or {}
        print(f"descrizione={normalized.get('description') or '-'}")
        return 0

    summary = fetch_json(f"{base}/api/dashboard/summary")
    leads = fetch_json(f"{base}/api/leads")["leads"][: args.limit]

    if args.json:
        print(json.dumps({"summary": summary, "leads": leads}, ensure_ascii=False, indent=2))
        return 0

    counts = summary.get("counts", {})
    print("Dashboard Automazione Artigiani")
    print(
        "counts="
        + ", ".join(
            f"{key}:{counts.get(key, 0)}"
            for key in ["new", "incomplete", "needs_review", "ready_for_quote", "sent", "draft_quotes"]
        )
    )
    print(f"email_enabled={summary.get('email_enabled')} receiver={summary.get('active_receiver_email')}")
    print("Leads:")
    if not leads:
        print("- nessun lead")
        return 0
    for lead in leads:
        print("- " + format_lead(lead))
    return 0


if __name__ == "__main__":
    sys.exit(main())
