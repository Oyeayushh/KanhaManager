import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode

from helpers import admin_only
from database import Session, Filter

log = logging.getLogger("KanhaManager.Filters")

@admin_only
async def add_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.effective_message

    if not context.args:
        await msg.reply_text("Usage: /filter <keyword> <reply>\nOr reply to a message with /filter <keyword>")
        return

    keyword = context.args[0].lower()

    if msg.reply_to_message:
        reply = msg.reply_to_message.text or msg.reply_to_message.caption or ""
    elif len(context.args) > 1:
        reply = " ".join(context.args[1:])
    else:
        await msg.reply_text("❌ Provide a reply text or reply to a message.")
        return

    s = Session()
    existing = s.query(Filter).filter_by(chat_id=chat.id, keyword=keyword).first()
    if existing:
        existing.reply = reply
    else:
        s.add(Filter(chat_id=chat.id, keyword=keyword, reply=reply))
    s.commit()
    s.close()
    await msg.reply_text(f"✅ Filter for <code>{keyword}</code> added!", parse_mode=ParseMode.HTML)

@admin_only
async def stop_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not context.args:
        await update.message.reply_text("Usage: /stop <keyword>")
        return

    keyword = context.args[0].lower()
    s = Session()
    f = s.query(Filter).filter_by(chat_id=chat.id, keyword=keyword).first()
    if f:
        s.delete(f)
        s.commit()
        await update.message.reply_text(f"✅ Filter for <code>{keyword}</code> removed.", parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(f"❌ No filter found for <code>{keyword}</code>.", parse_mode=ParseMode.HTML)
    s.close()

async def filters_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    s = Session()
    all_filters = s.query(Filter).filter_by(chat_id=chat.id).all()
    s.close()

    if not all_filters:
        await update.message.reply_text("📋 No filters active in this group.")
        return

    text = "📋 <b>Active Filters:</b>\n"
    for f in all_filters:
        text += f"• <code>{f.keyword}</code>\n"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def check_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not msg.text:
        return

    text_lower = msg.text.lower()
    s = Session()
    all_filters = s.query(Filter).filter_by(chat_id=chat.id).all()
    s.close()

    for f in all_filters:
        if f.keyword in text_lower:
            await msg.reply_text(f.reply, parse_mode=ParseMode.HTML)
            return

def register(app):
    app.add_handler(CommandHandler("filter", add_filter))
    app.add_handler(CommandHandler("stop", stop_filter))
    app.add_handler(CommandHandler("filters", filters_list))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_filters))
