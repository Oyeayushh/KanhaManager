import logging
from telegram import Update, ChatMemberUpdated, ChatMember
from telegram.ext import ContextTypes, CommandHandler, ChatMemberHandler
from telegram.constants import ParseMode

from helpers import admin_only, mention_html
from database import Session, WelcomeSetting

log = logging.getLogger("KanhaManager.Welcome")

def get_setting(chat_id):
    s = Session()
    setting = s.query(WelcomeSetting).filter_by(chat_id=chat_id).first()
    if not setting:
        setting = WelcomeSetting(chat_id=chat_id)
        s.add(setting)
        s.commit()
    s.close()
    return setting

def format_message(template, user, chat):
    mention = mention_html(user.id, user.first_name)
    return (
        template
        .replace("{mention}", mention)
        .replace("{first}", user.first_name or "")
        .replace("{last}", user.last_name or "")
        .replace("{username}", f"@{user.username}" if user.username else user.first_name)
        .replace("{chat}", chat.title or "this group")
        .replace("{id}", str(user.id))
    )

async def greet_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result: ChatMemberUpdated = update.chat_member
    if not result:
        return

    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status
    user = result.new_chat_member.user
    chat = result.chat

    if user.is_bot:
        return

    # User joined
    if old_status in (ChatMember.LEFT, ChatMember.BANNED) and new_status == ChatMember.MEMBER:
        setting = get_setting(chat.id)
        if setting.welcome_enabled:
            text = format_message(setting.welcome_message, user, chat)
            try:
                await context.bot.send_message(chat.id, text, parse_mode=ParseMode.HTML)
            except Exception as e:
                log.error(f"Welcome error: {e}")

    # User left
    elif old_status == ChatMember.MEMBER and new_status in (ChatMember.LEFT, ChatMember.BANNED):
        setting = get_setting(chat.id)
        if setting.goodbye_enabled:
            text = format_message(setting.goodbye_message, user, chat)
            try:
                await context.bot.send_message(chat.id, text, parse_mode=ParseMode.HTML)
            except Exception as e:
                log.error(f"Goodbye error: {e}")

@admin_only
async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.effective_message
    if not context.args and not msg.reply_to_message:
        await msg.reply_text(
            "Usage: /setwelcome <message>\n\n"
            "Variables:\n{mention} {first} {last} {username} {chat} {id}"
        )
        return

    if msg.reply_to_message:
        text = msg.reply_to_message.text or msg.reply_to_message.caption or ""
    else:
        text = " ".join(context.args)

    s = Session()
    setting = s.query(WelcomeSetting).filter_by(chat_id=chat.id).first()
    if not setting:
        setting = WelcomeSetting(chat_id=chat.id)
        s.add(setting)
    setting.welcome_message = text
    setting.welcome_enabled = True
    s.commit()
    s.close()
    await msg.reply_text("✅ Welcome message updated!")

@admin_only
async def set_goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.effective_message
    if not context.args and not msg.reply_to_message:
        await msg.reply_text(
            "Usage: /setgoodbye <message>\n\n"
            "Variables:\n{mention} {first} {last} {username} {chat} {id}"
        )
        return

    if msg.reply_to_message:
        text = msg.reply_to_message.text or msg.reply_to_message.caption or ""
    else:
        text = " ".join(context.args)

    s = Session()
    setting = s.query(WelcomeSetting).filter_by(chat_id=chat.id).first()
    if not setting:
        setting = WelcomeSetting(chat_id=chat.id)
        s.add(setting)
    setting.goodbye_message = text
    setting.goodbye_enabled = True
    s.commit()
    s.close()
    await msg.reply_text("✅ Goodbye message updated!")

@admin_only
async def welcome_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    s = Session()
    setting = s.query(WelcomeSetting).filter_by(chat_id=chat.id).first()
    if not setting:
        setting = WelcomeSetting(chat_id=chat.id)
        s.add(setting)
    setting.welcome_enabled = not setting.welcome_enabled
    s.commit()
    state = "✅ enabled" if setting.welcome_enabled else "❌ disabled"
    s.close()
    await update.message.reply_text(f"Welcome message is now {state}.")

@admin_only
async def goodbye_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    s = Session()
    setting = s.query(WelcomeSetting).filter_by(chat_id=chat.id).first()
    if not setting:
        setting = WelcomeSetting(chat_id=chat.id)
        s.add(setting)
    setting.goodbye_enabled = not setting.goodbye_enabled
    s.commit()
    state = "✅ enabled" if setting.goodbye_enabled else "❌ disabled"
    s.close()
    await update.message.reply_text(f"Goodbye message is now {state}.")

def register(app):
    app.add_handler(ChatMemberHandler(greet_new_member, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(CommandHandler("setwelcome", set_welcome))
    app.add_handler(CommandHandler("setgoodbye", set_goodbye))
    app.add_handler(CommandHandler("welcome", welcome_toggle))
    app.add_handler(CommandHandler("goodbye", goodbye_toggle))
