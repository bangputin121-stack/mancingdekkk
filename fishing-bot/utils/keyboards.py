from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎣 Mancing", callback_data="cmd_fishing"),
            InlineKeyboardButton("🗺 Peta", callback_data="cmd_map"),
        ],
        [
            InlineKeyboardButton("🛒 Shop", callback_data="cmd_shop"),
            InlineKeyboardButton("🎒 Tas", callback_data="cmd_bag"),
        ],
        [
            InlineKeyboardButton("👤 Profil", callback_data="cmd_profile"),
            InlineKeyboardButton("🏆 Ranking", callback_data="cmd_leaderboard"),
        ],
        [
            InlineKeyboardButton("🎁 Daily", callback_data="cmd_daily"),
            InlineKeyboardButton("🍾 Boost", callback_data="cmd_boost"),
        ],
        [
            InlineKeyboardButton("📖 History", callback_data="cmd_history"),
            InlineKeyboardButton("⭐ Favorit", callback_data="cmd_favorite"),
        ],
        [
            InlineKeyboardButton("🌟 Koleksi", callback_data="cmd_collection"),
            InlineKeyboardButton("🎣 Equipment", callback_data="cmd_equipment"),
        ],
        [
            InlineKeyboardButton("🔧 Upgrade", callback_data="cmd_upgrade"),
            InlineKeyboardButton("👑 VIP", callback_data="cmd_vip"),
        ],
        [
            InlineKeyboardButton("🛒 Market", callback_data="cmd_market"),
            InlineKeyboardButton("➡️ Transfer", callback_data="cmd_transfer"),
        ],
        [
            InlineKeyboardButton("💰 Top Up", callback_data="cmd_topup"),
            InlineKeyboardButton("🗓 Event", callback_data="cmd_event"),
        ],
        [
            InlineKeyboardButton("⛑ Help", callback_data="cmd_help"),
            InlineKeyboardButton("👥 Group", callback_data="cmd_group"),
        ],
    ])


def back_button(callback: str = "cmd_main"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Kembali", callback_data=callback)]
    ])


def back_and_main():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("◀️ Kembali", callback_data="cmd_main"),
        ]
    ])


def shop_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎣 Joran", callback_data="shop_rods"),
            InlineKeyboardButton("🪱 Umpan", callback_data="shop_baits"),
        ],
        [
            InlineKeyboardButton("🍾 Boost", callback_data="shop_boosts"),
            InlineKeyboardButton("👑 VIP", callback_data="shop_vip"),
        ],
        [InlineKeyboardButton("◀️ Kembali ke Menu", callback_data="cmd_main")],
    ])


def fishing_action_keyboard(can_fish: bool, cooldown_left: int = 0):
    if can_fish:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎣 Lempar Kail!", callback_data="do_fishing")],
            [
                InlineKeyboardButton("🗺 Ganti Peta", callback_data="cmd_map"),
                InlineKeyboardButton("🎣 Equipment", callback_data="cmd_equipment"),
            ],
            [InlineKeyboardButton("◀️ Menu Utama", callback_data="cmd_main")],
        ])
    else:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"⏳ Tunggu {cooldown_left}s...", callback_data="fishing_wait")],
            [
                InlineKeyboardButton("🗺 Ganti Peta", callback_data="cmd_map"),
                InlineKeyboardButton("🎣 Equipment", callback_data="cmd_equipment"),
            ],
            [InlineKeyboardButton("◀️ Menu Utama", callback_data="cmd_main")],
        ])


def after_catch_keyboard(bag_id: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎣 Mancing Lagi!", callback_data="do_fishing"),
            InlineKeyboardButton(f"💰 Jual", callback_data=f"sell_fish_{bag_id}"),
        ],
        [
            InlineKeyboardButton("⭐ Favorit", callback_data=f"fav_fish_{bag_id}"),
            InlineKeyboardButton("🛒 Ke Market", callback_data=f"market_list_{bag_id}"),
        ],
        [InlineKeyboardButton("◀️ Menu Utama", callback_data="cmd_main")],
    ])


