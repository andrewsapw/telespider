from typing import Optional
import uvloop

import click

from telespider import scrapper
from telespider.app import app

uvloop.install()
# app.run(search_text("путин"))


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.pass_context
def cli(ctx, debug):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)

    ctx.obj["DEBUG"] = debug


@cli.command(name="search")
@click.option("--word", "-w", type=str, required=False)
@click.option("--user", "-u", type=str, required=False)
def search_word(word: Optional[str], user: Optional[str]):
    if word is None and user is None:
        raise click.BadOptionUsage(
            option_name="word | user", message="word or user must be specified"
        )

    app.run(scrapper.search_text(word))


if __name__ == "__main__":
    cli()
