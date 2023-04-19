from typing import AsyncGenerator, List, Optional
from collections import deque

from pyrogram.types import Chat, Message
from pyrogram.enums import MessageEntityType
from rich.panel import Panel

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

            yield ParsingProgress(message, len(parsed_channels), len(channels))

            if not settings.AUTO_EXPLORE_CHANNELS:
                continue

            linked_channels = extract_channels(message)
            linked_channels = filter(
                lambda x: x not in parsed_channels and x not in channels,
                linked_channels,
            )

            for linked_channel in linked_channels:
                channels.append(linked_channel)

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


async def search_text(text: str) -> AsyncGenerator[Message, None]:
    """Search for text in messages"""

    with console.status("Working...") as status:
        n_parsed = 0
        async for p in parse_channels(channels=CHANNELS):
            m = p.message

            if n_parsed % 100 == 0:
                status.update(
                    f"Parsed: {p.channels_parsed} ch. {n_parsed} messages  - remaining {p.channels_remaining} ch."  # noqa: E501
                    f" | Searching for word [bold]{text}[/bold] in {m.chat.username}"
                )

            # update task description
            message_text = m.text or m.caption
            if text in message_text.lower():
                # console.print(f"[bold]{m.chat.username}[/bold] - {message_text}")
                console.print(
                    Panel(
                        message_text,
                        title=f"{m.chat.username} ({m.date.strftime('%Y-%m-%d')})",
                    )
                )
                yield m

            n_parsed += 1


async def search_mentions(mention: str) -> AsyncGenerator[Message, None]:
    """Search for mentions in messages"""
    if mention.startswith("@"):
        mention = mention[1:]

    with console.status("Working...") as status:
        n_parsed = 0
        async for p in parse_channels(channels=CHANNELS):
            m = p.message

            if n_parsed % 100 == 0:
                status.update(
                    f"Parsed: {p.channels_parsed} ch. {n_parsed} messages  - remaining {p.channels_remaining} ch."  # noqa: E501
                    f" | Searching for mention of [bold]{mention}[/bold] in {m.chat.username}"
                )

            # update task description
            message_text = m.text or m.caption
            if m.entities is None:
                continue

            for message_mention in m.entities:
                if message_mention.type in (
                    MessageEntityType.MENTION,
                    MessageEntityType.TEXT_MENTION,
                ):
                    mentioned = message_text[
                        message_mention.offset
                        + 1 : message_mention.offset
                        + message_mention.length
                    ]

                    if mentioned == mention:
                        console.print(
                            Panel(
                                message_text,
                                title=f"{m.chat.username} ({m.date.strftime('%Y-%m-%d')})",
                            )
                        )
                        yield m

            n_parsed += 1
