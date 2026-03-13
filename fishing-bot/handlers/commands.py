import logging
import math
from datetime import datetime, timedelta
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from database.db import (
    get_player, create_player, update_player, add_coins, spend_coins,
    add_xp, get_inventory, add_to_inventory, use_inventory_item, has_item,
    get_bag, get_bag_count, add_to_bag, remove_from_bag, get_bag_item,
    toggle_favorite, get_favorites, add_history, get_history,
    get_active_boosts, activate_boost, get_total_boost,
    list_market_item, get_market_listings, buy_market_item, cancel_market_listing,
    get_rod_upgrade, upgrade_rod, get_unlocked_maps, unlock_map,
    get_leaderboard, is_vip_active, get_vip_bonus,
    get_active_events, get_all_events
)
from data.fish_data import FISH_DATA, RARITY_COLORS
from data.shop_data import (
    RODS, BAITS, BOOSTS, VIP_TIERS, MAPS, TOPUP_PACKAGES,
    get_level_title, xp_for_level
)
from utils.fishing_engine import do_fishing, get_fishing_cooldown
from utils.keyboards import (
    main_menu_keyboard, shop_menu_keyboard, back_button,
    fishing_action_keyboard, after_catch_keyboard, map_select_keyboard,
    equipment_keyboard, rod_select_keyboard, bait_select_keyboard,
    bag_keyboard, bag_item_keyboard, market_keyboard, boost_keyboard,
    leaderboard_keyboard, upgrade_keyboard, topup_keyboard, vip_keyboard,
    confirm_keyboard
)
from utils.formatters import (
    format_player_profile, format_fish_catch, format_bag,
    format_boost_status, format_shop_rods, format_shop_baits,
    format_history, rarity_badge, fmt_number
)

logger = logging.getLogger(__name__)

GROUP_LINK = "https://t.me/your_group"    # ← ganti dengan link grup kamu
CHANNEL_LINK = "https://t.me/your_channel"  # ← ganti dengan link channel kamu
ADMIN_IDS = []  # tambahkan ID admin jika diperlukan

PER_PAGE = 10

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

async def _safe_edit(query, text: str, keyboard=None, parse_mode=ParseMode.MARKDOWN):
    try:
        await query.edit_message_text(
            text, reply_markup=keyboard, parse_mode=parse_mode
        )
    except Exception:
        try:
            await query.message.reply_text(
                text, reply_markup=keyboard, parse_mode=parse_mode
            )
        except Exception as e:
            logger.error(f"Message send error: {e}")

async def _safe_reply(update: Update, text: str, keyboard=None, parse_mode=ParseMode.MARKDOWN):
    try:
        await update.message.reply_text(
            text, reply_markup=keyboard, parse_mode=parse_mode,
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Reply error: {e}")

def _get_or_require_player(user_id: int):
    """Return player or None."""
    return get_player(user_id)

def _cooldown_key(user_id: int) -> str:
    return f"fishing_cd_{user_id}"

def _get_cooldown_left(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> int:
    key = _cooldown_key(user_id)
    cd_end: Optional[datetime] = context.bot_data.get(key)
    if not cd_end:
        return 0
    left = (cd_end - datetime.utcnow()).total_seconds()
    return max(0, int(left))

def _set_cooldown(context: ContextTypes.DEFAULT_TYPE, user_id: int, seconds: int):
    key = _cooldown_key(user_id)
    context.bot_data[key] = datetime.utcnow() + timedelta(seconds=seconds)

# ─────────────────────────────────────────────────────────────
# /start
# ─────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        player = create_player(user.id, user.username, user.full_name)
        text = (
            f"🎉 **SELAMAT DATANG DI FISHING WORLD!** 🎉\n\n"
            f"Halo **{user.first_name}**! 👋\n\n"
            f"Akun kamu telah berhasil dibuat!\n\n"
            f"🎁 **Hadiah Pendaftaran:**\n"
            f"💰 500 Koin\n"
            f"🪱 10x Cacing Tanah\n"
            f"🎋 1x Joran Bambu\n\n"
            f"Selamat memancing dan kumpulkan ikan langka! 🎣\n\n"
            f"Gunakan menu di bawah untuk mulai bermain:"
        )
    else:
        text = (
            f"🎣 **FISHING WORLD**\n\n"
            f"Selamat datang kembali, **{user.first_name}**! 👋\n\n"
            f"💰 Koin: {fmt_number(player['coins'])}\n"
            f"⭐ Level: {player['level']}\n\n"
            f"Pilih menu di bawah:"
        )
    await _safe_reply(update, text, main_menu_keyboard())

# ─────────────────────────────────────────────────────────────
# /profile
# ─────────────────────────────────────────────────────────────

async def cmd_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await _safe_reply(update, "❌ Kamu belum terdaftar! Ketik /start", back_button())
        return
    rod_upgrade = get_rod_upgrade(user.id)
    vip = is_vip_active(player)
    text = format_player_profile(player, rod_upgrade, vip)
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎣 Equipment", callback_data="cmd_equipment"),
            InlineKeyboardButton("🔧 Upgrade", callback_data="cmd_upgrade"),
        ],
        [InlineKeyboardButton("◀️ Menu Utama", callback_data="cmd_main")],
    ])
    await _safe_reply(update, text, kb)

# ─────────────────────────────────────────────────────────────
# /fishing
# ─────────────────────────────────────────────────────────────

async def cmd_fishing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await _safe_reply(update, "❌ Ketik /start untuk mendaftar!", back_button())
        return
    await _show_fishing_screen(update, context, player, is_callback=False)

async def _show_fishing_screen(update, context, player, is_callback=False):
    user = update.effective_user if not is_callback else update.callback_query.from_user
    cd_left = _get_cooldown_left(context, user.id)
    can_fish = cd_left == 0

    rod = RODS.get(player["current_rod"], RODS["rod_bamboo"])
    bait = BAITS.get(player["current_bait"], BAITS["bait_worm"])
    location = MAPS.get(player["current_map"], MAPS["map_kolam"])
    boost = get_total_boost(user.id)
    vip_b = get_vip_bonus(player)

    rod_upgrade = get_rod_upgrade(user.id)
    total_luck = (
        rod.get("luck_bonus", 0) + bait.get("luck_bonus", 0)
        + rod_upgrade.get("luck_bonus", 0) + boost.get("luck", 0) + vip_b.get("luck", 0)
    )
    total_rare = (
        rod.get("rare_bonus", 0) + bait.get("rare_bonus", 0)
        + rod_upgrade.get("rare_bonus", 0) + boost.get("rare", 0) + vip_b.get("rare", 0)
    )

    vip_label = "✅ Aktif" if is_vip_active(player) else "❌ Tidak Aktif"
    bag_count = get_bag_count(user.id)

    text = (
        f"🎣 **MEMANCING**\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"📍 **Lokasi:** {location['name']}\n"
        f"🎣 **Joran:** {rod['emoji']} {rod['name']}\n"
        f"🔧 **Upgrade:** Lv.{rod_upgrade.get('level',0)}\n"
        f"🪱 **Umpan:** {bait['emoji']} {bait['name']}\n\n"
        f"📊 **Status Bonus:**\n"
        f"🍀 Luck: +{total_luck}%\n"
        f"💎 Rare: +{total_rare}%\n"
        f"⭐ XP: +{boost.get('xp',0)+vip_b.get('xp',0)}%\n"
        f"👑 VIP: {vip_label}\n\n"
        f"🎒 Tas: {bag_count} ikan\n"
    )
    if can_fish:
        text += "\n✅ **Siap memancing!** Tekan tombol di bawah!"
    else:
        text += f"\n⏳ **Cooldown:** {cd_left} detik lagi..."

    kb = fishing_action_keyboard(can_fish, cd_left)
    if is_callback:
        await _safe_edit(update.callback_query, text, kb)
    else:
        await _safe_reply(update, text, kb)

# ─────────────────────────────────────────────────────────────
# DO FISHING
# ─────────────────────────────────────────────────────────────

