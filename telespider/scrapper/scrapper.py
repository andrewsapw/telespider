from typing import AsyncGenerator, List, Set
from collections import deque

from pyrogram.client import Client
from pyrogram.enums import MessageEntityType

from telespider.config import settings
from .types import ExploreChannelsProgress, MessageParsingProgress
from .channel import parse_channel, extract_channels

CHANNELS = settings.ENTRYPOINT_CHANNELS.split(",")


async def parse_messages(
    app: Client,
    channels: List[str] = CHANNELS,
) -> AsyncGenerator[MessageParsingProgress, None]:
    channels_queue: deque = deque(set(channels))
    parsed_channels: Set[str] = set()

    while channels_queue:
        channel = channels_queue.popleft()

        async for message in parse_channel(app=app, channel_name=channel):
            if message.text is None and message.caption is None:
                continue

            yield MessageParsingProgress(
                message, len(parsed_channels), len(channels_queue)
            )

            if not settings.AUTO_EXPLORE_CHANNELS:
                continue

            linked_channels = extract_channels(message)
            linked_channels = list(
                filter(
                    lambda x: x not in parsed_channels and x not in channels_queue,
                    linked_channels,
                )
            )

            for linked_channel in linked_channels:
                channels_queue.append(linked_channel)

        parsed_channels.add(channel)


async def explore_channels(
    app: Client,
    channels: List[str] = CHANNELS,
) -> AsyncGenerator[ExploreChannelsProgress, None]:
    channels_queue: deque = deque(set(channels))
    parsed_channels = set()

    while channels_queue:
        channel = channels_queue.popleft()
        channel_mentions = set()
        async for message in parse_channel(app=app, channel_name=channel):
            linked_channels = extract_channels(message)
            linked_channels = list(
                filter(
                    lambda x: x not in parsed_channels and x not in channels_queue,
                    linked_channels,
                )
            )

            if not linked_channels:
                continue

            for linked_channel in linked_channels:
                channels_queue.append(linked_channel)
                channel_mentions.add(linked_channel)

        yield ExploreChannelsProgress(
            source_channel=channel, mentions=list(channel_mentions)
        )

        parsed_channels.add(channel)


async def search_text(
    app: Client, text: str, channels: List[str]
) -> AsyncGenerator[MessageParsingProgress, None]:
    """Search for text in messages"""

    async for p in parse_messages(app=app, channels=channels):
        m = p.message

        # update task description
        message_text = m.text or m.caption
        if text in message_text.lower():
            yield p


async def search_mentions(
    app: Client, mention: str, channels: List[str]
) -> AsyncGenerator[MessageParsingProgress, None]:
    """Search for mentions in messages"""
    if mention.startswith("@"):
        mention = mention[1:]

    async for p in parse_messages(app=app, channels=channels):
        m = p.message

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
                    yield p
