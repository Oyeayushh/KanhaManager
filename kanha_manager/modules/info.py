import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode

from helpers import get_target_user, mention_html, is_sudo

log = logging.getLogger("KanhaManager.Info")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat

    if msg.reply_to_message and msg.reply_to_message.from_user:
        user = msg.reply_to_message.from_user
    elif context.args:
        user_id, _ = await get_target_user(update, context)
        if not user_id:
            await msg.reply_text("❌ Could not find that user.")
            return
        try:
            user = await context.bot.get_chat(user_id)
        except Exception:
            await msg.reply_text("❌ Could not fetch user info.")
            return
    else:
        user = update.effective_user

    member = None
    if chat.type != "private":
        try:
            member = await chat.get_member(user.id)
        except Exception:
            pass

    text = (
        f"👤 <b>User Info</b>\n\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"📛 <b>Name:</b> {mention_html(user.id, user.first_name)}\n"
    )
    if hasattr(user, 'last_name') and user.last_name:
        text += f"📛 <b>Last Name:</b> {user.last_name}\n"
    if hasattr(user, 'username') and user.username:
        text += f"🔗 <b>Username:</b> @{user.username}\n"
    if is_sudo(user.id):
        text += f"🌟 <b>Role:</b> Bot Sudo/Owner\n"
    if member:
        text += f"📊 <b>Status:</b> {member.status}\n"

    await msg.reply_text(text, parse_mode=ParseMode.HTML)

async def chat_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    try:
        count = await chat.get_member_count()
    except Exception:
        count = "Unknown"

    text = (
        f"💬 <b>Chat Info</b>\n\n"
        f"🆔 <b>ID:</b> <code>{chat.id}</code>\n"
        f"📛 <b>Name:</b> {chat.title}\n"
        f"🔗 <b>Username:</b> @{chat.username if chat.username else 'None'}\n"
        f"👥 <b>Members:</b> {count}\n"
        f"📁 <b>Type:</b> {chat.type}\n"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

def register(app):
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("chatinfo", chat_info))
    app.add_handler(CommandHandler("id", info))
