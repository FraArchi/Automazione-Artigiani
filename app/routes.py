from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse

from app.models import ActivityLog, Lead, Quote
from app.services import (
    bootstrap_config,
    detect_source,
    dumps_json,
    email_sending_enabled,
    find_duplicate_lead,
    generate_quote_for_lead,
    get_active_receiver,
    loads_json,
    log_event,
    normalize_payload,
    send_quote_email,
    serialize_activity,
    serialize_lead,
    serialize_quote,
    set_active_receiver,
)
from app.settings import Settings
from app.utils import now_utc


def register_routes(app: FastAPI, SessionLocal, settings: Settings, smtplib_module) -> None:
    bootstrap_config(SessionLocal, settings)

    @app.get("/")
    async def serve_dashboard():
        index_path = settings.static_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"message": "Dashboard non trovata"}

    @app.get("/api/dashboard/summary")
    async def api_dashboard_summary():
        db = SessionLocal()
        try:
            leads = db.query(Lead).all()
            recent_activity = db.query(ActivityLog).order_by(ActivityLog.created_at.desc(), ActivityLog.id.desc()).limit(10).all()
            counts = {
                "new": 0,
                "incomplete": 0,
                "needs_review": 0,
                "ready_for_quote": 0,
                "quoted": 0,
                "sent": 0,
                "error": 0,
                "archived": 0,
                "draft_quotes": db.query(Quote).filter(Quote.status == "draft").count(),
            }
            for lead in leads:
                counts.setdefault(lead.status, 0)
                counts[lead.status] += 1

            return {
                "counts": counts,
                "active_receiver_email": get_active_receiver(db, settings),
                "email_enabled": email_sending_enabled(db, settings),
                "recent_activity": [serialize_activity(item) for item in recent_activity],
            }
        finally:
            db.close()

    @app.get("/api/activity-log")
    async def api_activity_log(limit: int = 20):
        db = SessionLocal()
        try:
            safe_limit = max(1, min(limit, 100))
            items = db.query(ActivityLog).order_by(ActivityLog.created_at.desc(), ActivityLog.id.desc()).limit(safe_limit).all()
            return {"items": [serialize_activity(item) for item in items]}
        finally:
            db.close()

    @app.get("/api/leads")
    async def api_get_leads():
        db = SessionLocal()
        try:
            leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
            return {"leads": [serialize_lead(lead) for lead in leads]}
        finally:
            db.close()

    @app.get("/api/leads/{lead_id}")
    async def api_get_lead(lead_id: int):
        db = SessionLocal()
        try:
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                raise HTTPException(status_code=404, detail="Lead not found")
            return serialize_lead(lead)
        finally:
            db.close()

    @app.patch("/api/leads/{lead_id}/review")
    async def api_update_lead_review(lead_id: int, request: Request):
        data = await request.json()
        db = SessionLocal()
        try:
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                raise HTTPException(status_code=404, detail="Lead not found")

            if "status" in data:
                lead.status = data["status"]
            if "missing_fields" in data:
                lead.missing_fields = dumps_json(data["missing_fields"])
            if "review_summary" in data:
                lead.review_summary = data["review_summary"]
            if "suggested_action" in data:
                lead.suggested_action = data["suggested_action"]
            lead.updated_at = now_utc()
            db.commit()
            log_event(db, "lead_review_updated", "Revisione lead aggiornata", lead_id=lead.id, actor="hermes")
            db.refresh(lead)
            return serialize_lead(lead)
        finally:
            db.close()

    @app.post("/api/leads/{lead_id}/generate-quote")
    async def api_generate_quote(lead_id: int):
        db = SessionLocal()
        try:
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                raise HTTPException(status_code=404, detail="Lead not found")
            if lead.status != "ready_for_quote":
                raise HTTPException(status_code=409, detail="Lead is not ready for quote generation")

            quote = generate_quote_for_lead(db, settings, smtplib_module, lead)
            return {"status": "success", "quote": serialize_quote(quote), "lead": serialize_lead(lead)}
        finally:
            db.close()

    @app.get("/api/quotes/{quote_id}/download")
    async def api_download_quote(quote_id: int):
        db = SessionLocal()
        try:
            quote = db.query(Quote).filter(Quote.id == quote_id).first()
            if not quote:
                raise HTTPException(status_code=404, detail="Quote not found")
            if not Path(quote.file_path).exists():
                raise HTTPException(status_code=404, detail="Quote file not found")
            return FileResponse(
                quote.file_path,
                filename=Path(quote.file_path).name,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        finally:
            db.close()

    @app.post("/api/quotes/{quote_id}/send")
    async def api_send_quote(quote_id: int):
        db = SessionLocal()
        try:
            quote = db.query(Quote).filter(Quote.id == quote_id).first()
            if not quote:
                raise HTTPException(status_code=404, detail="Quote not found")
            send_quote_email(db, settings, smtplib_module, quote)
            db.refresh(quote)
            return {"status": "success", "quote": serialize_quote(quote)}
        finally:
            db.close()

    @app.get("/api/receivers")
    async def api_get_receivers():
        db = SessionLocal()
        try:
            return {"receivers": [get_active_receiver(db, settings)]}
        finally:
            db.close()

    @app.post("/api/receivers")
    async def api_set_receiver(request: Request):
        data = await request.json()
        email = (data.get("email") or "").strip()
        if not email:
            raise HTTPException(status_code=400, detail="Email mancante")

        db = SessionLocal()
        try:
            set_active_receiver(db, email)
            log_event(db, "receiver_updated", f"Destinatario attivo impostato a {email}")
            return {"status": "success", "receiver": email}
        finally:
            db.close()

    @app.delete("/api/receivers/{email}")
    async def api_delete_receiver(email: str):
        db = SessionLocal()
        try:
            fallback = settings.default_receiver_email or settings.sender_email or "owner@example.com"
            set_active_receiver(db, fallback)
            log_event(db, "receiver_reset", f"Destinatario resettato da {email} a {fallback}")
            return {"status": "success", "receiver": fallback}
        finally:
            db.close()

    @app.get("/webhook")
    async def webhook_info():
        return {
            "message": "Webhook endpoint attivo. Usa POST per inviare i payload del form.",
            "methods": ["GET", "POST", "OPTIONS"],
        }

    @app.options("/webhook", status_code=204)
    async def webhook_options():
        return None

    @app.post("/webhook")
    async def receive_form(request: Request):
        try:
            payload = await request.json()
        except Exception:
            form_data = await request.form()
            payload = dict(form_data)

        source = detect_source(request, payload)
        normalized = normalize_payload(payload)
        initial_status = "new"
        initial_missing_fields: list[str] = []
        initial_review_summary = "Lead acquisito. In attesa della revisione Hermes."
        initial_suggested_action = "run_reviewer"

        db = SessionLocal()
        try:
            duplicate_lead = find_duplicate_lead(db, source, payload)
            if duplicate_lead:
                latest_quote = sorted(duplicate_lead.quotes, key=lambda quote: (quote.version, quote.id))[-1] if duplicate_lead.quotes else None
                log_event(
                    db,
                    "webhook_duplicate",
                    f"Webhook duplicato ignorato per {duplicate_lead.client_name or 'cliente sconosciuto'}",
                    lead_id=duplicate_lead.id,
                )
                return {
                    "status": "duplicate",
                    "duplicate": True,
                    "lead_id": duplicate_lead.id,
                    "lead_status": duplicate_lead.status,
                    "quote_id": latest_quote.id if latest_quote else None,
                    "quote_status": latest_quote.status if latest_quote else None,
                    "missing_fields": loads_json(duplicate_lead.missing_fields, []),
                    "review_summary": duplicate_lead.review_summary,
                    "suggested_action": duplicate_lead.suggested_action,
                }

            lead = Lead(
                source=source,
                client_name=normalized.get("client_name"),
                client_email=normalized.get("client_email"),
                client_phone=normalized.get("client_phone"),
                job_type=normalized.get("job_type"),
                description=normalized.get("description"),
                raw_payload=dumps_json(payload),
                normalized_payload=dumps_json(normalized),
                status=initial_status,
                missing_fields=dumps_json(initial_missing_fields),
                review_summary=initial_review_summary,
                suggested_action=initial_suggested_action,
            )
            db.add(lead)
            db.commit()
            db.refresh(lead)
            log_event(db, "lead_created", f"Nuova richiesta ricevuta per {lead.client_name or 'cliente sconosciuto'}", lead_id=lead.id)

            return {
                "status": "success",
                "lead_id": lead.id,
                "lead_status": lead.status,
                "quote_id": None,
                "quote_status": None,
                "missing_fields": initial_missing_fields,
                "review_summary": initial_review_summary,
                "suggested_action": initial_suggested_action,
            }
        finally:
            db.close()
