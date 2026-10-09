# ExamYatra – Student Telegram Bot (Phase 1–4)

*Prepare • Practice • Progress*

This package contains the **student bot**: registration, main menu, exam selection, practice quiz,
timed mock tests with scoring, performance, leaderboard, profile, settings, study-material lists,
and data deletion. **Not included yet:** Gemini AI, Admin Panel, API management, broadcasts, roles,
Alembic migrations (tables are created automatically for now).

> Honest status: this code was written and syntax-checked, but it has NOT been run against real
> Telegram or a real database. Run the tests (step 7) and report any error text back.

## 1. Install Termux packages (once)
```
pkg update && pkg upgrade -y
pkg install python unzip nano -y
```

## 2. Unpack the project
Download `examyatra.zip` from Claude into your phone's Downloads, then:
```
termux-setup-storage
cp ~/storage/downloads/examyatra.zip ~
cd ~ && unzip examyatra.zip && cd examyatra
```

## 3. Install Python packages
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
If this fails with words like `Rust`, `maturin` or `pydantic-core`, install the build tools and retry
(this can take a long time on a phone):
```
pkg install rust binutils -y
export ANDROID_API_LEVEL=$(getprop ro.build.version.sdk)
pip install -r requirements.txt
```
Copy the last error lines to Claude if it still fails.

## 4. Create your bot token and .env file
1. In Telegram open **@BotFather**, send `/newbot`, follow the steps, copy the token.
2. Create your settings file:
```
cp .env.example .env
nano .env
```
3. Replace `PASTE_YOUR_BOT_TOKEN_HERE` with your token. To save in Nano: **Ctrl+O**, **Enter**, then **Ctrl+X**.
   (On the Termux keyboard row, Ctrl is a button at the top.)
4. Optional: put your numeric Telegram ID in `ADMIN_IDS` (ask @userinfobot for it).

Never paste your `.env` or token into any chat. If a token leaks, send `/revoke` to @BotFather.

## 5. Add exams and sample content
```
python -m scripts.seed
```
This adds the 7 exam categories plus a few **sample** SSC questions and one sample mock test.

## 6. Run the bot
```
python main.py
```
Open your bot in Telegram, send `/start`. Stop it with **Ctrl+C**.

## 7. Run the automated tests
```
pip install -r requirements-dev.txt
pytest -q
```
The tests cover registration, exam selection, quiz answers and duplicate taps, mock scoring,
double submission, server-side deadlines, leaderboard rules, data deletion, and missing config.

## 8. Quick manual test checklist
- `/start` → welcome + exam buttons appear.
- 🎯 Select Exam → pick SSC.
- ❓ Daily Quiz → pick a subject → answer → see ✅/❌ and explanation. Tap an old answer button again → "already answered".
- 📝 Mock Tests → open the sample test → answer a few → 📤 Submit → see score → 📖 Review answers.
- 🏆 Leaderboard and 📊 My Performance show your result.
- ⚙️ Settings → 🗑 Delete my data removes your history.
- Set `MAINTENANCE_MODE=true` in `.env`, restart, and a non-admin sees the maintenance message.

## 9. Common problems
| Message | Meaning / fix |
|---|---|
| `BOT_TOKEN is missing or looks wrong` | Edit `.env` (step 4). |
| `Telegram rejected BOT_TOKEN` | Token wrong or revoked. Get a fresh one from @BotFather. |
| `ModuleNotFoundError` | Run `source .venv/bin/activate` first (every new Termux session). |
| Bot is silent | Is `python main.py` still running? Only one copy may run per token. |
| `database is locked` | Close any second copy of the bot, then restart. |

## 10. Backup (SQLite)
Stop the bot, then:
```
mkdir -p backups
cp examyatra.db backups/examyatra_$(date +%Y%m%d).db
```
Restore by stopping the bot and copying a backup file back over `examyatra.db`.

## 11. Running 24/7
Termux on Android can be killed by battery optimisation or the system at any time, so it is fine for
learning and testing but **not a guaranteed 24/7 host**. For real use, deploy to a cloud server with
PostgreSQL (planned for the deployment phase).

## Project layout
```
main.py              entry point
bot/                 config, middleware, services (logic), keyboards, handlers/
database/            models and session
scripts/seed.py      exams + sample data
tests/               automated tests
```