def map_select_keyboard(unlocked_maps, player_level, all_maps):
    buttons = []
    for map_id, map_data in all_maps.items():
        is_unlocked = map_id in unlocked_maps
        level_ok = player_level >= map_data["level_req"]
        if is_unlocked:
            label = f"✅ {map_data['name']}"
            cb = f"select_map_{map_id}"
        elif level_ok and map_data["unlock_cost"] > 0:
            label = f"🔓 {map_data['name']} ({map_data['unlock_cost']:,}🪙)"
            cb = f"unlock_map_{map_id}"
        else:
            label = f"🔒 {map_data['name']} (Lv.{map_data['level_req']})"
            cb = f"locked_map_{map_id}"
        buttons.append([InlineKeyboardButton(label, callback_data=cb)])
    buttons.append([InlineKeyboardButton("◀️ Kembali", callback_data="cmd_main")])
    return InlineKeyboardMarkup(buttons)


def equipment_keyboard(rods_owned, current_rod, current_bait, baits_owned):
    buttons = []
    buttons.append([InlineKeyboardButton("🎣 Ganti Joran", callback_data="equip_rod_menu")])
    buttons.append([InlineKeyboardButton("🪱 Ganti Umpan", callback_data="equip_bait_menu")])
    buttons.append([
        InlineKeyboardButton("🛒 Beli Joran", callback_data="shop_rods"),
        InlineKeyboardButton("🛒 Beli Umpan", callback_data="shop_baits"),
    ])
    buttons.append([InlineKeyboardButton("◀️ Kembali", callback_data="cmd_main")])
    return InlineKeyboardMarkup(buttons)


def rod_select_keyboard(rods_owned):
    buttons = []
    from data.shop_data import RODS
    for rod_id in rods_owned:
        rod = RODS.get(rod_id)
        if rod:
            buttons.append([InlineKeyboardButton(
                f"{rod['emoji']} {rod['name']}",
                callback_data=f"equip_rod_{rod_id}"
            )])
    buttons.append([InlineKeyboardButton("◀️ Kembali", callback_data="cmd_equipment")])
    return InlineKeyboardMarkup(buttons)


def bait_select_keyboard(baits_owned):
    buttons = []
    from data.shop_data import BAITS
    for item in baits_owned:
        bait = BAITS.get(item["item_id"])
        if bait and item["quantity"] > 0:
            buttons.append([InlineKeyboardButton(
                f"{bait['emoji']} {bait['name']} x{item['quantity']}",
                callback_data=f"equip_bait_{item['item_id']}"
            )])
    buttons.append([InlineKeyboardButton("◀️ Kembali", callback_data="cmd_equipment")])
    return InlineKeyboardMarkup(buttons)


def bag_keyboard(items, page: int, total_pages: int):
    buttons = []
    for item in items:
        from data.fish_data import RARITY_COLORS, FISH_DATA
        fish = FISH_DATA.get(item["fish_name"], {})
        color = RARITY_COLORS.get(item["rarity"], "")
        fav = "⭐" if item.get("is_favorite") else ""
        buttons.append([InlineKeyboardButton(
            f"{color}{fav} {fish.get('emoji','🐟')} {item['fish_name']} {item['weight']}kg",
            callback_data=f"bag_item_{item['id']}"
        )])

    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"bag_page_{page-1}"))
    nav.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="bag_info"))
    if page < total_pages:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"bag_page_{page+1}"))
    if nav:
        buttons.append(nav)

    buttons.append([
        InlineKeyboardButton("💰 Jual Semua", callback_data="sell_all"),
        InlineKeyboardButton("◀️ Menu", callback_data="cmd_main"),
    ])
    return InlineKeyboardMarkup(buttons)


def bag_item_keyboard(bag_id: int, is_favorite: bool):
    fav_label = "💔 Hapus Favorit" if is_favorite else "⭐ Tandai Favorit"
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💰 Jual", callback_data=f"sell_fish_{bag_id}"),
            InlineKeyboardButton(fav_label, callback_data=f"fav_fish_{bag_id}"),
        ],
        [InlineKeyboardButton("🛒 Jual di Market", callback_data=f"market_list_{bag_id}")],
        [InlineKeyboardButton("◀️ Kembali ke Tas", callback_data="cmd_bag")],
    ])


