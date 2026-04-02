from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import ActivityLog, Base, Config, Lead, Quote
from app.routes import register_routes
from app.services import analyze_lead, normalize_payload
from app.settings import Settings
from app.utils import dumps_json, loads_json, parse_currency, parse_number


@dataclass
class Runtime:
    app: FastAPI
    settings: Settings
    engine: Any
    SessionLocal: Any
    Config: type[Config]
    Lead: type[Lead]
    Quote: type[Quote]
    ActivityLog: type[ActivityLog]


def create_runtime(smtplib_module) -> Runtime:
    settings = Settings.from_env()
    engine_kwargs: dict[str, Any] = {}
    if settings.database_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}

    engine = create_engine(settings.database_url, **engine_kwargs)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    app = FastAPI(title="Automazione Artigiani")
    if settings.static_dir.exists():
        app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")

    register_routes(app, SessionLocal, settings, smtplib_module)

    return Runtime(
        app=app,
        settings=settings,
        engine=engine,
        SessionLocal=SessionLocal,
        Config=Config,
        Lead=Lead,
        Quote=Quote,
        ActivityLog=ActivityLog,
    )


__all__ = [
    "Runtime",
    "create_runtime",
    "Config",
    "Lead",
    "Quote",
    "ActivityLog",
    "dumps_json",
    "loads_json",
    "parse_currency",
    "parse_number",
    "normalize_payload",
    "analyze_lead",
]
