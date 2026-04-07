import logging
import os
import sys

from telegram import Update
from telegram.ext import ApplicationBuilder

from config import Config

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("KanhaManager")

if not Config.BOT_TOKEN:
    log.error("BOT_TOKEN not set! Exiting.")
    sys.exit(1)

if not Config.DATABASE_URL:
    log.error("DATABASE_URL not set! Exiting.")
    sys.exit(1)

app = ApplicationBuilder().token(Config.BOT_TOKEN).workers(Config.WORKERS).build()
