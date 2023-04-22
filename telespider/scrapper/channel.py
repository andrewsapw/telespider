from typing import AsyncGenerator, List, Optional

from pyrogram.types import Message, Chat
from pyrogram.errors.exceptions.bad_request_400 import (
    UsernameNotOccupied,
    UsernameInvalid,
)

from pyrogram.enums import MessageEntityType

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
    except (UsernameNotOccupied, UsernameInvalid):
        logger.error(f"Skipping {channel_name} - does not exists or invalid")
        return


async def search_message(
    channel_name: str, query: str
) -> AsyncGenerator[Message, None]:
    async for message in app.search_messages(channel_name, query=query):
        yield message


def extract_channels(message: Message) -> List[str]:
    linked_channels = []
    forwarded_from: Optional[Chat] = message.forward_from_chat
    if forwarded_from is not None:
        if (
            forwarded_from.username is not None
            and not forwarded_from.is_restricted
            and not forwarded_from.is_scam
            and not forwarded_from.is_fake
        ):
            linked_channels.append(forwarded_from.username)

    # find mentions in message text
    if message.entities is not None:
        message_text = message.text or message.caption
        for entity in message.entities:
            if entity.type in (
                MessageEntityType.TEXT_MENTION,
                MessageEntityType.MENTION,
            ):
                # entity.offset + 1 to remove `@` before mention
                mentioned = message_text[
                    entity.offset + 1 : entity.offset + entity.length
                ]
                linked_channels.append(mentioned)

    return linked_channels
