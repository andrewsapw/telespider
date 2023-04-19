from typing import Optional

from rich.table import Table
from rich.console import Group

from .types import ParsingProgress


def update_table_result(
    n_parsed: int,
    search_title: str,
    search_value: str,
    table: Table,
    progress: Optional[ParsingProgress] = None,
):
    if progress is None:
        return Group(
            table,
            (
                f"Parsed: {progress.channels_parsed} ch. "
                f"{n_parsed} messages  - remaining {progress.channels_remaining} ch."
                f" | Searching for {search_title} of [bold]{search_value}[/bold] "
                f"in {progress.message.chat.username}"
            ),
        )

    table.add_row(
        f"{progress.message.chat.username}",
        f"{progress.message.date}",
        f"{progress.message.text}",
    )
    return Group(
        table,
        (
            f"Parsed: {progress.channels_parsed} ch. "
            f"{n_parsed} messages  - remaining {progress.channels_remaining} ch."
            f" | Searching for {search_title} of [bold]{search_value}[/bold] "
            f"in {progress.message.chat.username}"
        ),
    )
