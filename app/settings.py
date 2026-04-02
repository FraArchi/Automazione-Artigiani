import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    environment: str
    database_url: str
    default_receiver_email: str
    sender_email: str
    sender_password: str
    public_base_url: str
    quote_output_dir: Path
    project_root: Path
    static_dir: Path
    email_enabled_default: bool

    @classmethod
    def from_env(cls) -> "Settings":
        project_root = Path(__file__).resolve().parent.parent
        database_url = os.environ.get("DATABASE_URL", "sqlite:///./local.db")
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        quote_output_dir = Path(os.environ.get("QUOTE_OUTPUT_DIR", "quotes"))
        if not quote_output_dir.is_absolute():
            quote_output_dir = project_root / quote_output_dir
        quote_output_dir.mkdir(parents=True, exist_ok=True)

        public_base_url = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/")
        email_enabled_default = os.environ.get("EMAIL_ENABLED", "false").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

        return cls(
            environment=os.environ.get("ENVIRONMENT", "development"),
            database_url=database_url,
            default_receiver_email=os.environ.get("DEFAULT_RECEIVER_EMAIL", ""),
            sender_email=os.environ.get("SENDER_EMAIL", ""),
            sender_password=os.environ.get("SENDER_PASSWORD", ""),
            public_base_url=public_base_url,
            quote_output_dir=quote_output_dir,
            project_root=project_root,
            static_dir=project_root / "static",
            email_enabled_default=email_enabled_default,
        )
