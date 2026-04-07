import logging
from datetime import timedelta
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode

from helpers import admin_only, get_target_user, mention_html, is_sudo

log = logging.getLogger("KanhaManager.Admin")

FULL_PERMISSIONS = ChatPermissions(
    can_send_messages=True,
    can_send_audios=True,
    can_send_documents=True,
    can_send_photos=True,
    can_send_videos=True,
    can_send_video_notes=True,
    can_send_voice_notes=True,
    can_send_polls=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True,
    can_change_info=False,
    can_invite_users=True,
    can_pin_messages=False,
)

NO_PERMISSIONS = ChatPermissions(
    can_send_messages=False,
    can_send_audios=False,
    can_send_documents=False,
    can_send_photos=False,
    can_send_videos=False,
    can_send_video_notes=False,
    can_send_voice_notes=False,
    can_send_polls=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False,
)

@admin_only
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_id, name = await get_target_user(update, context)
    if not user_id:
        await update.message.reply_text("❌ Reply to a user or provide username/ID.")
        return
    reason = " ".join(context.args[1:]) if context.args and len(context.args) > 1 else "No reason given."
    try:
        await chat.ban_member(user_id)
        text = f"🚫 {mention_html(user_id, name)} has been <b>banned</b>.\n📝 <b>Reason:</b> {reason}"
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to ban: {e}")

@admin_only
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_id, name = await get_target_user(update, context)
    if not user_id:
        await update.message.reply_text("❌ Reply to a user or provide username/ID.")
        return
    try:
        await chat.unban_member(user_id)
        text = f"✅ {mention_html(user_id, name)} has been <b>unbanned</b>."
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to unban: {e}")

@admin_only
async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_id, name = await get_target_user(update, context)
    if not user_id:
        await update.message.reply_text("❌ Reply to a user or provide username/ID.")
        return
    reason = " ".join(context.args[1:]) if context.args and len(context.args) > 1 else "No reason given."
    try:
        await chat.ban_member(user_id)
        await chat.unban_member(user_id)
        text = f"👟 {mention_html(user_id, name)} has been <b>kicked</b>.\n📝 <b>Reason:</b> {reason}"
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to kick: {e}")

@admin_only
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_id, name = await get_target_user(update, context)
    if not user_id:
        await update.message.reply_text("❌ Reply to a user or provide username/ID.")
        return
    try:
        await chat.restrict_member(user_id, NO_PERMISSIONS)
        text = f"🔇 {mention_html(user_id, name)} has been <b>muted</b>."
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to mute: {e}")

@admin_only
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_id, name = await get_target_user(update, context)
    if not user_id:
        await update.message.reply_text("❌ Reply to a user or provide username/ID.")
        return
    try:
        await chat.restrict_member(user_id, FULL_PERMISSIONS)
        text = f"🔊 {mention_html(user_id, name)} has been <b>unmuted</b>."
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to unmute: {e}")

@admin_only
async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg.reply_to_message:
        await msg.reply_text("❌ Reply to a message to pin it.")
        return
    try:
        await msg.reply_to_message.pin()
        await msg.reply_text("📌 Message pinned!")
    except Exception as e:
        await msg.reply_text(f"❌ Failed to pin: {e}")

@admin_only
async def unpin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    try:
        await chat.unpin_all_messages()
        await update.message.reply_text("📌 All messages unpinned!")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to unpin: {e}")

@admin_only
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_id, name = await get_target_user(update, context)
    if not user_id:
        await update.message.reply_text("❌ Reply to a user or provide username/ID.")
        return
    try:
        await chat.promote_member(
            user_id,
            can_delete_messages=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_invite_users=True,
        )
        text = f"⭐ {mention_html(user_id, name)} has been <b>promoted</b>!"
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to promote: {e}")

@admin_only
async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_id, name = await get_target_user(update, context)
    if not user_id:
        await update.message.reply_text("❌ Reply to a user or provide username/ID.")
        return
    try:
        await chat.promote_member(
            user_id,
            can_delete_messages=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_invite_users=False,
            can_change_info=False,
            can_manage_chat=False,
        )
        text = f"🔻 {mention_html(user_id, name)} has been <b>demoted</b>."
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to demote: {e}")

def register(app):
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("pin", pin))
    app.add_handler(CommandHandler("unpin", unpin))
    app.add_handler(CommandHandler("promote", promote))
    app.add_handler(CommandHandler("demote", demote))
