from typing import AsyncGenerator

from pyrogram.types import Message

from telespider.config import settings
from telespider.app import app

CHANNELS = settings.ENTRYPOINT_CHANNELS.split(",")


async def parse_channel(
    channel_name: str, limit: int = settings.MAX_PER_CHANNEL
) -> AsyncGenerator[Message, None]:
    async for message in app.get_chat_history(channel_name, limit=limit):
        yield message


async def search_message(
    channel_name: str, query: str
) -> AsyncGenerator[Message, None]:
    async for message in app.search_messages(channel_name, query=query):
        yield message


# async def explore_channels(source_channel: str) -> AsyncGenerator[Message, None]:
# async for message in app.search_messages(channel_name, query=query):
# yield message
