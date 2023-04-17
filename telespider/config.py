from pathlib import Path

from pydantic import BaseSettings

ROOT_DIR = Path(__file__).parent


class Settings(BaseSettings):
    APP_NAME: str = "Scrapppppppp"

    API_HASH: str
    API_ID: str

    ENTRYPOINT_CHANNELS: str  # comma separated list of channels
    MAX_PER_CHANNEL: int = 1000  # maximum number of messages to parse per channel

    # parse .env
    class Config:
        env_file = ROOT_DIR.parent / ".env"


settings = Settings()
