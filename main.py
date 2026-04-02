import smtplib

from app.runtime import create_runtime
from app.services import analyze_lead, normalize_payload
from app.utils import dumps_json, loads_json, parse_currency, parse_number

runtime = create_runtime(smtplib)

app = runtime.app
settings = runtime.settings
engine = runtime.engine
SessionLocal = runtime.SessionLocal
Config = runtime.Config
Lead = runtime.Lead
Quote = runtime.Quote
ActivityLog = runtime.ActivityLog

__all__ = [
    "app",
    "settings",
    "engine",
    "SessionLocal",
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
    "smtplib",
]
