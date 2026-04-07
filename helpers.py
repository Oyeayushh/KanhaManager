import logging
from functools import wraps
from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from config import Config

log = logging.getLogger("KanhaManager.Helpers")

def mention_html(user_id, name):
    return f'<a href="tg://user?id={user_id}">{name}</a>'

def is_sudo(user_id):
    return user_id == Config.OWNER_ID or user_id in Config.SUDO_USERS

async def get_member(chat, user_id):
    try:
        return await chat.get_member(user_id)
    except Exception:
        return None

async def is_admin(update: Update, user_id: int) -> bool:
    member = await get_member(update.effective_chat, user_id)
    if not member:
        return False
    return member.status in (ChatMember.ADMINISTRATOR, ChatMember.OWNER)

# ─── DECORATORS ───────────────────────────────────────────

def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        chat = update.effective_chat
        if not user:
            return
        if chat.type == "private":
            await update.message.reply_text("This command only works in groups.")
            return
        if is_sudo(user.id):
            return await func(update, context, *args, **kwargs)
        member = await get_member(chat, user.id)
        if member and member.status in (ChatMember.ADMINISTRATOR, ChatMember.OWNER):
            return await func(update, context, *args, **kwargs)
        await update.message.reply_text("⚠️ You need to be an admin to use this command.")
    return wrapper

def owner_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not user or not is_sudo(user.id):
            await update.message.reply_text("⛔ This command is only for the bot owner.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

async def get_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Returns (user_id, first_name) from reply or args."""
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.from_user:
        u = msg.reply_to_message.from_user
        return u.id, u.first_name
    if context.args:
        arg = context.args[0]
        if arg.startswith("@"):
            arg = arg[1:]
        try:
            uid = int(arg)
            return uid, str(uid)
        except ValueError:
            try:
                user = await context.bot.get_chat(arg)
                return user.id, user.first_name or arg
            except Exception:
                return None, None
    return None, None
