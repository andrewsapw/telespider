from typing import NamedTuple
from pyrogram.types import Message


class ParsingProgress(NamedTuple):
    message: Message
    channels_parsed: int
    channels_remaining: int


class ChannelInfo(NamedTuple):
    name: str
    size: int
