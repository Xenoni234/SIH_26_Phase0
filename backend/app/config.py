"""Environment-driven application settings (Pydantic v2)."""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "/app/.env"), env_file_encoding="utf-8", extra="ignore"
    )

    # --- App ---
    app_env: str = "dev"
    log_level: str = "INFO"
    topology_path: str = "/app/data/topology/vasai.yaml"
    # Comma-separated allowed CORS origins (Vite dev server by default).
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    # Regex allowing any localhost port in dev (Vite may pick 5174, 5175, …).
    cors_origin_regex: str = r"^http://(localhost|127\.0\.0\.1):\d+$"
    # Populate Postgres from the topology on startup (idempotent).
    seed_on_startup: bool = True

    # --- RailRadar (external prototype source; NOT RTIS) ---
    railradar_api_key: str = ""
    railradar_base_url: str = "https://api.railradar.in/v1"
    railradar_train_numbers: str = ""  # comma-separated (optional per-train live)
    railradar_cache_ttl: int = 300
    railradar_station_code: str = "BSR"   # Vasai Road — station board source
    railradar_board_ttl: int = 900        # cache the board 15 min (respect 50/day)

    # --- Live simulation (Phase 2) ---
    sim_tick_seconds: float = 1.0         # broadcast cadence
    sim_speed: float = 20.0               # sim-time acceleration (20x real time)
    sim_window_minutes: int = 45          # trains within +/- this window are "around Vasai"
    sim_max_trains: int = 40              # cap for a legible view
    sim_synthetic_freight: int = 4        # synthetic goods rakes (real boards omit freight)

    # --- Database ---
    postgres_user: str = "vasai"
    postgres_password: str = "vasai"
    postgres_db: str = "vasai_twin"
    postgres_host: str = "db"
    postgres_port: int = 5432

    # --- Redis ---
    redis_host: str = "redis"
    redis_port: int = 6379

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    @property
    def railradar_enabled(self) -> bool:
        """Live RailRadar is used only when a key is present; else fixtures."""
        return bool(self.railradar_api_key.strip())

    @property
    def railradar_train_list(self) -> list[str]:
        return [t.strip() for t in self.railradar_train_numbers.split(",") if t.strip()]

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
