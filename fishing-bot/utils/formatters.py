from datetime import datetime
from typing import Dict, Optional
from data.fish_data import RARITY_COLORS, RARITY_EMOJIS, FISH_DATA
from data.shop_data import RODS, BAITS, MAPS, VIP_TIERS, get_level_title, xp_for_level


def fmt_number(n) -> str:
    try:
        return f"{int(n):,}"
    except Exception:
        return str(n)


def rarity_badge(rarity: str) -> str:
    colors = {
        "Common":    "⬜ Common",
        "Uncommon":  "🟩 Uncommon",
        "Rare":      "🟦 Rare",
        "Epic":      "🟪 Epic",
        "Legendary": "🟧 Legendary",
        "Mythic":    "🔴 Mythic",
        "Divine":    "✨ Divine",
    }
    return colors.get(rarity, rarity)


def format_player_profile(player: Dict, rod_upgrade: Dict, vip_active: bool) -> str:
    level = player["level"]
    title = get_level_title(level)
    xp = player["xp"]
    xp_needed = xp_for_level(level + 1)
    xp_pct = int((xp / xp_needed) * 20)
    xp_bar = "█" * xp_pct + "░" * (20 - xp_pct)

    rod = RODS.get(player["current_rod"], RODS["rod_bamboo"])
    bait = BAITS.get(player["current_bait"], BAITS["bait_worm"])
    location = MAPS.get(player["current_map"], MAPS["map_kolam"])

    vip_status = ""
    if vip_active and player.get("vip_type"):
        vip = VIP_TIERS.get(player["vip_type"], {})
        expires = player.get("vip_expires", "")
        try:
            exp_dt = datetime.fromisoformat(expires)
            days_left = (exp_dt - datetime.utcnow()).days
        except Exception:
            days_left = 0
        vip_status = f"\n👑 **VIP:** {vip.get('emoji','')} {vip.get('name','')} ({days_left} hari lagi)"

    upgrade_level = rod_upgrade.get("level", 0)
    join_date = player.get("joined_at", "")[:10]

    text = (
        f"╔══════════════════════╗\n"
        f"║  👤 **PROFIL PEMANCING**  ║\n"
        f"╚══════════════════════╝\n\n"
        f"🏅 **{title}**\n"
        f"👤 **Nama:** {player.get('full_name','Unknown')}\n"
        f"🆔 **ID:** `{player['user_id']}`\n"
        f"📅 **Bergabung:** {join_date}\n"
        f"{vip_status}\n\n"
        f"━━━━━━ 📊 STATISTIK ━━━━━━\n"
        f"⭐ **Level:** {level}\n"
        f"📈 **XP:** {fmt_number(xp)} / {fmt_number(xp_needed)}\n"
        f"[{xp_bar}]\n\n"
        f"💰 **Koin:** {fmt_number(player['coins'])} 🪙\n"
        f"🐟 **Total Tangkapan:** {fmt_number(player['total_caught'])}\n"
        f"💰 **Total Penghasilan:** {fmt_number(player['total_earned'])} 🪙\n\n"
        f"━━━━━━ 🎣 EQUIPMENT ━━━━━━\n"
        f"🎣 **Joran:** {rod['emoji']} {rod['name']}\n"
        f"🔧 **Upgrade Joran:** Lv.{upgrade_level}\n"
        f"🪱 **Umpan:** {bait['emoji']} {bait['name']}\n"
        f"🗺 **Lokasi:** {location['name']}\n"
    )
    return text


def format_fish_catch(fish_name: str, rarity: str, weight: float,
                      xp_earned: int, location: str, is_new_record: bool = False) -> str:
    fish = FISH_DATA.get(fish_name, {})
    emoji = fish.get("emoji", "🐟")
    badge = rarity_badge(rarity)
    rare_anim = ""
    if rarity in ["Mythic", "Divine"]:
        rare_anim = "\n🌟✨🌟 **TANGKAPAN LUAR BIASA!!!** 🌟✨🌟\n"
    elif rarity in ["Legendary"]:
        rare_anim = "\n🔥🏆 **TANGKAPAN LEGENDARIS!!** 🏆🔥\n"
    elif rarity in ["Epic"]:
        rare_anim = "\n💜 **TANGKAPAN EPIC!!** 💜\n"

    record_txt = "\n🏆 **REKOR BARU BERAT!** 🏆" if is_new_record else ""

    return (
        f"{rare_anim}"
        f"┌─────────────────────┐\n"
        f"│  🎣 **IKAN TERTANGKAP!**  │\n"
        f"└─────────────────────┘\n\n"
        f"{emoji} **{fish_name}**\n"
        f"🏅 **Rarity:** {badge}\n"
        f"⚖️ **Berat:** {weight} kg{record_txt}\n"
        f"✨ **XP:** +{fmt_number(xp_earned)}\n"
        f"📍 **Lokasi:** {location}\n"
    )


