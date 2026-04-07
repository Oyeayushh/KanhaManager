import logging
import os
import sys

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from config import Config

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("KanhaManager")

# Check जरूरी variables
if not Config.BOT_TOKEN:
    log.error("BOT_TOKEN not set! Exiting.")
    sys.exit(1)

if not Config.DATABASE_URL:
    log.error("DATABASE_URL not set! Exiting.")
    sys.exit(1)

# ✅ FIXED LINE (workers removed)
app = ApplicationBuilder().token(Config.BOT_TOKEN).build()


# ---------------- COMMANDS ---------------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Bot is working!")

# Add handlers
app.add_handler(CommandHandler("start", start))


# ---------------- RUN BOT ---------------- #

if __name__ == "__main__":
    log.info("Bot started...")
    app.run_polling()