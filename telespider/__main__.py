from functools import wraps
from typing import Optional
import asyncio
import uvloop

import click

from telespider import scrapper
from telespider.config import settings
from telespider.app import app
from telespider.console import console

uvloop.install()


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(f(*args, **kwargs))

    return wrapper


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.pass_context
def cli(ctx, debug):
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug


@cli.command(name="search")
@click.option("--explore/--no-explore", default=True, help="Auto explore new channels")
@click.option("--silent", is_flag=True, default=False, help="Suppress all output")
@click.option("--word", "-w", type=str, required=False)
@click.option("--user", "-u", type=str, required=False)
@click.option(
    "-n", type=int, default=1000, help="Number of messages to parse per channel"
)
@coro
async def search_word(
    explore: bool, silent: bool, word: Optional[str], user: Optional[str], n: int
):
    if word is None and user is None:
        raise click.BadOptionUsage(
            option_name="word | user", message="word or user must be specified"
        )

    settings.MAX_PER_CHANNEL = n
    settings.AUTO_EXPLORE_CHANNELS = explore
    console.quiet = silent

    await app.start()
    try:
        if word is not None:
            async for _ in scrapper.search_text(word):
                ...
        elif user is not None:
            async for _ in scrapper.search_mentions(user):
                ...
    finally:
        await app.stop(block=False)


if __name__ == "__main__":
    cli()
