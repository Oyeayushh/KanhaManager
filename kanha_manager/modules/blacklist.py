import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode

from helpers import admin_only, is_admin, is_sudo
from database import Session, BlacklistWord

log = logging.getLogger("KanhaManager.Blacklist")

@admin_only
async def add_blacklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not context.args:
        await update.message.reply_text("Usage: /blacklist <word>")
        return

    words = [w.lower() for w in context.args]
    s = Session()
    added = []
    for word in words:
        if not s.query(BlacklistWord).filter_by(chat_id=chat.id, word=word).first():
            s.add(BlacklistWord(chat_id=chat.id, word=word))
            added.append(word)
    s.commit()
    s.close()

    if added:
        await update.message.reply_text(
            f"✅ Added to blacklist: {', '.join(f'<code>{w}</code>' for w in added)}",
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text("ℹ️ All words already in blacklist.")

@admin_only
async def remove_blacklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not context.args:
        await update.message.reply_text("Usage: /unblacklist <word>")
        return

    word = context.args[0].lower()
    s = Session()
    entry = s.query(BlacklistWord).filter_by(chat_id=chat.id, word=word).first()
    if entry:
        s.delete(entry)
        s.commit()
        await update.message.reply_text(f"✅ <code>{word}</code> removed from blacklist.", parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(f"❌ <code>{word}</code> not in blacklist.", parse_mode=ParseMode.HTML)
    s.close()

async def blacklist_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    s = Session()
    words = s.query(BlacklistWord).filter_by(chat_id=chat.id).all()
    s.close()

    if not words:
        await update.message.reply_text("📋 No blacklisted words.")
        return

    text = "🚫 <b>Blacklisted Words:</b>\n"
    for w in words:
        text += f"• <code>{w.word}</code>\n"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def check_blacklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not msg.text or not user:
        return
    if is_sudo(user.id):
        return
    if await is_admin(update, user.id):
        return

    text_lower = msg.text.lower()
    s = Session()
    words = s.query(BlacklistWord).filter_by(chat_id=chat.id).all()
    s.close()

    for entry in words:
        if entry.word in text_lower:
            try:
                await msg.delete()
                await context.bot.send_message(
                    chat.id,
                    f"⚠️ Message deleted — contained a blacklisted word: <code>{entry.word}</code>",
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                log.error(f"Blacklist delete error: {e}")
            return

def register(app):
    app.add_handler(CommandHandler("blacklist", blacklist_list))
    app.add_handler(CommandHandler("addblacklist", add_blacklist))
    app.add_handler(CommandHandler("unblacklist", remove_blacklist))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_blacklist))
