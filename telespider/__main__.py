from functools import wraps
from typing import Optional
import asyncio
import uvloop

import click

from telespider import scrapper
from telespider.config import settings, ROOT_DIR
from telespider.app import App
from telespider.console import console

uvloop.install()


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(f(*args, **kwargs))

    return wrapper


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.option(
    "--workdir", type=click.Path(exists=True), default=ROOT_DIR.parent / "sessions"
)
@click.pass_context
def cli(ctx, debug, workdir):
    app = App(
        name=settings.APP_NAME,
        api_id=settings.API_ID,
        api_hash=settings.API_HASH,
        workdir=workdir,
    )
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug
    ctx.obj["APP"] = app.app


@cli.command(name="search", help="Search word or user mentions in channels messages")
@click.option("--explore/--no-explore", default=True, help="Auto explore new channels")
@click.option("--silent", is_flag=True, default=False, help="Suppress all output")
@click.option("--word", "-w", type=str, required=False)
@click.option("--user", "-u", type=str, required=False)
@click.option(
    "-n", type=int, default=1000, help="Number of messages to parse per channel"
)
@click.pass_context
@coro
async def search_word(
    ctx, explore: bool, silent: bool, word: Optional[str], user: Optional[str], n: int
):
    if word is None and user is None:
        raise click.BadOptionUsage(
            option_name="word | user", message="word or user must be specified"
        )

    app = ctx.obj["APP"]

    settings.MAX_PER_CHANNEL = n
    settings.AUTO_EXPLORE_CHANNELS = explore
    console.quiet = silent

    await app.start()
    try:
        if word is not None:
            async for _ in scrapper.search_text(app=app, text=word):
                ...
        elif user is not None:
            async for _ in scrapper.search_mentions(app=app, mention=user):
                ...
    finally:
        await app.stop(block=False)


@cli.command(name="explore-channels", help="Explore channels mentions")
@click.option("--silent", is_flag=True, default=False, help="Suppress all output")
@click.option(
    "-n", type=int, default=1000, help="Number of messages to parse per channel"
)
@click.pass_context
@coro
async def explore_channels(ctx, silent: bool, n: int):
    settings.MAX_PER_CHANNEL = n
    console.quiet = silent

    app = ctx.obj["APP"]

    await app.start()
    try:
        async for i in scrapper.explore_channels(app=app):
            source_channel = i.source_channel
            console.print(f"{source_channel}: {i.mentions}")
    finally:
        await app.stop(block=False)


if __name__ == "__main__":
    cli()
