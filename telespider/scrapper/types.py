from typing import List, NamedTuple
from pyrogram.types import Message


class MessageParsingProgress(NamedTuple):
    message: Message
    channels_parsed: int
    channels_remaining: int


class ExploreChannelsProgress(NamedTuple):
    source_channel: str
    mentions: List[str]


class ChannelInfo(NamedTuple):
    name: str
    size: int
