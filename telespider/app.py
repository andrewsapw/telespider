from pyrogram.client import Client

from telespider.config import settings
from telespider.config import ROOT_DIR

SESSION_DIR = ROOT_DIR.parent / "sessions"
app = Client(
    name=settings.APP_NAME,
    api_id=settings.API_ID,
    api_hash=settings.API_HASH,
    workdir=SESSION_DIR,
)
