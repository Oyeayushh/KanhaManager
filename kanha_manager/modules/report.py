import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode

from helpers import mention_html, is_admin, is_sudo

log = logging.getLogger("KanhaManager.Report")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        await msg.reply_text("Reports only work in groups.")
        return

    if not msg.reply_to_message:
        await msg.reply_text("❌ Reply to a message to report it.")
        return

    reported_user = msg.reply_to_message.from_user
    if not reported_user:
        await msg.reply_text("❌ Cannot report that message.")
        return

    if reported_user.id == user.id:
        await msg.reply_text("😅 You can't report yourself!")
        return

    if is_sudo(reported_user.id):
        await msg.reply_text("⚠️ That user is a bot admin — can't report them.")
        return

    if await is_admin(update, reported_user.id):
        await msg.reply_text("⚠️ That user is an admin — can't report them.")
        return

    reason = " ".join(context.args) if context.args else "No reason given."

    # Get all admins and notify them
    try:
        admins = await chat.get_administrators()
        admin_mentions = []
        for admin in admins:
            if not admin.user.is_bot:
                admin_mentions.append(mention_html(admin.user.id, admin.user.first_name))

        report_text = (
            f"⚠️ <b>Report</b>\n\n"
            f"👤 <b>Reported by:</b> {mention_html(user.id, user.first_name)}\n"
            f"🚨 <b>Reported user:</b> {mention_html(reported_user.id, reported_user.first_name)}\n"
            f"📝 <b>Reason:</b> {reason}\n\n"
            f"📢 Admins: {' '.join(admin_mentions)}"
        )
        await msg.reply_text(report_text, parse_mode=ParseMode.HTML)
    except Exception as e:
        log.error(f"Report error: {e}")
        await msg.reply_text("❌ Could not send report.")

def register(app):
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("report", report))
