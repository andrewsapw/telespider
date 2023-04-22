from pyrogram.client import Client

from telespider.config import ROOT_DIR

SESSION_DIR = ROOT_DIR.parent / "sessions"


class App:
    def __init__(self, name: str, api_id: str, api_hash: str, workdir: str) -> None:
        self.app = Client(name=name, api_id=api_id, api_hash=api_hash, workdir=workdir)