def market_keyboard(listings, page: int = 1, total_pages: int = 1, rarity_filter: str = "all"):
    buttons = []

    # Filter buttons
    buttons.append([
        InlineKeyboardButton("🔵 Rare", callback_data="market_filter_Rare"),
        InlineKeyboardButton("🟣 Epic", callback_data="market_filter_Epic"),
        InlineKeyboardButton("🟠 Legend", callback_data="market_filter_Legendary"),
    ])
    buttons.append([
        InlineKeyboardButton("🔴 Mythic", callback_data="market_filter_Mythic"),
        InlineKeyboardButton("✨ Divine", callback_data="market_filter_Divine"),
        InlineKeyboardButton("🗂 Semua", callback_data="market_filter_all"),
    ])

    for listing in listings:
        from data.fish_data import RARITY_COLORS, FISH_DATA
        fish = FISH_DATA.get(listing["fish_name"], {})
        color = RARITY_COLORS.get(listing["rarity"], "")
        buttons.append([InlineKeyboardButton(
            f"{color} {fish.get('emoji','🐟')} {listing['fish_name']} {listing['weight']}kg — {listing['price']:,}🪙",
            callback_data=f"buy_market_{listing['id']}"
        )])

    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"market_page_{page-1}"))
    nav.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="market_info"))
    if page < total_pages:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"market_page_{page+1}"))
    if nav:
        buttons.append(nav)

    buttons.append([
        InlineKeyboardButton("📦 Jual Ikan", callback_data="market_sell_menu"),
        InlineKeyboardButton("◀️ Menu", callback_data="cmd_main"),
    ])
    return InlineKeyboardMarkup(buttons)


def boost_keyboard(boosts_owned):
    buttons = []
    from data.shop_data import BOOSTS
    for item in boosts_owned:
        boost = BOOSTS.get(item["item_id"])
        if boost and item["quantity"] > 0:
            buttons.append([InlineKeyboardButton(
                f"{boost['emoji']} {boost['name']} x{item['quantity']} — Aktifkan",
                callback_data=f"use_boost_{item['item_id']}"
            )])
    buttons.append([
        InlineKeyboardButton("🛒 Beli Boost", callback_data="shop_boosts"),
        InlineKeyboardButton("◀️ Menu", callback_data="cmd_main"),
    ])
    return InlineKeyboardMarkup(buttons)


def leaderboard_keyboard(current: str = "coins"):
    tabs = [
        ("💰 Koin", "lb_coins"),
        ("⭐ Level", "lb_level"),
        ("🐟 Tangkapan", "lb_caught"),
        ("💎 Penghasilan", "lb_earned"),
    ]
    row = [InlineKeyboardButton(
        f"{'✅' if current == t[1].split('_')[1] else ''}{t[0]}",
        callback_data=t[1]
    ) for t in tabs]
    return InlineKeyboardMarkup([
        row[:2], row[2:],
        [InlineKeyboardButton("◀️ Menu Utama", callback_data="cmd_main")]
    ])


def upgrade_keyboard(current_level: int, cost: int, max_level: int = 20):
    buttons = []
    if current_level < max_level:
        buttons.append([InlineKeyboardButton(
            f"⬆️ Upgrade Joran ({cost:,} 🪙)",
            callback_data="do_upgrade"
        )])
    else:
        buttons.append([InlineKeyboardButton("✅ Upgrade Maksimal!", callback_data="upgrade_max")])
    buttons.append([InlineKeyboardButton("◀️ Kembali", callback_data="cmd_main")])
    return InlineKeyboardMarkup(buttons)


def topup_keyboard():
    from data.shop_data import TOPUP_PACKAGES
    buttons = []
    for pkg_id, pkg in TOPUP_PACKAGES.items():
        buttons.append([InlineKeyboardButton(
            f"💰 {pkg['label']} — Rp {pkg['price_idr']:,}",
            callback_data=f"topup_{pkg_id}"
        )])
    buttons.append([InlineKeyboardButton("◀️ Kembali", callback_data="cmd_main")])
    return InlineKeyboardMarkup(buttons)


def vip_keyboard():
    from data.shop_data import VIP_TIERS
    buttons = []
    for vip_id, vip in VIP_TIERS.items():
        buttons.append([InlineKeyboardButton(
            f"{vip['emoji']} {vip['name']} — {vip['price']:,} 🪙",
            callback_data=f"buy_vip_{vip_id}"
        )])
    buttons.append([InlineKeyboardButton("◀️ Kembali", callback_data="cmd_main")])
    return InlineKeyboardMarkup(buttons)


def confirm_keyboard(confirm_cb: str, cancel_cb: str = "cmd_main"):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Ya, Konfirmasi", callback_data=confirm_cb),
            InlineKeyboardButton("❌ Batal", callback_data=cancel_cb),
        ]
    ])
