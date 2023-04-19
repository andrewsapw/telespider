from typing import AsyncGenerator, List, Optional
from collections import deque

from pyrogram.types import Chat, Message

from telespider.config import settings
from telespider.console import console
from .types import ParsingProgress
from .channel import parse_channel

CHANNELS = settings.ENTRYPOINT_CHANNELS.split(",")


async def parse_channels(
    channels: List[str] = CHANNELS,
) -> AsyncGenerator[ParsingProgress, None]:
    channels: deque = deque(set(channels))
    parsed_channels = set()

    while channels:
        channel = channels.popleft()

        async for message in parse_channel(channel_name=channel):
            if message.text is None and message.caption is None:
                continue

            linked_channels = extract_channels(message)
            linked_channels = filter(
                lambda x: x not in parsed_channels and x not in channels,
                linked_channels,
            )

            for linked_channel in linked_channels:
                channels.append(linked_channel)

            yield ParsingProgress(message, len(parsed_channels), len(channels))

        parsed_channels.add(channel)


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
        for entity in message.entities:
            if entity.type == "mention":
                linked_channels.append(entity.user.username)

    return linked_channels


async def search_text(text: str):
    """Search for text in messages"""

    with console.status("Working...") as status:
        n_parsed = 0
        async for p in parse_channels(channels=CHANNELS):
            m = p.message

            if n_parsed % 100 == 0:
                status.update(
                    f"Parsed channels: {p.channels_parsed} - remaining {p.channels_remaining} : "
                    f"total messages {n_parsed} | Searching for [bold]{text}[/bold] in {m.chat.username}"
                )

            # update task description
            message_text = m.text or m.caption
            if text in message_text.lower():
                console.print(f"[bold]{m.chat.username}[/bold] - {message_text}")

            n_parsed += 1

    return


async def search_mentions(mention: str):
    """Search for mentions in messages"""

    with console.status("Working...") as status:
        n_parsed = 0
        async for p in parse_channels(channels=CHANNELS):
            m = p.message

            if n_parsed % 100 == 0:
                status.update(
                    f"Parsed channels: {p.channels_parsed} - remaining {p.channels_remaining} : "
                    f"total messages {n_parsed} | Searching for [bold]{mention}[/bold] in {m.chat.username}"
                )

            # update task description
            message_text = m.text or m.caption
            if m.entities is None:
                continue

            for message_mention in m.entities:
                if (
                    message_mention.type == "mention"
                    and message_mention.user.username == mention
                ):
                    console.print(f"[bold]{m.chat.username}[/bold] - {message_text}")

            n_parsed += 1

    return