def format_bag(items, page: int, total: int, per_page: int = 10) -> str:
    if not items:
        return (
            "🎒 **TAS KOSONG**\n\n"
            "Belum ada ikan di dalam tas.\n"
            "Pergi memancing dulu! 🎣"
        )
    start = (page - 1) * per_page + 1
    lines = [f"🎒 **TAS IKAN** (Total: {total} ekor)\n"]
    for i, item in enumerate(items, start=start):
        fish = FISH_DATA.get(item["fish_name"], {})
        emoji = fish.get("emoji", "🐟")
        color = RARITY_COLORS.get(item["rarity"], "")
        fav = "⭐" if item.get("is_favorite") else ""
        lines.append(
            f"{i}. {color}{fav}{emoji} **{item['fish_name']}**\n"
            f"   ⚖️ {item['weight']}kg | {rarity_badge(item['rarity'])}\n"
        )
    return "\n".join(lines)


def format_boost_status(active_boosts, total_boost: Dict) -> str:
    if not active_boosts:
        return (
            "🍾 **BOOST AKTIF**\n\n"
            "❌ Tidak ada boost yang aktif.\n"
            "Beli boost di /shop untuk meningkatkan peluang!"
        )

    lines = ["🍾 **BOOST AKTIF**\n"]
    now = datetime.utcnow()
    for b in active_boosts:
        try:
            exp = datetime.fromisoformat(b["expires_at"])
            remaining = int((exp - now).total_seconds() / 60)
            lines.append(
                f"✅ **{b['boost_name']}**\n"
                f"   ⏳ Sisa: {remaining} menit\n"
            )
        except Exception:
            pass

    lines.append(f"\n📊 **Total Bonus:**")
    lines.append(f"🍀 Luck: +{total_boost.get('luck',0)}%")
    lines.append(f"💎 Rare: +{total_boost.get('rare',0)}%")
    lines.append(f"⭐ XP: +{total_boost.get('xp',0)}%")
    lines.append(f"💰 Koin: +{total_boost.get('coin',0)}%")
    return "\n".join(lines)


def format_shop_rods() -> str:
    lines = ["🎣 **TOKO JORAN**\n", "━━━━━━━━━━━━━━━━━━━━\n"]
    from data.shop_data import RODS
    for rod_id, rod in RODS.items():
        price_txt = "🆓 Gratis" if rod["price"] == 0 else f"{fmt_number(rod['price'])} 🪙"
        lines.append(
            f"{rod['emoji']} **{rod['name']}** [{rod['tier']}]\n"
            f"   💰 {price_txt} | Lv.{rod['level_req']} required\n"
            f"   🍀 Luck +{rod['luck_bonus']}% | 💎 Rare +{rod['rare_bonus']}%\n"
            f"   📝 {rod['description']}\n"
        )
    return "\n".join(lines)


def format_shop_baits() -> str:
    lines = ["🪱 **TOKO UMPAN**\n", "━━━━━━━━━━━━━━━━━━━━\n"]
    from data.shop_data import BAITS
    for bait_id, bait in BAITS.items():
        qty = bait.get("quantity", 1)
        qty_txt = f" (x{qty})" if qty > 1 else ""
        lines.append(
            f"{bait['emoji']} **{bait['name']}{qty_txt}** [{bait['tier']}]\n"
            f"   💰 {fmt_number(bait['price'])} 🪙\n"
            f"   🍀 +{bait['luck_bonus']}% | 💎 +{bait['rare_bonus']}%\n"
            f"   📝 {bait['description']}\n"
        )
    return "\n".join(lines)


def format_history(history_items) -> str:
    if not history_items:
        return "📖 **HISTORI KOSONG**\n\nBelum ada aktivitas."

    lines = ["📖 **HISTORI TANGKAPAN (20 Terakhir)**\n", "━━━━━━━━━━━━━━━━━━━━\n"]
    for h in history_items:
        fish = FISH_DATA.get(h["fish_name"], {})
        emoji = fish.get("emoji", "🐟")
        action_map = {
            "catch": "🎣 Ditangkap",
            "sell": "💰 Dijual",
            "transfer": "➡️ Transfer",
        }
        action = action_map.get(h["action"], h["action"])
        date = h.get("created_at", "")[:16].replace("T", " ")
        earn_txt = f" +{fmt_number(h['coins_earned'])}🪙" if h.get("coins_earned") else ""
        lines.append(
            f"{emoji} **{h['fish_name']}** {h['weight']}kg\n"
            f"   {rarity_badge(h['rarity'])} | {action}{earn_txt}\n"
            f"   📍 {h.get('location','?')} | 🕒 {date}\n"
        )
    return "\n".join(lines)
