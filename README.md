# 🌸 Kanha Manager Bot

A powerful Telegram Group Management Bot — Rose style.

## Features
- Ban / Unban / Kick / Mute / Unmute
- Warn system with auto-ban/kick/mute
- Welcome & Goodbye messages
- Notes (#notename support)
- Filters (keyword auto-replies)
- Blacklist words (auto-delete)
- Message Locks (sticker/gif/photo/video/url etc.)
- Flood protection
- User Info / Chat Info
- Report system
- Interactive /help menu

---

## 🚀 Deploy on Heroku

### Step 1 — Create Bot
- Go to [@BotFather](https://t.me/BotFather) → /newbot → copy the token

### Step 2 — Get API ID & Hash
- Go to [my.telegram.org](https://my.telegram.org) → login → API development tools → copy API ID and API Hash

### Step 3 — Deploy to Heroku
1. Create a new app on [Heroku](https://heroku.com)
2. Go to **Resources** tab → Add **Heroku Postgres** addon (free plan)
3. Go to **Settings** → **Config Vars** → Add these:

| Key | Value |
|-----|-------|
| `BOT_TOKEN` | Your bot token from BotFather |
| `OWNER_ID` | `7682307978` |
| `OWNER_USERNAME` | Your Telegram username |
| `SUDO_USERS` | `7682307978` |
| `DATABASE_URL` | Auto-filled by Heroku Postgres |
| `API_ID` | From my.telegram.org |
| `API_HASH` | From my.telegram.org |

4. Go to **Deploy** tab → Connect GitHub or upload zip via Heroku CLI
5. Go to **Resources** tab → Enable the **worker** dyno (turn off web dyno if any)

### Step 4 — Add Bot to Group
- Add your bot to a group
- Make it **admin** with these permissions:
  - Delete messages ✅
  - Ban users ✅
  - Restrict members ✅
  - Pin messages ✅
  - Invite users ✅

---

## Commands

| Command | Description |
|---------|-------------|
| `/ban` | Ban a user |
| `/unban` | Unban a user |
| `/kick` | Kick a user |
| `/mute` | Mute a user |
| `/unmute` | Unmute a user |
| `/warn` | Warn a user |
| `/warns` | Check warns |
| `/setwelcome` | Set welcome message |
| `/filter` | Add keyword filter |
| `/save` | Save a note |
| `/lock` | Lock message type |
| `/setflood` | Set flood limit |
| `/report` | Report user to admins |
| `/help` | Show all commands |

---

**Owner:** @YourUsername  
**Bot:** Kanha Manager