async def do_fishing_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    player = get_player(user.id)
    if not player:
        await _safe_edit(query, "❌ Ketik /start untuk mendaftar!")
        return

    cd_left = _get_cooldown_left(context, user.id)
    if cd_left > 0:
        await query.answer(f"⏳ Tunggu {cd_left} detik lagi!", show_alert=True)
        return

    # Check bait
    bait_id = player["current_bait"]
    if bait_id != "bait_worm" or True:  # always check
        if not has_item(user.id, bait_id):
            # Try fallback to worm
            if has_item(user.id, "bait_worm"):
                update_player(user.id, current_bait="bait_worm")
                player["current_bait"] = "bait_worm"
                bait_id = "bait_worm"
            else:
                await _safe_edit(query,
                    "❌ **Umpan Habis!**\n\nBeli umpan di /shop untuk melanjutkan memancing.",
                    InlineKeyboardMarkup([
                        [InlineKeyboardButton("🛒 Beli Umpan", callback_data="shop_baits")],
                        [InlineKeyboardButton("◀️ Menu", callback_data="cmd_main")],
                    ])
                )
                return

    rod_upgrade = get_rod_upgrade(user.id)
    boost = get_total_boost(user.id)
    vip_b = get_vip_bonus(player)
    vip = is_vip_active(player)

    result = do_fishing(
        user_id=user.id,
        rod_id=player["current_rod"],
        bait_id=bait_id,
        map_id=player["current_map"],
        rod_upgrade=rod_upgrade,
        boost_bonus=boost,
        vip_bonus=vip_b,
        player_level=player["level"],
    )

    if not result.get("success"):
        await query.answer("Tidak ada ikan yang tertangkap, coba lagi!", show_alert=True)
        return

    # Use one bait
    use_inventory_item(user.id, bait_id, 1)

    # Set cooldown
    cd_seconds = get_fishing_cooldown(player["current_map"], player["current_rod"], vip)
    _set_cooldown(context, user.id, cd_seconds)

    # Save to bag
    location_name = MAPS.get(player["current_map"], {}).get("name", "Unknown")
    bag_id = add_to_bag(user.id, result["fish_name"], result["weight"], result["rarity"], location_name)

    # Add XP
    xp_result = add_xp(user.id, result["xp_earned"])

    # Update stats
    update_player(user.id, total_caught=player["total_caught"] + 1)

    # Add history
    add_history(user.id, result["fish_name"], result["weight"],
                result["rarity"], "catch", 0, location_name)

    # Format message
    text = format_fish_catch(
        result["fish_name"], result["rarity"], result["weight"],
        result["xp_earned"], location_name
    )

    # Level up notification
    if xp_result["leveled_up"]:
        text += (
            f"\n\n🎊 **LEVEL UP!** 🎊\n"
            f"Level {xp_result['old_level']} → **{xp_result['new_level']}**\n"
            f"🏅 {get_level_title(xp_result['new_level'])}"
        )

    text += f"\n\n⏳ Cooldown: {cd_seconds} detik"

    await _safe_edit(query, text, after_catch_keyboard(bag_id))

# ─────────────────────────────────────────────────────────────
# /map
# ─────────────────────────────────────────────────────────────

