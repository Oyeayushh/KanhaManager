import logging
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode

from helpers import admin_only, is_admin, is_sudo
from database import Session, LockSetting

log = logging.getLogger("KanhaManager.Locks")

LOCK_TYPES = {
    "sticker": "sticker",
    "gif": "gif",
    "photo": "photo",
    "video": "video",
    "audio": "audio",
    "document": "document",
    "voice": "voice",
    "url": "url",
    "forward": "forward",
    "bot": "bot",
}

def get_lock_setting(chat_id):
    s = Session()
    setting = s.query(LockSetting).filter_by(chat_id=chat_id).first()
    if not setting:
        setting = LockSetting(chat_id=chat_id)
        s.add(setting)
        s.commit()
    s.close()
    return setting

@admin_only
async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not context.args or context.args[0] not in LOCK_TYPES:
        await update.message.reply_text(
            f"Usage: /lock <type>\n\nAvailable: {', '.join(LOCK_TYPES.keys())}"
        )
        return

    lock_type = context.args[0]
    s = Session()
    setting = s.query(LockSetting).filter_by(chat_id=chat.id).first()
    if not setting:
        setting = LockSetting(chat_id=chat.id)
        s.add(setting)
    setattr(setting, lock_type, True)
    s.commit()
    s.close()
    await update.message.reply_text(f"🔒 <b>{lock_type}</b> locked!", parse_mode=ParseMode.HTML)

@admin_only
async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not context.args or context.args[0] not in LOCK_TYPES:
        await update.message.reply_text(
            f"Usage: /unlock <type>\n\nAvailable: {', '.join(LOCK_TYPES.keys())}"
        )
        return

    lock_type = context.args[0]
    s = Session()
    setting = s.query(LockSetting).filter_by(chat_id=chat.id).first()
    if not setting:
        setting = LockSetting(chat_id=chat.id)
        s.add(setting)
    setattr(setting, lock_type, False)
    s.commit()
    s.close()
    await update.message.reply_text(f"🔓 <b>{lock_type}</b> unlocked!", parse_mode=ParseMode.HTML)

async def locks_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    setting = get_lock_setting(chat.id)
    text = "🔒 <b>Lock Status:</b>\n\n"
    for lt in LOCK_TYPES:
        status = "🔒" if getattr(setting, lt, False) else "🔓"
        text += f"{status} {lt}\n"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def check_locks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not user:
        return
    if is_sudo(user.id):
        return
    if await is_admin(update, user.id):
        return

    setting = get_lock_setting(chat.id)

    locked = False
    if setting.sticker and msg.sticker:
        locked = True
    elif setting.gif and msg.animation:
        locked = True
    elif setting.photo and msg.photo:
        locked = True
    elif setting.video and msg.video:
        locked = True
    elif setting.audio and msg.audio:
        locked = True
    elif setting.document and msg.document:
        locked = True
    elif setting.voice and msg.voice:
        locked = True
    elif setting.url and msg.text and ("http://" in msg.text or "https://" in msg.text):
        locked = True
    elif setting.forward and msg.forward_date:
        locked = True

    if locked:
        try:
            await msg.delete()
        except Exception as e:
            log.error(f"Lock delete error: {e}")

def register(app):
    app.add_handler(CommandHandler("lock", lock))
    app.add_handler(CommandHandler("unlock", unlock))
    app.add_handler(CommandHandler("locks", locks_list))
    app.add_handler(MessageHandler(filters.ALL, check_locks))
