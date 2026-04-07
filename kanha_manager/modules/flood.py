import logging
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode

from helpers import admin_only, is_admin, is_sudo, mention_html
from database import Session, FloodSetting, FloodCount
from admin import NO_PERMISSIONS

log = logging.getLogger("KanhaManager.Flood")

@admin_only
async def set_flood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not context.args:
        await update.message.reply_text("Usage: /setflood <number|off>\nExample: /setflood 5")
        return

    arg = context.args[0].lower()
    s = Session()
    setting = s.query(FloodSetting).filter_by(chat_id=chat.id).first()
    if not setting:
        setting = FloodSetting(chat_id=chat.id)
        s.add(setting)

    if arg == "off" or arg == "0":
        setting.limit = 0
        s.commit()
        s.close()
        await update.message.reply_text("✅ Flood protection disabled.")
        return

    try:
        limit = int(arg)
        if limit < 2:
            raise ValueError
    except ValueError:
        s.close()
        await update.message.reply_text("❌ Provide a valid number (min 2) or 'off'.")
        return

    setting.limit = limit
    s.commit()
    s.close()
    await update.message.reply_text(
        f"✅ Flood protection set to <b>{limit}</b> messages.\nMode: <b>{setting.mode}</b>",
        parse_mode=ParseMode.HTML
    )

@admin_only
async def set_flood_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not context.args or context.args[0] not in ("ban", "kick", "mute"):
        await update.message.reply_text("Usage: /floodmode <ban|kick|mute>")
        return

    mode = context.args[0]
    s = Session()
    setting = s.query(FloodSetting).filter_by(chat_id=chat.id).first()
    if not setting:
        setting = FloodSetting(chat_id=chat.id)
        s.add(setting)
    setting.mode = mode
    s.commit()
    s.close()
    await update.message.reply_text(f"✅ Flood mode set to <b>{mode}</b>.", parse_mode=ParseMode.HTML)

async def flood_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    s = Session()
    setting = s.query(FloodSetting).filter_by(chat_id=chat.id).first()
    s.close()
    if not setting or setting.limit == 0:
        await update.message.reply_text("ℹ️ Flood protection is <b>disabled</b>.", parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(
            f"🌊 Flood limit: <b>{setting.limit}</b> messages\nMode: <b>{setting.mode}</b>",
            parse_mode=ParseMode.HTML
        )

async def check_flood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not user or not chat:
        return
    if is_sudo(user.id):
        return
    if await is_admin(update, user.id):
        return

    s = Session()
    setting = s.query(FloodSetting).filter_by(chat_id=chat.id).first()
    if not setting or setting.limit == 0:
        s.close()
        return

    flood = s.query(FloodCount).filter_by(chat_id=chat.id, user_id=user.id).first()
    if not flood:
        flood = FloodCount(chat_id=chat.id, user_id=user.id, count=1, last_msg_id=msg.message_id)
        s.add(flood)
        s.commit()
        s.close()
        return

    if msg.message_id == flood.last_msg_id + 1:
        flood.count += 1
        flood.last_msg_id = msg.message_id
    else:
        flood.count = 1
        flood.last_msg_id = msg.message_id
    s.commit()

    if flood.count >= setting.limit:
        flood.count = 0
        s.commit()
        s.close()
        mode = setting.mode
        name = user.first_name
        try:
            if mode == "ban":
                await chat.ban_member(user.id)
                await msg.reply_text(
                    f"🚫 {mention_html(user.id, name)} banned for flooding!",
                    parse_mode=ParseMode.HTML
                )
            elif mode == "kick":
                await chat.ban_member(user.id)
                await chat.unban_member(user.id)
                await msg.reply_text(
                    f"👟 {mention_html(user.id, name)} kicked for flooding!",
                    parse_mode=ParseMode.HTML
                )
            elif mode == "mute":
                await chat.restrict_member(user.id, NO_PERMISSIONS)
                await msg.reply_text(
                    f"🔇 {mention_html(user.id, name)} muted for flooding!",
                    parse_mode=ParseMode.HTML
                )
        except Exception as e:
            log.error(f"Flood action error: {e}")
    else:
        s.close()

def register(app):
    app.add_handler(CommandHandler("setflood", set_flood))
    app.add_handler(CommandHandler("floodmode", set_flood_mode))
    app.add_handler(CommandHandler("flood", flood_status))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, check_flood))
