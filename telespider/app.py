from typing import AsyncGenerator, AsyncIterator, List
from contextlib import asynccontextmanager

from pyrogram.client import Client
from pyrogram.types import Message

from telespider.config import ROOT_DIR
from telespider.scrapper import explore_channels, search_mentions, search_text
from telespider.scrapper.types import ExploreChannelsProgress

SESSION_DIR = ROOT_DIR.parent / "sessions"


class App:
    def __init__(self, name: str, api_id: str, api_hash: str, workdir: str) -> None:
        self._client = Client(
            name=name,
            api_id=api_id,
            api_hash=api_hash,
            workdir=workdir,
            no_updates=True,
        )

    @asynccontextmanager
    async def session(self) -> AsyncIterator[Client]:
        await self._client.start()
        try:
            yield self._client
        finally:
            await self._client.stop(block=False)

    async def search_mentions(
        self, mention: str, channels: List[str]
    ) -> AsyncGenerator[Message, None]:
        async with self.session() as app:
            async for i in search_mentions(app=app, mention=mention, channels=channels):
                yield i

    async def explore_channels(
        self,
        channels: List[str],
    ) -> AsyncGenerator[ExploreChannelsProgress, None]:
        async with self.session() as app:
            async for i in explore_channels(app=app, channels=channels):
                yield i

    async def search_text(
        self, text: str, channels: List[str]
    ) -> AsyncGenerator[Message, None]:
        async with self.session() as app:
            async for i in search_text(app=app, text=text, channels=channels):
                yield i
