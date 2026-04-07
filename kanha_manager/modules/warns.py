import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode

from helpers import admin_only, get_target_user, mention_html
from database import Session, UserWarn, WarnSetting

log = logging.getLogger("KanhaManager.Warns")

def get_warn_setting(chat_id):
    s = Session()
    setting = s.query(WarnSetting).filter_by(chat_id=chat_id).first()
    if not setting:
        setting = WarnSetting(chat_id=chat_id, warn_limit=3, warn_mode="ban")
        s.add(setting)
        s.commit()
    s.close()
    return setting

@admin_only
async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_id, name = await get_target_user(update, context)
    if not user_id:
        await update.message.reply_text("❌ Reply to a user or provide username/ID.")
        return

    reason = " ".join(context.args[1:]) if context.args and len(context.args) > 1 else "No reason given."

    s = Session()
    setting = get_warn_setting(chat.id)
    new_warn = UserWarn(chat_id=chat.id, user_id=user_id, reason=reason)
    s.add(new_warn)
    s.commit()

    warn_count = s.query(UserWarn).filter_by(chat_id=chat.id, user_id=user_id).count()
    s.close()

    text = (
        f"⚠️ {mention_html(user_id, name)} has been <b>warned</b>!\n"
        f"📝 <b>Reason:</b> {reason}\n"
        f"📊 <b>Warns:</b> {warn_count}/{setting.warn_limit}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

    if warn_count >= setting.warn_limit:
        mode = setting.warn_mode
        try:
            if mode == "ban":
                await chat.ban_member(user_id)
                await update.message.reply_text(
                    f"🚫 {mention_html(user_id, name)} has been <b>banned</b> for reaching warn limit!",
                    parse_mode=ParseMode.HTML
                )
            elif mode == "kick":
                await chat.ban_member(user_id)
                await chat.unban_member(user_id)
                await update.message.reply_text(
                    f"👟 {mention_html(user_id, name)} has been <b>kicked</b> for reaching warn limit!",
                    parse_mode=ParseMode.HTML
                )
            elif mode == "mute":
                from admin import NO_PERMISSIONS
                await chat.restrict_member(user_id, NO_PERMISSIONS)
                await update.message.reply_text(
                    f"🔇 {mention_html(user_id, name)} has been <b>muted</b> for reaching warn limit!",
                    parse_mode=ParseMode.HTML
                )
        except Exception as e:
            log.error(f"Failed to punish after warns: {e}")

        # Reset warns
        s = Session()
        s.query(UserWarn).filter_by(chat_id=chat.id, user_id=user_id).delete()
        s.commit()
        s.close()

@admin_only
async def unwarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_id, name = await get_target_user(update, context)
    if not user_id:
        await update.message.reply_text("❌ Reply to a user or provide username/ID.")
        return

    s = Session()
    last_warn = s.query(UserWarn).filter_by(chat_id=chat.id, user_id=user_id).order_by(UserWarn.warned_at.desc()).first()
    if last_warn:
        s.delete(last_warn)
        s.commit()
        count = s.query(UserWarn).filter_by(chat_id=chat.id, user_id=user_id).count()
        s.close()
        setting = get_warn_setting(chat.id)
        await update.message.reply_text(
            f"✅ Removed one warn from {mention_html(user_id, name)}.\n📊 <b>Warns:</b> {count}/{setting.warn_limit}",
            parse_mode=ParseMode.HTML
        )
    else:
        s.close()
        await update.message.reply_text(f"ℹ️ {mention_html(user_id, name)} has no warns.", parse_mode=ParseMode.HTML)

async def warns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_id, name = await get_target_user(update, context)
    if not user_id:
        if update.effective_user:
            user_id = update.effective_user.id
            name = update.effective_user.first_name
        else:
            await update.message.reply_text("❌ Who?")
            return

    s = Session()
    all_warns = s.query(UserWarn).filter_by(chat_id=chat.id, user_id=user_id).all()
    s.close()
    setting = get_warn_setting(chat.id)

    if not all_warns:
        await update.message.reply_text(f"✅ {mention_html(user_id, name)} has no warns.", parse_mode=ParseMode.HTML)
        return

    text = f"⚠️ <b>Warns for {mention_html(user_id, name)}:</b> {len(all_warns)}/{setting.warn_limit}\n\n"
    for i, w in enumerate(all_warns, 1):
        text += f"{i}. {w.reason}\n"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

@admin_only
async def resetwarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_id, name = await get_target_user(update, context)
    if not user_id:
        await update.message.reply_text("❌ Reply to a user or provide username/ID.")
        return

    s = Session()
    s.query(UserWarn).filter_by(chat_id=chat.id, user_id=user_id).delete()
    s.commit()
    s.close()
    await update.message.reply_text(f"✅ All warns cleared for {mention_html(user_id, name)}.", parse_mode=ParseMode.HTML)

@admin_only
async def setwarnlimit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not context.args:
        await update.message.reply_text("Usage: /setwarnlimit <number>")
        return
    try:
        limit = int(context.args[0])
        if limit < 1:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Provide a valid number.")
        return

    s = Session()
    setting = s.query(WarnSetting).filter_by(chat_id=chat.id).first()
    if not setting:
        setting = WarnSetting(chat_id=chat.id)
        s.add(setting)
    setting.warn_limit = limit
    s.commit()
    s.close()
    await update.message.reply_text(f"✅ Warn limit set to <b>{limit}</b>.", parse_mode=ParseMode.HTML)

@admin_only
async def setwarnmode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not context.args or context.args[0] not in ("ban", "kick", "mute"):
        await update.message.reply_text("Usage: /setwarnmode <ban|kick|mute>")
        return

    mode = context.args[0]
    s = Session()
    setting = s.query(WarnSetting).filter_by(chat_id=chat.id).first()
    if not setting:
        setting = WarnSetting(chat_id=chat.id)
        s.add(setting)
    setting.warn_mode = mode
    s.commit()
    s.close()
    await update.message.reply_text(f"✅ Warn mode set to <b>{mode}</b>.", parse_mode=ParseMode.HTML)

def register(app):
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("unwarn", unwarn))
    app.add_handler(CommandHandler("warns", warns))
    app.add_handler(CommandHandler("resetwarn", resetwarn))
    app.add_handler(CommandHandler("setwarnlimit", setwarnlimit))
    app.add_handler(CommandHandler("setwarnmode", setwarnmode))
