import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode

from helpers import admin_only
from database import Session, Note

log = logging.getLogger("KanhaManager.Notes")

@admin_only
async def save_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.effective_message

    if not context.args:
        await msg.reply_text("Usage: /save <name> <content>\nOr reply to a message with /save <name>")
        return

    name = context.args[0].lower()

    if msg.reply_to_message:
        content = msg.reply_to_message.text or msg.reply_to_message.caption or ""
    elif len(context.args) > 1:
        content = " ".join(context.args[1:])
    else:
        await msg.reply_text("❌ Provide content or reply to a message.")
        return

    s = Session()
    existing = s.query(Note).filter_by(chat_id=chat.id, name=name).first()
    if existing:
        existing.content = content
    else:
        s.add(Note(chat_id=chat.id, name=name, content=content))
    s.commit()
    s.close()
    await msg.reply_text(f"✅ Note <b>#{name}</b> saved!", parse_mode=ParseMode.HTML)

async def get_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.effective_message

    if not context.args:
        await msg.reply_text("Usage: /get <name>")
        return

    name = context.args[0].lower()
    s = Session()
    note = s.query(Note).filter_by(chat_id=chat.id, name=name).first()
    s.close()

    if not note:
        await msg.reply_text(f"❌ No note found with name <b>#{name}</b>.", parse_mode=ParseMode.HTML)
        return

    await msg.reply_text(note.content, parse_mode=ParseMode.HTML)

async def notes_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    s = Session()
    all_notes = s.query(Note).filter_by(chat_id=chat.id).all()
    s.close()

    if not all_notes:
        await update.message.reply_text("📝 No notes saved in this group.")
        return

    text = "📋 <b>Saved Notes:</b>\n"
    for note in all_notes:
        text += f"• #{note.name}\n"
    text += "\nUse /get <name> to retrieve a note."
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

@admin_only
async def clear_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not context.args:
        await update.message.reply_text("Usage: /clear <name>")
        return

    name = context.args[0].lower()
    s = Session()
    note = s.query(Note).filter_by(chat_id=chat.id, name=name).first()
    if note:
        s.delete(note)
        s.commit()
        await update.message.reply_text(f"✅ Note <b>#{name}</b> deleted.", parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(f"❌ No note named <b>#{name}</b>.", parse_mode=ParseMode.HTML)
    s.close()

async def hash_get(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle #notename messages"""
    msg = update.effective_message
    chat = update.effective_chat
    text = msg.text or ""
    words = text.split()
    for word in words:
        if word.startswith("#") and len(word) > 1:
            name = word[1:].lower()
            s = Session()
            note = s.query(Note).filter_by(chat_id=chat.id, name=name).first()
            s.close()
            if note:
                await msg.reply_text(note.content, parse_mode=ParseMode.HTML)
                return

def register(app):
    app.add_handler(CommandHandler("save", save_note))
    app.add_handler(CommandHandler("get", get_note))
    app.add_handler(CommandHandler("notes", notes_list))
    app.add_handler(CommandHandler("saved", notes_list))
    app.add_handler(CommandHandler("clear", clear_note))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"#\w+"), hash_get))
