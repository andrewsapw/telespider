from typing import AsyncGenerator, List, Optional, NamedTuple

import uvloop
from pyrogram.client import Client
from pyrogram.types import Chat, Message

from telespider.config import settings
from telespider.config import ROOT_DIR
from telespider.console import console


class ParsingProgress(NamedTuple):
    message: Message
    channels_parsed: int
    channels_remaining: int


SESSION_DIR = ROOT_DIR.parent / "sessions"
CHANNELS = settings.ENTRYPOINT_CHANNELS.split(",")

app = Client(
    name=settings.APP_NAME,
    api_id=settings.API_ID,
    api_hash=settings.API_HASH,
    workdir=SESSION_DIR,
)


async def parse_channel(
    channel_name: str, limit: int = settings.MAX_PER_CHANNEL
) -> AsyncGenerator[Message, None]:
    async for message in app.get_chat_history(channel_name, limit=limit):
        yield message


async def parse_channels(
    channels: List[str] = CHANNELS,
) -> AsyncGenerator[ParsingProgress, None]:
    channels = set(channels)
    parsed_channels = set()

    while channels:
        channel = channels.pop()

        async for message in parse_channel(channel_name=channel):
            if message.text is None and message.caption is None:
                continue

            linked_channels = extract_channels(message)
            linked_channels = filter(
                lambda x: x not in parsed_channels, linked_channels
            )

            for linked_channel in linked_channels:
                channels.add(linked_channel)

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
    async with app:
        with console.status("Working...") as status:
            n_parsed = 0
            async for p in parse_channels(CHANNELS):
                m = p.message

                if n_parsed % 100 == 0:
                    status.update(
                        f"Parsed channels: {p.channels_parsed} - remaining {p.channels_remaining} : "
                        f"total messages {n_parsed} | Searching for [bold]{text}[/bold] in {m.chat.username}"
                    )

                # update task description
                message_text = m.text or m.caption
                if text in message_text.lower():
                    console.print(f"[bold]{m.chat.username}[/bold] - {m.text}")

                n_parsed += 1


if __name__ == "__main__":
    uvloop.install()
    app.run(search_text("сарапул"))