async def cmd_map(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await _safe_reply(update, "❌ Ketik /start untuk mendaftar!")
        return
    unlocked = get_unlocked_maps(user.id)
    text = "🗺 **PILIH LOKASI MEMANCING**\n\n"
    for map_id, m in MAPS.items():
        status = "✅" if map_id in unlocked else ("🔓" if player["level"] >= m["level_req"] else "🔒")
        text += (
            f"{status} {m['name']}\n"
            f"   📊 Ikan: {', '.join(m['fish_types'])}\n"
            f"   💎 Rare x{m['rare_multiplier']} | 💰 Koin x{m['coin_multiplier']}\n"
            f"   🔑 Level {m['level_req']} | 💰 {fmt_number(m['unlock_cost'])} koin\n\n"
        )
    kb = map_select_keyboard(unlocked, player["level"], MAPS)
    await _safe_reply(update, text, kb)

# ─────────────────────────────────────────────────────────────
# /boost
# ─────────────────────────────────────────────────────────────

async def cmd_boost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await _safe_reply(update, "❌ Ketik /start untuk mendaftar!")
        return
    active = get_active_boosts(user.id)
    total = get_total_boost(user.id)
    text = format_boost_status(active, total)
    boosts_owned = get_inventory(user.id, "boost")
    kb = boost_keyboard(boosts_owned)
    await _safe_reply(update, text, kb)

# ─────────────────────────────────────────────────────────────
# /bag
# ─────────────────────────────────────────────────────────────

async def cmd_bag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await _safe_reply(update, "❌ Ketik /start untuk mendaftar!")
        return
    await _show_bag(update, context, user.id, page=1, is_callback=False)

async def _show_bag(update, context, user_id, page=1, is_callback=False):
    total = get_bag_count(user_id)
    total_pages = max(1, math.ceil(total / PER_PAGE))
    page = max(1, min(page, total_pages))
    items = get_bag(user_id, limit=PER_PAGE, offset=(page - 1) * PER_PAGE)
    text = format_bag(items, page, total, PER_PAGE)
    kb = bag_keyboard(items, page, total_pages)
    if is_callback:
        await _safe_edit(update.callback_query, text, kb)
    else:
        await _safe_reply(update, text, kb)

# ─────────────────────────────────────────────────────────────
# /equipment
# ─────────────────────────────────────────────────────────────

async def cmd_equipment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await _safe_reply(update, "❌ Ketik /start untuk mendaftar!")
        return
    rod = RODS.get(player["current_rod"], RODS["rod_bamboo"])
    bait = BAITS.get(player["current_bait"], BAITS["bait_worm"])
    location = MAPS.get(player["current_map"], MAPS["map_kolam"])
    rod_upgrade = get_rod_upgrade(user.id)

    # Count baits
    bait_inv = get_inventory(user.id, "bait")
    bait_count = next((i["quantity"] for i in bait_inv if i["item_id"] == player["current_bait"]), 0)

    text = (
        f"🎣 **EQUIPMENT**\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"**Joran Aktif:**\n"
        f"{rod['emoji']} {rod['name']} [{rod['tier']}]\n"
        f"🔧 Upgrade Level: {rod_upgrade.get('level',0)}\n"
        f"🍀 Luck +{rod.get('luck_bonus',0)+rod_upgrade.get('luck_bonus',0)}%\n"
        f"💎 Rare +{rod.get('rare_bonus',0)+rod_upgrade.get('rare_bonus',0)}%\n\n"
        f"**Umpan Aktif:**\n"
        f"{bait['emoji']} {bait['name']} (sisa: {bait_count})\n"
        f"🍀 Luck +{bait.get('luck_bonus',0)}% | 💎 +{bait.get('rare_bonus',0)}%\n\n"
        f"**Lokasi:**\n"
        f"{location['name']}\n"
    )
    rods_owned = [i["item_id"] for i in get_inventory(user.id, "rod")]
    baits_owned = get_inventory(user.id, "bait")
    kb = equipment_keyboard(rods_owned, player["current_rod"], player["current_bait"], baits_owned)
    await _safe_reply(update, text, kb)

# ─────────────────────────────────────────────────────────────
# /upgrade
# ─────────────────────────────────────────────────────────────

async def cmd_upgrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await _safe_reply(update, "❌ Ketik /start untuk mendaftar!")
        return
    await _show_upgrade_screen(update, player, is_callback=False)

async def _show_upgrade_screen(update, player, is_callback=False):
    upgrade = get_rod_upgrade(player["user_id"])
    current_level = upgrade.get("level", 0)
    max_level = 20
    cost = 500 + (current_level * 250)
    text = (
        f"🔧 **UPGRADE JORAN**\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"⭐ **Level Upgrade:** {current_level} / {max_level}\n"
        f"🍀 **Luck Bonus:** +{upgrade.get('luck_bonus',0)}%\n"
        f"💎 **Rare Bonus:** +{upgrade.get('rare_bonus',0)}%\n"
        f"💰 **Total Dihabiskan:** {fmt_number(upgrade.get('total_spent',0))} 🪙\n\n"
        f"💡 Setiap level upgrade:\n"
        f"   +3% Luck | +2% Rare\n\n"
    )
    if current_level < max_level:
        text += (
            f"**Level berikutnya:** {current_level + 1}\n"
            f"💰 **Biaya:** {fmt_number(cost)} 🪙\n"
            f"🏦 **Koin kamu:** {fmt_number(player['coins'])} 🪙"
        )
    else:
        text += "✅ **Upgrade sudah mencapai level maksimal!**"
    kb = upgrade_keyboard(current_level, cost, max_level)
    if is_callback:
        await _safe_edit(update.callback_query, text, kb)
    else:
        await _safe_reply(update, text, kb)

# ─────────────────────────────────────────────────────────────
# /daily
# ─────────────────────────────────────────────────────────────

async def cmd_daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await _safe_reply(update, "❌ Ketik /start untuk mendaftar!")
        return

    now = datetime.utcnow()
    last_daily_str = player.get("last_daily", "")
    can_claim = True
    if last_daily_str:
        try:
            last_dt = datetime.fromisoformat(last_daily_str)
            if (now - last_dt).total_seconds() < 86400:
                can_claim = False
                next_claim = last_dt + timedelta(hours=24)
                hours_left = int((next_claim - now).total_seconds() / 3600)
                mins_left = int(((next_claim - now).total_seconds() % 3600) / 60)
        except Exception:
            pass

    if not can_claim:
        text = (
            f"🎁 **HADIAH HARIAN**\n\n"
            f"❌ Kamu sudah mengklaim hadiah hari ini!\n\n"
            f"⏳ Klaim berikutnya dalam:\n"
            f"🕐 **{hours_left} jam {mins_left} menit**"
        )
        kb = back_button("cmd_main")
    else:
        # Calculate reward
        base_reward = 200 + (player["level"] * 50)
        vip = is_vip_active(player)
        vip_bonus_coins = 0
        if vip and player.get("vip_type"):
            vip_data = VIP_TIERS.get(player["vip_type"], {})
            vip_bonus_coins = vip_data.get("daily_bonus", 0)
        total_reward = base_reward + vip_bonus_coins

        # Bait reward
        bait_reward = 5 + (player["level"] // 5)

        add_coins(user.id, total_reward)
        add_to_inventory(user.id, "bait", "bait_worm", bait_reward)
        update_player(user.id, last_daily=now.isoformat())

        text = (
            f"🎁 **HADIAH HARIAN**\n\n"
            f"✅ Berhasil klaim hadiah hari ini!\n\n"
            f"🎁 **Hadiah:**\n"
            f"💰 +{fmt_number(total_reward)} Koin\n"
            f"🪱 +{bait_reward}x Cacing Tanah\n"
        )
        if vip_bonus_coins > 0:
            text += f"👑 Bonus VIP: +{fmt_number(vip_bonus_coins)} Koin\n"
        text += f"\n💰 Total Koin: {fmt_number(player['coins'] + total_reward)}"
        kb = back_button("cmd_main")

    await _safe_reply(update, text, kb)

# ─────────────────────────────────────────────────────────────
# /history
# ─────────────────────────────────────────────────────────────

async def cmd_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await _safe_reply(update, "❌ Ketik /start untuk mendaftar!")
        return
    hist = get_history(user.id, 20)
    text = format_history(hist)
    await _safe_reply(update, text, back_button("cmd_main"))

# ─────────────────────────────────────────────────────────────
# /vip
# ─────────────────────────────────────────────────────────────

async def cmd_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await _safe_reply(update, "❌ Ketik /start untuk mendaftar!")
        return
    vip = is_vip_active(player)
    if vip and player.get("vip_type"):
        vip_data = VIP_TIERS.get(player["vip_type"], {})
        try:
            exp_dt = datetime.fromisoformat(player["vip_expires"])
            days_left = max(0, (exp_dt - datetime.utcnow()).days)
        except Exception:
            days_left = 0
        text = (
            f"👑 **STATUS VIP**\n\n"
            f"✅ VIP Aktif!\n"
            f"{vip_data.get('emoji','')} **{vip_data.get('name','')}**\n\n"
            f"📅 Berakhir: {days_left} hari lagi\n\n"
            f"**Bonus Aktif:**\n"
            f"🎁 Bonus Harian: {fmt_number(vip_data.get('daily_bonus',0))} 🪙\n"
            f"🍀 Luck: +{vip_data.get('luck_bonus',0)}%\n"
            f"💎 Rare: +{vip_data.get('rare_bonus',0)}%\n"
            f"⭐ XP: +{vip_data.get('xp_bonus',0)}%\n"
            f"💰 Koin: +{vip_data.get('coin_bonus',0)}%\n"
            f"🎒 Kapasitas Tas: {vip_data.get('bag_slots',50)}\n"
        )
    else:
        text = (
            f"👑 **STATUS VIP**\n\n"
            f"❌ Kamu belum berlangganan VIP\n\n"
            f"**Keuntungan VIP:**\n"
            f"🎁 Bonus harian lebih besar\n"
            f"🍀 Luck & Rare bonus meningkat\n"
            f"⭐ XP & Koin bonus meningkat\n"
            f"🎒 Kapasitas tas lebih besar\n"
            f"⏱ Cooldown lebih cepat (-30%)\n\n"
            f"Pilih paket VIP di bawah:"
        )
    kb = vip_keyboard()
    await _safe_reply(update, text, kb)

# ─────────────────────────────────────────────────────────────
# /shop
# ─────────────────────────────────────────────────────────────

async def cmd_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await _safe_reply(update, "❌ Ketik /start untuk mendaftar!")
        return
    text = (
        f"🛒 **TOKO PERALATAN**\n\n"
        f"💰 Koin kamu: {fmt_number(player['coins'])} 🪙\n\n"
        f"Pilih kategori belanja:"
    )
    await _safe_reply(update, text, shop_menu_keyboard())

# ─────────────────────────────────────────────────────────────
# /market
# ─────────────────────────────────────────────────────────────

async def cmd_market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await _safe_reply(update, "❌ Ketik /start untuk mendaftar!")
        return
    listings = get_market_listings(limit=10)
    text = (
        f"🛒 **PASAR IKAN**\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Koin kamu: {fmt_number(player['coins'])} 🪙\n"
        f"📦 {len(listings)} listing tersedia\n\n"
        f"Pilih filter dan ikan yang ingin dibeli:"
    )
    kb = market_keyboard(listings, 1, 1)
    await _safe_reply(update, text, kb)

# ─────────────────────────────────────────────────────────────
# /favorite
# ─────────────────────────────────────────────────────────────

async def cmd_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await _safe_reply(update, "❌ Ketik /start untuk mendaftar!")
        return
    favs = get_favorites(user.id)
    if not favs:
        text = (
            "⭐ **IKAN FAVORIT**\n\n"
            "Belum ada ikan favorit.\n"
            "Tandai ikan dari tas sebagai favorit!"
        )
    else:
        text = f"⭐ **IKAN FAVORIT** ({len(favs)} ikan)\n\n"
        for f in favs:
            fish = FISH_DATA.get(f["fish_name"], {})
            emoji = fish.get("emoji", "🐟")
            color = RARITY_COLORS.get(f["rarity"], "")
            text += f"{color}{emoji} **{f['fish_name']}** {f['weight']}kg — {rarity_badge(f['rarity'])}\n"
    await _safe_reply(update, text, back_button("cmd_main"))

# ─────────────────────────────────────────────────────────────
# /collection
# ─────────────────────────────────────────────────────────────

async def cmd_collection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await _safe_reply(update, "❌ Ketik /start untuk mendaftar!")
        return
    # Get unique fish caught from history
    from database.db import get_db
    with get_db() as conn:
        rows = conn.execute("""
            SELECT fish_name, rarity, COUNT(*) as count, MAX(weight) as max_weight
            FROM bag WHERE user_id=?
            GROUP BY fish_name ORDER BY rarity DESC, fish_name
        """, (user.id,)).fetchall()

    total_types = len(FISH_DATA)
    found_types = len(rows)

    text = (
        f"🌟 **KOLEKSI IKAN MEWAH**\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 Terkumpul: **{found_types}/{total_types}** jenis\n\n"
    )
    for r in rows:
        fish = FISH_DATA.get(r["fish_name"], {})
        emoji = fish.get("emoji", "🐟")
        color = RARITY_COLORS.get(r["rarity"], "")
        text += f"{color}{emoji} **{r['fish_name']}** x{r['count']} (max {r['max_weight']}kg)\n"

    if not rows:
        text += "Belum ada ikan di koleksi. Mulai memancing! 🎣"

    await _safe_reply(update, text, back_button("cmd_main"))

# ─────────────────────────────────────────────────────────────
# /transfer
# ─────────────────────────────────────────────────────────────

async def cmd_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await _safe_reply(update, "❌ Ketik /start untuk mendaftar!")
        return
    text = (
        f"➡️ **TRANSFER IKAN**\n\n"
        f"Untuk mentransfer ikan ke pemain lain, gunakan:\n\n"
        f"📝 Format: `/transfer [user_id] [bag_id]`\n\n"
        f"Contoh: `/transfer 123456789 42`\n\n"
        f"💡 Cari bag_id dari /bag\n"
        f"💡 User ID bisa dilihat di profil pemain"
    )
    await _safe_reply(update, text, back_button("cmd_main"))

async def cmd_transfer_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /transfer user_id bag_id"""
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        return
    args = context.args
    if len(args) < 2:
        await _safe_reply(update, "❌ Format: `/transfer [user_id] [bag_id]`")
        return
    try:
        target_id = int(args[0])
        bag_id = int(args[1])
    except ValueError:
        await _safe_reply(update, "❌ Format salah! Gunakan: `/transfer [user_id] [bag_id]`")
        return
    if target_id == user.id:
        await _safe_reply(update, "❌ Tidak bisa transfer ke diri sendiri!")
        return
    target = get_player(target_id)
    if not target:
        await _safe_reply(update, "❌ Pemain tujuan tidak ditemukan!")
        return
    bag_item = get_bag_item(bag_id)
    if not bag_item or bag_item["user_id"] != user.id:
        await _safe_reply(update, "❌ Ikan tidak ditemukan di tas kamu!")
        return

    # Do transfer
    remove_from_bag(user.id, bag_id)
    new_bag_id = add_to_bag(target_id, bag_item["fish_name"], bag_item["weight"],
                             bag_item["rarity"], "Transfer")
    add_history(user.id, bag_item["fish_name"], bag_item["weight"],
                bag_item["rarity"], "transfer", 0, "Transfer")

    fish = FISH_DATA.get(bag_item["fish_name"], {})
    emoji = fish.get("emoji", "🐟")
    text = (
        f"✅ **Transfer Berhasil!**\n\n"
        f"{emoji} **{bag_item['fish_name']}** {bag_item['weight']}kg\n"
        f"➡️ Dikirim ke: {target.get('full_name','Unknown')}\n"
    )
    await _safe_reply(update, text, back_button("cmd_main"))

# ─────────────────────────────────────────────────────────────
# /topup
# ─────────────────────────────────────────────────────────────

async def cmd_topup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await _safe_reply(update, "❌ Ketik /start untuk mendaftar!")
        return
    text = (
        f"💰 **TOP UP KOIN**\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Koin saat ini: {fmt_number(player['coins'])} 🪙\n\n"
        f"📋 Pilih paket top up:\n\n"
        f"💡 Pembayaran via transfer bank / e-wallet\n"
        f"📱 Hubungi admin setelah memilih paket"
    )
    await _safe_reply(update, text, topup_keyboard())

# ─────────────────────────────────────────────────────────────
# /event
# ─────────────────────────────────────────────────────────────

async def cmd_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    events = get_active_events()
    all_events = get_all_events()
    if not events:
        text = "🗓 **EVENT**\n\n❌ Tidak ada event yang sedang berlangsung."
    else:
        text = f"🗓 **EVENT AKTIF** ({len(events)} event)\n\n"
        for e in events:
            try:
                end_dt = datetime.fromisoformat(e["end_date"])
                days_left = max(0, (end_dt - datetime.utcnow()).days)
            except Exception:
                days_left = 0
            text += (
                f"🎉 **{e['title']}**\n"
                f"📝 {e['description']}\n"
                f"🎁 Hadiah: {e['reward']}\n"
                f"⏳ Berakhir dalam: {days_left} hari\n\n"
            )
    await _safe_reply(update, text, back_button("cmd_main"))

# ─────────────────────────────────────────────────────────────
# /leaderboard
# ─────────────────────────────────────────────────────────────

async def cmd_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _show_leaderboard(update, context, "coins", is_callback=False)

async def _show_leaderboard(update, context, category: str, is_callback=False):
    cat_map = {
        "coins": ("💰 Koin Terbanyak", "coins"),
        "level": ("⭐ Level Tertinggi", "level"),
        "caught": ("🐟 Tangkapan Terbanyak", "total_caught"),
        "earned": ("💎 Penghasilan Terbesar", "total_earned"),
    }
    label, db_col = cat_map.get(category, cat_map["coins"])
    data = get_leaderboard(db_col, 10)
    medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7

    text = f"🏆 **LEADERBOARD - {label}**\n\n"
    for i, row in enumerate(data):
        medal = medals[i] if i < len(medals) else f"{i+1}."
        name = row.get("full_name", row.get("username", "Unknown"))[:20]
        val = fmt_number(row["value"])
        text += f"{medal} **{name}** — {val}\n"

    if not data:
        text += "Belum ada data."

    kb = leaderboard_keyboard(category)
    if is_callback:
        await _safe_edit(update.callback_query, text, kb)
    else:
        await _safe_reply(update, text, kb)

# ─────────────────────────────────────────────────────────────
# /group /channel
# ─────────────────────────────────────────────────────────────

async def cmd_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"👥 **GRUP & CHANNEL**\n\n"
        f"Bergabunglah dengan komunitas kami!\n\n"
        f"📢 Channel: {CHANNEL_LINK}\n"
        f"💬 Grup: {GROUP_LINK}\n\n"
        f"Dapatkan info update terbaru, event, dan tips memancing!"
    )
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 Channel", url=CHANNEL_LINK),
            InlineKeyboardButton("💬 Grup", url=GROUP_LINK),
        ],
        [InlineKeyboardButton("◀️ Menu Utama", callback_data="cmd_main")],
    ])
    await _safe_reply(update, text, kb)

# ─────────────────────────────────────────────────────────────
# /help
# ─────────────────────────────────────────────────────────────

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"⛑ **BANTUAN - FISHING WORLD**\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"**📋 DAFTAR PERINTAH:**\n\n"
        f"📥 /start — Daftar / Menu Utama\n"
        f"👤 /profil — Info pemain\n"
        f"🎣 /fishing — Mulai memancing\n"
        f"🗺 /map — Pilih lokasi\n"
        f"🍾 /boost — Aktifkan boost\n"
        f"🎒 /bag — Lihat tas ikan\n"
        f"🎣 /equipment — Ganti peralatan\n"
        f"🔧 /upgrade — Upgrade joran\n"
        f"🎁 /daily — Hadiah harian\n"
        f"📖 /history — Histori tangkapan\n"
        f"👑 /vip — Status VIP\n"
        f"🛒 /shop — Beli peralatan\n"
        f"🛒 /market — Jual/beli ikan\n"
        f"⭐ /favorite — Ikan favorit\n"
        f"🌟 /collection — Koleksi ikan\n"
        f"➡️ /transfer — Transfer ikan\n"
        f"💰 /topup — Beli koin\n"
        f"🗓 /event — Info event\n"
        f"🏆 /leaderboard — Peringkat\n"
        f"👥 /group — Grup & Channel\n\n"
        f"**💡 TIPS:**\n"
        f"• Gunakan umpan & joran terbaik\n"
        f"• Aktifkan boost untuk rare+\n"
        f"• Buka peta baru untuk ikan langka\n"
        f"• Jual ikan di market untuk harga lebih baik\n"
    )
    await _safe_reply(update, text, back_button("cmd_main"))

# ─────────────────────────────────────────────────────────────
# CALLBACK QUERY HANDLER
# ─────────────────────────────────────────────────────────────

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user

    # ── MAIN MENU ──
    if data == "cmd_main":
        player = get_player(user.id)
        if not player:
            await _safe_edit(query, "❌ Ketik /start untuk mendaftar!")
            return
        text = (
            f"🎣 **FISHING WORLD**\n\n"
            f"Selamat datang, **{user.first_name}**! 👋\n\n"
            f"💰 Koin: {fmt_number(player['coins'])}\n"
            f"⭐ Level: {player['level']}\n\n"
            f"Pilih menu:"
        )
        await _safe_edit(query, text, main_menu_keyboard())

    # ── FISHING ──
    elif data == "cmd_fishing":
        player = get_player(user.id)
        if not player:
            return
        await _show_fishing_screen(update, context, player, is_callback=True)

    elif data == "do_fishing":
        await do_fishing_action(update, context)

    elif data == "fishing_wait":
        cd = _get_cooldown_left(context, user.id)
        await query.answer(f"⏳ Masih cooldown {cd} detik!", show_alert=True)

    # ── SELL FISH ──
    elif data.startswith("sell_fish_"):
        bag_id = int(data.split("_")[-1])
        item = get_bag_item(bag_id)
        if not item or item["user_id"] != user.id:
            await query.answer("❌ Ikan tidak ditemukan!", show_alert=True)
            return
        player = get_player(user.id)
        boost = get_total_boost(user.id)
        vip_b = get_vip_bonus(player)
        from utils.fishing_engine import calculate_coin_reward
        coins = calculate_coin_reward(
            item["fish_name"], item["weight"],
            boost.get("coin", 0), vip_b.get("coin", 0)
        )
        remove_from_bag(user.id, bag_id)
        add_coins(user.id, coins)
        update_player(user.id,
            total_sold=player["total_sold"] + 1,
            total_earned=player["total_earned"] + coins
        )
        add_history(user.id, item["fish_name"], item["weight"],
                    item["rarity"], "sell", coins, item.get("location",""))
        fish = FISH_DATA.get(item["fish_name"], {})
        await _safe_edit(query,
            f"💰 **IKAN TERJUAL!**\n\n"
            f"{fish.get('emoji','🐟')} **{item['fish_name']}** {item['weight']}kg\n"
            f"💰 Kamu mendapat: **{fmt_number(coins)} 🪙**\n\n"
            f"💰 Total koin: {fmt_number(player['coins'] + coins)}",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("🎣 Mancing Lagi", callback_data="do_fishing")],
                [InlineKeyboardButton("🎒 Lihat Tas", callback_data="cmd_bag")],
                [InlineKeyboardButton("◀️ Menu", callback_data="cmd_main")],
            ])
        )

    elif data == "sell_all":
        player = get_player(user.id)
        items = get_bag(user.id, limit=500)
        if not items:
            await query.answer("Tas kosong!", show_alert=True)
            return
        boost = get_total_boost(user.id)
        vip_b = get_vip_bonus(player)
        from utils.fishing_engine import calculate_coin_reward
        total_coins = 0
        for item in items:
            if not item.get("is_favorite"):
                coins = calculate_coin_reward(item["fish_name"], item["weight"],
                                               boost.get("coin",0), vip_b.get("coin",0))
                total_coins += coins
                remove_from_bag(user.id, item["id"])
                add_history(user.id, item["fish_name"], item["weight"],
                            item["rarity"], "sell", coins, item.get("location",""))
        add_coins(user.id, total_coins)
        update_player(user.id, total_earned=player["total_earned"] + total_coins)
        await _safe_edit(query,
            f"💰 **SEMUA IKAN TERJUAL!**\n\n"
            f"💰 Total koin: **{fmt_number(total_coins)} 🪙**\n"
            f"(Ikan favorit tidak dijual)",
            back_button("cmd_main")
        )

    # ── FAVORITE ──
    elif data.startswith("fav_fish_"):
        bag_id = int(data.split("_")[-1])
        ok = toggle_favorite(user.id, bag_id)
        if ok:
            item = get_bag_item(bag_id)
            label = "⭐ Ditambahkan ke favorit!" if item and item.get("is_favorite") else "💔 Dihapus dari favorit"
            await query.answer(label, show_alert=True)
            if item:
                await _safe_edit(query,
                    f"⭐ **{item['fish_name']}** {item['weight']}kg\n{rarity_badge(item['rarity'])}\n\n{label}",
                    bag_item_keyboard(bag_id, bool(item.get("is_favorite")))
                )
        else:
            await query.answer("❌ Error", show_alert=True)

    # ── BAG ──
    elif data == "cmd_bag":
        await _show_bag(update, context, user.id, page=1, is_callback=True)

    elif data.startswith("bag_page_"):
        page = int(data.split("_")[-1])
        await _show_bag(update, context, user.id, page=page, is_callback=True)

    elif data.startswith("bag_item_"):
        bag_id = int(data.split("_")[-1])
        item = get_bag_item(bag_id)
        if not item or item["user_id"] != user.id:
            await query.answer("❌ Tidak ditemukan", show_alert=True)
            return
        fish = FISH_DATA.get(item["fish_name"], {})
        emoji = fish.get("emoji", "🐟")
        text = (
            f"{emoji} **{item['fish_name']}**\n\n"
            f"🏅 {rarity_badge(item['rarity'])}\n"
            f"⚖️ Berat: {item['weight']} kg\n"
            f"📍 Lokasi: {item.get('location','?')}\n"
            f"🕒 Ditangkap: {str(item.get('caught_at',''))[:16]}\n"
        )
        await _safe_edit(query, text, bag_item_keyboard(bag_id, bool(item.get("is_favorite"))))

    # ── MARKET ──
    elif data.startswith("market_filter_"):
        filt = data.split("market_filter_")[1]
        rarity_f = None if filt == "all" else filt
        listings = get_market_listings(rarity_f, 10)
        player = get_player(user.id)
        text = (
            f"🛒 **PASAR IKAN**\n"
            f"💰 Koin: {fmt_number(player['coins'])} 🪙\n"
            f"📦 {len(listings)} listing\n\n"
            f"Filter: {'Semua' if not rarity_f else rarity_f}"
        )
        await _safe_edit(query, text, market_keyboard(listings))

    elif data.startswith("buy_market_"):
        listing_id = int(data.split("_")[-1])
        result = buy_market_item(user.id, listing_id)
        if result["success"]:
            listing = result["listing"]
            fish = FISH_DATA.get(listing["fish_name"], {})
            await _safe_edit(query,
                f"✅ **PEMBELIAN BERHASIL!**\n\n"
                f"{fish.get('emoji','🐟')} **{listing['fish_name']}** {listing['weight']}kg\n"
                f"💰 Dibayar: {fmt_number(listing['price'])} 🪙",
                back_button("cmd_market")
            )
        else:
            await query.answer(f"❌ {result['error']}", show_alert=True)

    elif data.startswith("market_list_"):
        bag_id = int(data.split("_")[-1])
        item = get_bag_item(bag_id)
        if not item or item["user_id"] != user.id:
            await query.answer("❌ Tidak ditemukan", show_alert=True)
            return
        fish_d = FISH_DATA.get(item["fish_name"], {})
        suggested = fish_d.get("base_price", 100)
        context.user_data["market_pending"] = bag_id
        text = (
            f"🛒 **JUAL DI MARKET**\n\n"
            f"{fish_d.get('emoji','🐟')} **{item['fish_name']}** {item['weight']}kg\n"
            f"🏅 {rarity_badge(item['rarity'])}\n\n"
            f"💡 Harga NPC: {fmt_number(fish_d.get('sell_price',50))} 🪙\n"
            f"💡 Harga Pasaran: ~{fmt_number(suggested)} 🪙\n\n"
            f"Balas dengan angka harga yang diinginkan:"
        )
        await _safe_edit(query, text, back_button("cmd_market"))

    elif data == "market_sell_menu":
        text = (
            "📦 **JUAL IKAN DI MARKET**\n\n"
            "Pilih ikan dari /bag lalu tekan 'Jual di Market'."
        )
        await _safe_edit(query, text, back_button("cmd_market"))

    # ── SHOP ──
    elif data == "cmd_shop":
        player = get_player(user.id)
        text = f"🛒 **TOKO PERALATAN**\n\n💰 Koin: {fmt_number(player['coins'])} 🪙\n\nPilih kategori:"
        await _safe_edit(query, text, shop_menu_keyboard())

    elif data == "shop_rods":
        text = format_shop_rods()
        rods_kb = []
        player = get_player(user.id)
        for rod_id, rod in RODS.items():
            owned = has_item(user.id, rod_id)
            if owned:
                label = f"✅ {rod['emoji']} {rod['name']} (Dimiliki)"
            elif rod["price"] == 0:
                label = f"🆓 {rod['emoji']} {rod['name']}"
            else:
                label = f"🛒 {rod['emoji']} {rod['name']} — {fmt_number(rod['price'])}🪙"
            rods_kb.append([InlineKeyboardButton(label, callback_data=f"buy_rod_{rod_id}")])
        rods_kb.append([InlineKeyboardButton("◀️ Kembali ke Shop", callback_data="cmd_shop")])
        await _safe_edit(query, text, InlineKeyboardMarkup(rods_kb))

    elif data.startswith("buy_rod_"):
        rod_id = data.split("buy_rod_")[1]
        rod = RODS.get(rod_id)
        if not rod:
            await query.answer("❌ Joran tidak ditemukan", show_alert=True)
            return
        player = get_player(user.id)
        if has_item(user.id, rod_id):
            await query.answer("✅ Sudah dimiliki!", show_alert=True)
            return
        if player["level"] < rod["level_req"]:
            await query.answer(f"❌ Level {rod['level_req']} diperlukan!", show_alert=True)
            return
        if rod["price"] == 0 or spend_coins(user.id, rod["price"]):
            add_to_inventory(user.id, "rod", rod_id, 1)
            await query.answer(f"✅ {rod['name']} berhasil dibeli!", show_alert=True)
        else:
            await query.answer(f"❌ Koin tidak cukup! Butuh {fmt_number(rod['price'])} 🪙", show_alert=True)

    elif data == "shop_baits":
        text = format_shop_baits()
        baits_kb = []
        for bait_id, bait in BAITS.items():
            qty = bait.get("quantity", 1)
            qty_txt = f" x{qty}" if qty > 1 else ""
            label = f"🛒 {bait['emoji']} {bait['name']}{qty_txt} — {fmt_number(bait['price'])}🪙"
            baits_kb.append([InlineKeyboardButton(label, callback_data=f"buy_bait_{bait_id}")])
        baits_kb.append([InlineKeyboardButton("◀️ Kembali ke Shop", callback_data="cmd_shop")])
        await _safe_edit(query, text, InlineKeyboardMarkup(baits_kb))

    elif data.startswith("buy_bait_"):
        bait_id = data.split("buy_bait_")[1]
        bait = BAITS.get(bait_id)
        if not bait:
            await query.answer("❌ Umpan tidak ditemukan", show_alert=True)
            return
        player = get_player(user.id)
        if spend_coins(user.id, bait["price"]):
            qty = bait.get("quantity", 1)
            # Map bundle to base bait
            base_bait_id = bait_id.split("_")[0] + "_" + bait_id.split("_")[1]
            if bait_id.endswith("_10") or bait_id.endswith("_5"):
                base_bait_id = "_".join(bait_id.split("_")[:2])
            add_to_inventory(user.id, "bait", base_bait_id, qty)
            await query.answer(f"✅ {bait['name']} x{qty} berhasil dibeli!", show_alert=True)
        else:
            await query.answer(f"❌ Koin tidak cukup! Butuh {fmt_number(bait['price'])} 🪙", show_alert=True)

    elif data == "shop_boosts":
        boosts_kb = []
        for boost_id, boost in BOOSTS.items():
            label = f"🛒 {boost['emoji']} {boost['name']} — {fmt_number(boost['price'])}🪙"
            boosts_kb.append([InlineKeyboardButton(label, callback_data=f"buy_boost_{boost_id}")])
        boosts_kb.append([InlineKeyboardButton("◀️ Kembali ke Shop", callback_data="cmd_shop")])
        text = "🍾 **TOKO BOOST**\n\nPilih boost:"
        await _safe_edit(query, text, InlineKeyboardMarkup(boosts_kb))

    elif data.startswith("buy_boost_"):
        boost_id = data.split("buy_boost_")[1]
        boost = BOOSTS.get(boost_id)
        if not boost:
            await query.answer("❌ Boost tidak ditemukan", show_alert=True)
            return
        player = get_player(user.id)
        if boost_id == "boost_vip" and not is_vip_active(player):
            await query.answer("❌ Boost ini khusus VIP!", show_alert=True)
            return
        if spend_coins(user.id, boost["price"]):
            add_to_inventory(user.id, "boost", boost_id, 1)
            await query.answer(f"✅ {boost['name']} berhasil dibeli!", show_alert=True)
        else:
            await query.answer(f"❌ Koin tidak cukup! Butuh {fmt_number(boost['price'])} 🪙", show_alert=True)

    elif data == "shop_vip":
        await _safe_edit(query, "👑 **PILIH PAKET VIP:**", vip_keyboard())

    # ── BOOST ACTIVATE ──
    elif data == "cmd_boost":
        player = get_player(user.id)
        active = get_active_boosts(user.id)
        total = get_total_boost(user.id)
        text = format_boost_status(active, total)
        boosts_owned = get_inventory(user.id, "boost")
        await _safe_edit(query, text, boost_keyboard(boosts_owned))

    elif data.startswith("use_boost_"):
        boost_id = data.split("use_boost_")[1]
        boost = BOOSTS.get(boost_id)
        if not boost:
            await query.answer("❌ Boost tidak ditemukan", show_alert=True)
            return
        if not has_item(user.id, boost_id):
            await query.answer("❌ Boost tidak ada di inventory!", show_alert=True)
            return
        use_inventory_item(user.id, boost_id, 1)
        activate_boost(
            user.id, boost_id, boost["name"],
            boost["luck_bonus"], boost["rare_bonus"],
            boost["xp_bonus"], boost["coin_bonus"],
            boost["duration"]
        )
        await query.answer(f"✅ {boost['name']} aktif selama {boost['duration']} menit!", show_alert=True)
        # Refresh boost screen
        active = get_active_boosts(user.id)
        total = get_total_boost(user.id)
        text = format_boost_status(active, total)
        boosts_owned = get_inventory(user.id, "boost")
        await _safe_edit(query, text, boost_keyboard(boosts_owned))

    # ── MAP ──
    elif data == "cmd_map":
        player = get_player(user.id)
        unlocked = get_unlocked_maps(user.id)
        text = "🗺 **PILIH LOKASI MEMANCING**\n\n"
        for map_id, m in MAPS.items():
            status = "✅" if map_id in unlocked else ("🔓" if player["level"] >= m["level_req"] else "🔒")
            text += f"{status} {m['name']} — Rare x{m['rare_multiplier']}\n"
        kb = map_select_keyboard(unlocked, player["level"], MAPS)
        await _safe_edit(query, text, kb)

    elif data.startswith("select_map_"):
        map_id = data.split("select_map_")[1]
        if map_id not in MAPS:
            await query.answer("❌ Lokasi tidak valid", show_alert=True)
            return
        unlocked = get_unlocked_maps(user.id)
        if map_id not in unlocked:
            await query.answer("❌ Lokasi belum dibuka!", show_alert=True)
            return
        update_player(user.id, current_map=map_id)
        m = MAPS[map_id]
        await query.answer(f"✅ Pindah ke {m['name']}!", show_alert=True)
        player = get_player(user.id)
        await _show_fishing_screen(update, context, player, is_callback=True)

    elif data.startswith("unlock_map_"):
        map_id = data.split("unlock_map_")[1]
        m = MAPS.get(map_id)
        if not m:
            await query.answer("❌ Lokasi tidak valid", show_alert=True)
            return
        player = get_player(user.id)
        if player["level"] < m["level_req"]:
            await query.answer(f"❌ Level {m['level_req']} diperlukan!", show_alert=True)
            return
        if spend_coins(user.id, m["unlock_cost"]):
            unlock_map(user.id, map_id)
            await query.answer(f"✅ {m['name']} berhasil dibuka!", show_alert=True)
        else:
            await query.answer(f"❌ Koin tidak cukup! Butuh {fmt_number(m['unlock_cost'])} 🪙", show_alert=True)

    elif data.startswith("locked_map_"):
        map_id = data.split("locked_map_")[1]
        m = MAPS.get(map_id)
        if m:
            await query.answer(f"🔒 Butuh Level {m['level_req']} untuk membuka!", show_alert=True)

    # ── EQUIPMENT ──
    elif data == "cmd_equipment":
        player = get_player(user.id)
        rod = RODS.get(player["current_rod"], RODS["rod_bamboo"])
        bait = BAITS.get(player["current_bait"], BAITS["bait_worm"])
        location = MAPS.get(player["current_map"], MAPS["map_kolam"])
        rod_upgrade = get_rod_upgrade(user.id)
        bait_inv = get_inventory(user.id, "bait")
        bait_count = next((i["quantity"] for i in bait_inv if i["item_id"] == player["current_bait"]), 0)
        text = (
            f"🎣 **EQUIPMENT**\n\n"
            f"**Joran:** {rod['emoji']} {rod['name']} [Upgrade Lv.{rod_upgrade.get('level',0)}]\n"
            f"**Umpan:** {bait['emoji']} {bait['name']} (sisa: {bait_count})\n"
            f"**Lokasi:** {location['name']}\n"
        )
        rods_owned = [i["item_id"] for i in get_inventory(user.id, "rod")]
        baits_owned = get_inventory(user.id, "bait")
        kb = equipment_keyboard(rods_owned, player["current_rod"], player["current_bait"], baits_owned)
        await _safe_edit(query, text, kb)

    elif data == "equip_rod_menu":
        rods_owned = [i["item_id"] for i in get_inventory(user.id, "rod")]
        if not rods_owned:
            await query.answer("❌ Tidak punya joran lain!", show_alert=True)
            return
        await _safe_edit(query, "🎣 **PILIH JORAN:**", rod_select_keyboard(rods_owned))

    elif data.startswith("equip_rod_"):
        rod_id = data.split("equip_rod_")[1]
        if has_item(user.id, rod_id):
            update_player(user.id, current_rod=rod_id)
            rod = RODS.get(rod_id, {})
            await query.answer(f"✅ Joran {rod.get('name','')} dipasang!", show_alert=True)
        else:
            await query.answer("❌ Joran tidak dimiliki!", show_alert=True)

    elif data == "equip_bait_menu":
        baits_owned = get_inventory(user.id, "bait")
        if not baits_owned:
            await query.answer("❌ Tidak punya umpan!", show_alert=True)
            return
        await _safe_edit(query, "🪱 **PILIH UMPAN:**", bait_select_keyboard(baits_owned))

    elif data.startswith("equip_bait_"):
        bait_id = data.split("equip_bait_")[1]
        if has_item(user.id, bait_id):
            update_player(user.id, current_bait=bait_id)
            bait = BAITS.get(bait_id, {})
            await query.answer(f"✅ Umpan {bait.get('name','')} dipasang!", show_alert=True)
        else:
            await query.answer("❌ Umpan tidak dimiliki!", show_alert=True)

    # ── UPGRADE ──
    elif data == "cmd_upgrade":
        player = get_player(user.id)
        await _show_upgrade_screen(update, player, is_callback=True)

    elif data == "do_upgrade":
        player = get_player(user.id)
        result = upgrade_rod(user.id)
        if result["success"]:
            text = (
                f"✅ **UPGRADE BERHASIL!**\n\n"
                f"🔧 Level Upgrade: **{result['new_level']}**\n"
                f"🍀 Luck Bonus: +{result['luck_bonus']}%\n"
                f"💎 Rare Bonus: +{result['rare_bonus']}%\n"
                f"💰 Biaya: {fmt_number(result['cost'])} 🪙"
            )
            player_fresh = get_player(user.id)
            await _safe_edit(query, text, upgrade_keyboard(result["new_level"], 500 + result["new_level"] * 250))
        else:
            await query.answer(f"❌ {result['error']}", show_alert=True)

    elif data == "upgrade_max":
        await query.answer("✅ Upgrade sudah maksimal!", show_alert=True)

    # ── LEADERBOARD ──
    elif data == "cmd_leaderboard":
        await _show_leaderboard(update, context, "coins", is_callback=True)

    elif data.startswith("lb_"):
        cat = data.split("lb_")[1]
        await _show_leaderboard(update, context, cat, is_callback=True)

    # ── DAILY ──
    elif data == "cmd_daily":
        # Simulate command
        class FakeMsg:
            effective_user = query.from_user
            class message:
                @staticmethod
                async def reply_text(text, **kwargs):
                    await query.edit_message_text(text, **kwargs)
        # Just call the logic inline
        user_obj = query.from_user
        player = get_player(user_obj.id)
        now = datetime.utcnow()
        last_daily_str = player.get("last_daily", "")
        can_claim = True
        hours_left = 0
        mins_left = 0
        if last_daily_str:
            try:
                last_dt = datetime.fromisoformat(last_daily_str)
                if (now - last_dt).total_seconds() < 86400:
                    can_claim = False
                    next_claim = last_dt + timedelta(hours=24)
                    hours_left = int((next_claim - now).total_seconds() / 3600)
                    mins_left = int(((next_claim - now).total_seconds() % 3600) / 60)
            except Exception:
                pass
        if not can_claim:
            text = f"🎁 **HADIAH HARIAN**\n\n❌ Sudah diklaim hari ini!\n⏳ Klaim lagi: **{hours_left}j {mins_left}m**"
        else:
            base_reward = 200 + (player["level"] * 50)
            vip = is_vip_active(player)
            vip_bonus_coins = 0
            if vip and player.get("vip_type"):
                vip_data = VIP_TIERS.get(player["vip_type"], {})
                vip_bonus_coins = vip_data.get("daily_bonus", 0)
            total_reward = base_reward + vip_bonus_coins
            bait_reward = 5 + (player["level"] // 5)
            add_coins(user_obj.id, total_reward)
            add_to_inventory(user_obj.id, "bait", "bait_worm", bait_reward)
            update_player(user_obj.id, last_daily=now.isoformat())
            text = (
                f"🎁 **HADIAH HARIAN**\n\n✅ Berhasil diklaim!\n\n"
                f"💰 +{fmt_number(total_reward)} Koin\n"
                f"🪱 +{bait_reward}x Cacing\n"
            )
            if vip_bonus_coins > 0:
                text += f"👑 Bonus VIP: +{fmt_number(vip_bonus_coins)} Koin\n"
        await _safe_edit(query, text, back_button("cmd_main"))

    # ── VIP ──
    elif data == "cmd_vip":
        player = get_player(user.id)
        vip = is_vip_active(player)
        if vip and player.get("vip_type"):
            vip_data = VIP_TIERS.get(player["vip_type"], {})
            try:
                days_left = max(0, (datetime.fromisoformat(player["vip_expires"]) - datetime.utcnow()).days)
            except Exception:
                days_left = 0
            text = (
                f"👑 **STATUS VIP**\n\n✅ VIP Aktif!\n"
                f"{vip_data.get('emoji','')} {vip_data.get('name','')}\n"
                f"📅 Sisa: {days_left} hari\n\n"
                f"🎁 Daily: {fmt_number(vip_data.get('daily_bonus',0))} 🪙\n"
                f"🍀 +{vip_data.get('luck_bonus',0)}% | 💎 +{vip_data.get('rare_bonus',0)}%"
            )
        else:
            text = "👑 **STATUS VIP**\n\n❌ Belum berlangganan VIP\n\nPilih paket:"
        await _safe_edit(query, text, vip_keyboard())

    elif data.startswith("buy_vip_"):
        vip_id = data.split("buy_vip_")[1]
        vip = VIP_TIERS.get(vip_id)
        if not vip:
            await query.answer("❌ Paket tidak valid", show_alert=True)
            return
        player = get_player(user.id)
        if spend_coins(user.id, vip["price"]):
            now = datetime.utcnow()
            # Extend if already VIP
            if is_vip_active(player) and player.get("vip_type") == vip_id:
                try:
                    current_exp = datetime.fromisoformat(player["vip_expires"])
                    new_exp = current_exp + timedelta(days=vip["duration_days"])
                except Exception:
                    new_exp = now + timedelta(days=vip["duration_days"])
            else:
                new_exp = now + timedelta(days=vip["duration_days"])
            update_player(user.id, vip_type=vip_id, vip_expires=new_exp.isoformat())
            await query.answer(f"✅ {vip['name']} aktif selama {vip['duration_days']} hari!", show_alert=True)
        else:
            await query.answer(f"❌ Koin tidak cukup! Butuh {fmt_number(vip['price'])} 🪙", show_alert=True)

    # ── TOPUP ──
    elif data == "cmd_topup":
        player = get_player(user.id)
        text = f"💰 **TOP UP KOIN**\n\n💰 Koin: {fmt_number(player['coins'])} 🪙\n\nPilih paket:"
        await _safe_edit(query, text, topup_keyboard())

    elif data.startswith("topup_topup_"):
        pkg_id = data.split("topup_")[1]
        pkg = TOPUP_PACKAGES.get(pkg_id)
        if not pkg:
            await query.answer("❌ Paket tidak valid", show_alert=True)
            return
        text = (
            f"💰 **TOP UP - {pkg['label']}**\n\n"
            f"💰 Koin: {fmt_number(pkg['coins'])}\n"
            f"💵 Harga: Rp {pkg['price_idr']:,}\n\n"
            f"📱 Hubungi admin untuk proses pembayaran:\n"
            f"Kirim bukti transfer + ID: `{user.id}`"
        )
        await _safe_edit(query, text, back_button("cmd_topup"))

    # ── PROFILE ──
    elif data == "cmd_profile":
        player = get_player(user.id)
        rod_upgrade = get_rod_upgrade(user.id)
        vip = is_vip_active(player)
        text = format_player_profile(player, rod_upgrade, vip)
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎣 Equipment", callback_data="cmd_equipment"),
                InlineKeyboardButton("🔧 Upgrade", callback_data="cmd_upgrade"),
            ],
            [InlineKeyboardButton("◀️ Menu Utama", callback_data="cmd_main")],
        ])
        await _safe_edit(query, text, kb)

    # ── HELP ──
    elif data == "cmd_help":
        text = (
            f"⛑ **BANTUAN**\n\n"
            f"/start — Menu Utama\n/fishing — Memancing\n/shop — Toko\n"
            f"/bag — Tas ikan\n/daily — Hadiah harian\n/help — Bantuan\n\n"
            f"Untuk info lengkap, ketik /help"
        )
        await _safe_edit(query, text, back_button("cmd_main"))

    elif data == "cmd_history":
        hist = get_history(user.id, 20)
        text = format_history(hist)
        await _safe_edit(query, text, back_button("cmd_main"))

    elif data == "cmd_favorite":
        favs = get_favorites(user.id)
        if not favs:
            text = "⭐ **IKAN FAVORIT**\n\nBelum ada ikan favorit."
        else:
            text = f"⭐ **IKAN FAVORIT** ({len(favs)} ikan)\n\n"
            for f in favs:
                fish = FISH_DATA.get(f["fish_name"], {})
                text += f"{fish.get('emoji','🐟')} **{f['fish_name']}** {f['weight']}kg — {rarity_badge(f['rarity'])}\n"
        await _safe_edit(query, text, back_button("cmd_main"))

    elif data == "cmd_collection":
        from database.db import get_db as _gdb
        with _gdb() as conn:
            rows = conn.execute("""
                SELECT fish_name, rarity, COUNT(*) as count, MAX(weight) as max_weight
                FROM bag WHERE user_id=?
                GROUP BY fish_name ORDER BY rarity DESC
            """, (user.id,)).fetchall()
        text = f"🌟 **KOLEKSI IKAN** ({len(rows)}/{len(FISH_DATA)} jenis)\n\n"
        for r in rows:
            fish = FISH_DATA.get(r["fish_name"], {})
            color = RARITY_COLORS.get(r["rarity"], "")
            text += f"{color}{fish.get('emoji','🐟')} **{r['fish_name']}** x{r['count']}\n"
        if not rows:
            text += "Belum ada koleksi. Mulai memancing! 🎣"
        await _safe_edit(query, text, back_button("cmd_main"))

    elif data == "cmd_event":
        events = get_active_events()
        if not events:
            text = "🗓 **EVENT**\n\n❌ Tidak ada event aktif."
        else:
            text = f"🗓 **EVENT AKTIF** ({len(events)} event)\n\n"
            for e in events:
                try:
                    days_left = max(0, (datetime.fromisoformat(e["end_date"]) - datetime.utcnow()).days)
                except Exception:
                    days_left = 0
                text += f"🎉 **{e['title']}**\n📝 {e['description']}\n⏳ {days_left} hari\n\n"
        await _safe_edit(query, text, back_button("cmd_main"))

    elif data == "cmd_group":
        text = f"👥 **GRUP & CHANNEL**\n\n📢 Channel: {CHANNEL_LINK}\n💬 Grup: {GROUP_LINK}"
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📢 Channel", url=CHANNEL_LINK),
                InlineKeyboardButton("💬 Grup", url=GROUP_LINK),
            ],
            [InlineKeyboardButton("◀️ Menu", callback_data="cmd_main")],
        ])
        await _safe_edit(query, text, kb)

    elif data == "cmd_market":
        player = get_player(user.id)
        listings = get_market_listings(limit=10)
        text = (
            f"🛒 **PASAR IKAN**\n\n"
            f"💰 Koin: {fmt_number(player['coins'])} 🪙\n"
            f"📦 {len(listings)} listing tersedia"
        )
        await _safe_edit(query, text, market_keyboard(listings))

    # ── TRANSFER via callback (show info) ──
    elif data == "cmd_transfer":
        text = (
            f"➡️ **TRANSFER IKAN**\n\n"
            f"Gunakan: `/transfer [user_id] [bag_id]`\n\n"
            f"Contoh: `/transfer 123456 42`"
        )
        await _safe_edit(query, text, back_button("cmd_main"))

    else:
        logger.warning(f"Unknown callback: {data}")

# ─────────────────────────────────────────────────────────────
# MESSAGE HANDLER (for market price input)
# ─────────────────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        return

    pending_bag_id = context.user_data.get("market_pending")
    if pending_bag_id and update.message.text:
        text = update.message.text.strip()
        if text.isdigit():
            price = int(text)
            item = get_bag_item(pending_bag_id)
            if item and item["user_id"] == user.id:
                if price < 1:
                    await update.message.reply_text("❌ Harga harus minimal 1 koin!")
                    return
                remove_from_bag(user.id, pending_bag_id)
                list_market_item(user.id, pending_bag_id, item["fish_name"],
                                  item["weight"], item["rarity"], price)
                context.user_data.pop("market_pending", None)
                fish = FISH_DATA.get(item["fish_name"], {})
                await update.message.reply_text(
                    f"✅ **Berhasil didaftarkan ke Market!**\n\n"
                    f"{fish.get('emoji','🐟')} **{item['fish_name']}** {item['weight']}kg\n"
                    f"💰 Harga: {fmt_number(price)} 🪙",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=back_button("cmd_market")
                )
                return
        context.user_data.pop("market_pending", None)
