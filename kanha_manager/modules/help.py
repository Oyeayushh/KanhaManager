from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.constants import ParseMode

BOT_NAME = "Kanha Manager"

HELP_MODULES = {
    "👮 Admin": (
        "/ban <reply/user> - Ban a user\n"
        "/unban <reply/user> - Unban a user\n"
        "/kick <reply/user> - Kick a user\n"
        "/mute <reply/user> - Mute a user\n"
        "/unmute <reply/user> - Unmute a user\n"
        "/promote <reply/user> - Promote to admin\n"
        "/demote <reply/user> - Demote admin\n"
        "/pin - Pin replied message\n"
        "/unpin - Unpin all messages"
    ),
    "⚠️ Warns": (
        "/warn <reply/user> [reason] - Warn a user\n"
        "/unwarn <reply/user> - Remove last warn\n"
        "/warns <reply/user> - Check warns\n"
        "/resetwarn <reply/user> - Reset all warns\n"
        "/setwarnlimit <n> - Set warn limit\n"
        "/setwarnmode <ban|kick|mute> - Set warn action"
    ),
    "👋 Welcome": (
        "/setwelcome <message> - Set welcome message\n"
        "/setgoodbye <message> - Set goodbye message\n"
        "/welcome - Toggle welcome on/off\n"
        "/goodbye - Toggle goodbye on/off\n\n"
        "Variables: {mention} {first} {last} {username} {chat} {id}"
    ),
    "📝 Notes": (
        "/save <n> <text> - Save a note\n"
        "/get <n> - Get a note\n"
        "/notes - List all notes\n"
        "/clear <n> - Delete a note\n\n"
        "Also works with #notename in chat!"
    ),
    "🔍 Filters": (
        "/filter <keyword> <reply> - Add a filter\n"
        "/stop <keyword> - Remove a filter\n"
        "/filters - List all filters"
    ),
    "🚫 Blacklist": (
        "/addblacklist <word> - Add word to blacklist\n"
        "/unblacklist <word> - Remove from blacklist\n"
        "/blacklist - List blacklisted words"
    ),
    "🔒 Locks": (
        "/lock <type> - Lock a message type\n"
        "/unlock <type> - Unlock a message type\n"
        "/locks - Show lock status\n\n"
        "Types: sticker gif photo video audio document voice url forward"
    ),
    "🌊 Flood": (
        "/setflood <n|off> - Set flood limit\n"
        "/floodmode <ban|kick|mute> - Set flood action\n"
        "/flood - Show flood settings"
    ),
    "ℹ️ Info": (
        "/info <reply/user> - Get user info\n"
        "/chatinfo - Get group info\n"
        "/id - Get user ID"
    ),
    "🚨 Report": (
        "/report <reply> - Report a user to admins\n\n"
        "Reply to any message and use /report [reason]"
    ),
}

def build_main_keyboard():
    buttons = []
    row = []
    for name in HELP_MODULES:
        row.append(InlineKeyboardButton(name, callback_data=f"help_{name}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("❌ Close", callback_data="help_close")])
    return InlineKeyboardMarkup(buttons)

def build_module_keyboard(mod_name):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="help_back")]
    ])

async def help_cmd(update: Update, context):
    text = (
        f"🌸 <b>Kanha Manager Help</b>\n\n"
        f"Hello! I'm <b>{BOT_NAME}</b> — your powerful group management bot.\n\n"
        f"Choose a category below to see available commands:"
    )
    await update.message.reply_text(
        text,
        reply_markup=build_main_keyboard(),
        parse_mode=ParseMode.HTML
    )

async def help_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "help_back":
        text = (
            f"🌸 <b>Kanha Manager Help</b>\n\n"
            f"Hello! I'm <b>{BOT_NAME}</b> — your powerful group management bot.\n\n"
            f"Choose a category below to see available commands:"
        )
        await query.edit_message_text(
            text,
            reply_markup=build_main_keyboard(),
            parse_mode=ParseMode.HTML
        )
    elif data == "help_close":
        await query.delete_message()
    elif data.startswith("help_"):
        mod_name = data[5:]
        if mod_name in HELP_MODULES:
            content = HELP_MODULES[mod_name]
            text = f"{mod_name} <b>Commands</b>\n\n{content}"
            await query.edit_message_text(
                text,
                reply_markup=build_module_keyboard(mod_name),
                parse_mode=ParseMode.HTML
            )

async def start(update: Update, context):
    user = update.effective_user
    text = (
        f"🌸 <b>Welcome to Kanha Manager!</b>\n\n"
        f"Hey {user.first_name}! I'm a powerful group management bot.\n\n"
        f"Add me to your group and give me admin rights to get started.\n\n"
        f"Use /help to see all commands."
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

def register(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(help_callback, pattern=r"^help_"))
