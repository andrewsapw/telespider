from typing import AsyncGenerator

from pyrogram.types import Message
from pyrogram.errors.exceptions.bad_request_400 import UsernameNotOccupied

from telespider.config import settings
from telespider.app import app
from telespider.console import logger

CHANNELS = settings.ENTRYPOINT_CHANNELS.split(",")


async def parse_channel(
    channel_name: str, limit: int = settings.MAX_PER_CHANNEL
) -> AsyncGenerator[Message, None]:
    try:
        async for message in app.get_chat_history(channel_name, limit=limit):
            yield message
    except UsernameNotOccupied:
        logger.error(f"Skipping {channel_name} - does not exists")
        return


async def search_message(
    channel_name: str, query: str
) -> AsyncGenerator[Message, None]:
    async for message in app.search_messages(channel_name, query=query):
        yield message
