import logging
from rich.console import Console
from .config import settings

logger = logging.getLogger("__root__")
logger.setLevel(logging.CRITICAL)

console = Console(quiet=settings.SILENT)
