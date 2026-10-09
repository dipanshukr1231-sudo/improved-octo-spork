"""ExamYatra student bot – entry point.  Run with:  python main.py"""
from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.types import BotCommand, ErrorEvent

from bot.config import ConfigError, load_settings
from bot.handlers import ROUTERS
from bot.logging_setup import setup_logging
from bot.middlewares import AccessMiddleware
from bot.services import expire_overdue
from database.session import init_models, make_engine, make_session_factory

log = logging.getLogger("examyatra")


async def expiry_loop(session_factory) -> None:
    """Every minute, auto-submit mock tests whose time has run out."""
    while True:
        try:
            async with session_factory() as session:
                count = await expire_overdue(session)
                await session.commit()
                if count:
                    log.info("Auto-submitted %d overdue test attempt(s)", count)
        except Exception:
            log.exception("Expiry loop error (will retry)")
        await asyncio.sleep(60)


async def on_error(event: ErrorEvent) -> bool:
    log.error("Unhandled error while processing an update", exc_info=event.exception)
    try:
        if event.update.callback_query:
            await event.update.callback_query.answer("Something went wrong. Please try again.", show_alert=True)
        elif event.update.message:
            await event.update.message.answer("⚠️ Something went wrong. Please try again.")
    except Exception:
        pass
    return True


async def main() -> int:
    try:
        cfg = load_settings()
    except ConfigError as exc:
        print(f"\n❌ Configuration problem:\n{exc}\n")
        return 1
    setup_logging(cfg.log_level)

    engine = make_engine(cfg.database_url)
    await init_models(engine)
    session_factory = make_session_factory(engine)

    bot = Bot(token=cfg.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    access = AccessMiddleware(cfg, session_factory)
    dp.message.middleware(access)
    dp.callback_query.middleware(access)
    for router in ROUTERS:
        dp.include_router(router)
    dp.errors.register(on_error)

    background = None
    try:
        me = await bot.get_me()
        log.info("Bot started as @%s", me.username)
        await bot.set_my_commands(
            [
                BotCommand(command="start", description="Start ExamYatra"),
                BotCommand(command="menu", description="Show main menu"),
                BotCommand(command="help", description="Help & support"),
            ]
        )
        background = asyncio.create_task(expiry_loop(session_factory))
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        return 0
    except TelegramUnauthorizedError:
        print("\n❌ Telegram rejected BOT_TOKEN. Check it in .env (get a new one from @BotFather with /token).\n")
        return 1
    finally:
        if background:
            background.cancel()
        await bot.session.close()
        await engine.dispose()
        log.info("Shutdown complete")


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        pass
