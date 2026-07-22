"""Simple app settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    upload_dir: str = "data/uploads"
    api_host: str = "0.0.0.0"
    api_port: int = 8010

    @property
    def upload_path(self) -> Path:
        path = ROOT_DIR / self.upload_dir
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def has_gemini(self) -> bool:
        return bool(
            self.gemini_api_key
            and self.gemini_api_key != "paste-your-gemini-key-here"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
