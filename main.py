import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from database.db import init_db, add_sample_events
from handlers.commands import (
    cmd_start, cmd_profile, cmd_fishing, cmd_map, cmd_boost,
    cmd_bag, cmd_equipment, cmd_upgrade, cmd_daily, cmd_history,
    cmd_vip, cmd_shop, cmd_market, cmd_favorite, cmd_collection,
    cmd_transfer, cmd_transfer_execute, cmd_topup, cmd_event,
    cmd_leaderboard, cmd_group, cmd_help,
    handle_callback, handle_message,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("❌ BOT_TOKEN tidak ditemukan di environment variables!")

    # Init database
    init_db()
    add_sample_events()

    app = ApplicationBuilder().token(token).build()

    # ── COMMANDS ──────────────────────────────────────────────
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("profil", cmd_profile))
    app.add_handler(CommandHandler("profile", cmd_profile))
    app.add_handler(CommandHandler("fishing", cmd_fishing))
    app.add_handler(CommandHandler("map", cmd_map))
    app.add_handler(CommandHandler("boost", cmd_boost))
    app.add_handler(CommandHandler("bag", cmd_bag))
    app.add_handler(CommandHandler("equipment", cmd_equipment))
    app.add_handler(CommandHandler("upgrade", cmd_upgrade))
    app.add_handler(CommandHandler("daily", cmd_daily))
    app.add_handler(CommandHandler("history", cmd_history))
    app.add_handler(CommandHandler("vip", cmd_vip))
    app.add_handler(CommandHandler("shop", cmd_shop))
    app.add_handler(CommandHandler("market", cmd_market))
    app.add_handler(CommandHandler("favorite", cmd_favorite))
    app.add_handler(CommandHandler("collection", cmd_collection))
    app.add_handler(CommandHandler("transfer", cmd_transfer_execute))
    app.add_handler(CommandHandler("topup", cmd_topup))
    app.add_handler(CommandHandler("event", cmd_event))
    app.add_handler(CommandHandler("leaderboard", cmd_leaderboard))
    app.add_handler(CommandHandler("group", cmd_group))
    app.add_handler(CommandHandler("channel", cmd_group))
    app.add_handler(CommandHandler("help", cmd_help))

    # ── CALLBACK QUERIES ──────────────────────────────────────
    app.add_handler(CallbackQueryHandler(handle_callback))

    # ── MESSAGES (for market price input) ────────────────────
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message
    ))

    logger.info("✅ Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
