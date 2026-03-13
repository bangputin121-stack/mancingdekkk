# ============================================================
# SHOP DATA - Rods, Baits, Boosts, VIP
# ============================================================

RODS = {
    "rod_bamboo": {
        "name": "Joran Bambu", "emoji": "🎋",
        "price": 0, "description": "Joran dasar gratis untuk pemula",
        "luck_bonus": 0, "rare_bonus": 0, "catch_speed": 1.0,
        "durability": 100, "level_req": 1,
        "tier": "Starter"
    },
    "rod_basic": {
        "name": "Joran Basic", "emoji": "🎣",
        "price": 500, "description": "Joran standar dengan sedikit peningkatan",
        "luck_bonus": 5, "rare_bonus": 2, "catch_speed": 1.1,
        "durability": 150, "level_req": 1,
        "tier": "Basic"
    },
    "rod_fiber": {
        "name": "Joran Fiber", "emoji": "🎣",
        "price": 2000, "description": "Joran fiber ringan dan kuat",
        "luck_bonus": 10, "rare_bonus": 5, "catch_speed": 1.2,
        "durability": 250, "level_req": 5,
        "tier": "Standard"
    },
    "rod_carbon": {
        "name": "Joran Carbon", "emoji": "⚫",
        "price": 5000, "description": "Joran karbon premium, sangat sensitif",
        "luck_bonus": 20, "rare_bonus": 10, "catch_speed": 1.4,
        "durability": 400, "level_req": 10,
        "tier": "Premium"
    },
    "rod_titanium": {
        "name": "Joran Titanium", "emoji": "⚙️",
        "price": 15000, "description": "Joran titanium ultra kuat",
        "luck_bonus": 35, "rare_bonus": 20, "catch_speed": 1.6,
        "durability": 700, "level_req": 20,
        "tier": "Elite"
    },
    "rod_dragon": {
        "name": "Joran Naga", "emoji": "🐉",
        "price": 50000, "description": "Joran legendaris berbentuk naga. Drop rate Legendary+",
        "luck_bonus": 60, "rare_bonus": 35, "catch_speed": 2.0,
        "durability": 1500, "level_req": 40,
        "tier": "Legendary"
    },
    "rod_divine": {
        "name": "Joran Ilahi", "emoji": "✨",
        "price": 200000, "description": "Joran tertinggi. Chance Divine sangat meningkat!",
        "luck_bonus": 100, "rare_bonus": 60, "catch_speed": 2.5,
        "durability": 5000, "level_req": 70,
        "tier": "Divine"
    },
}

BAITS = {
    "bait_worm": {
        "name": "Cacing Tanah", "emoji": "🪱",
        "price": 10, "description": "Umpan dasar paling umum",
        "luck_bonus": 0, "rare_bonus": 0, "quantity": 1,
        "tier": "Basic"
    },
    "bait_shrimp": {
        "name": "Udang Kecil", "emoji": "🦐",
        "price": 25, "description": "Umpan udang untuk ikan menengah",
        "luck_bonus": 5, "rare_bonus": 3, "quantity": 1,
        "tier": "Standard"
    },
    "bait_fish": {
        "name": "Ikan Kecil", "emoji": "🐟",
        "price": 50, "description": "Umpan ikan untuk menarik ikan besar",
        "luck_bonus": 10, "rare_bonus": 7, "quantity": 1,
        "tier": "Premium"
    },
    "bait_cricket": {
        "name": "Jangkrik Emas", "emoji": "🦗",
        "price": 80, "description": "Jangkrik emas menarik ikan Rare+",
        "luck_bonus": 15, "rare_bonus": 12, "quantity": 1,
        "tier": "Elite"
    },
    "bait_squid": {
        "name": "Cumi Segar", "emoji": "🦑",
        "price": 150, "description": "Cumi segar untuk ikan laut dalam",
        "luck_bonus": 20, "rare_bonus": 18, "quantity": 1,
        "tier": "Elite"
    },
    "bait_golden": {
        "name": "Umpan Emas", "emoji": "✨",
        "price": 500, "description": "Umpan ajaib meningkatkan semua rarity!",
        "luck_bonus": 40, "rare_bonus": 30, "quantity": 1,
        "tier": "Legendary"
    },
    "bait_divine": {
        "name": "Umpan Kristal", "emoji": "💎",
        "price": 2000, "description": "Umpan Divine, chance Mythic & Divine meningkat drastis!",
        "luck_bonus": 80, "rare_bonus": 60, "quantity": 1,
        "tier": "Divine"
    },
    # Bundle packs
    "bait_worm_10": {
        "name": "Cacing x10", "emoji": "🪱",
        "price": 90, "description": "Paket 10 cacing tanah",
        "luck_bonus": 0, "rare_bonus": 0, "quantity": 10,
        "tier": "Basic"
    },
    "bait_shrimp_10": {
        "name": "Udang x10", "emoji": "🦐",
        "price": 220, "description": "Paket 10 udang kecil",
        "luck_bonus": 5, "rare_bonus": 3, "quantity": 10,
        "tier": "Standard"
    },
    "bait_golden_5": {
        "name": "Umpan Emas x5", "emoji": "✨",
        "price": 2200, "description": "Paket 5 umpan emas",
        "luck_bonus": 40, "rare_bonus": 30, "quantity": 5,
        "tier": "Legendary"
    },
}

BOOSTS = {
    "boost_luck_small": {
        "name": "Jimat Keberuntungan Kecil", "emoji": "🍀",
        "price": 300, "description": "+20% luck selama 30 menit",
        "duration": 30, "luck_bonus": 20, "rare_bonus": 0,
        "xp_bonus": 0, "coin_bonus": 0,
        "tier": "Basic"
    },
    "boost_luck_medium": {
        "name": "Jimat Keberuntungan", "emoji": "🍀",
        "price": 800, "description": "+40% luck selama 1 jam",
        "duration": 60, "luck_bonus": 40, "rare_bonus": 10,
        "xp_bonus": 0, "coin_bonus": 0,
        "tier": "Standard"
    },
    "boost_rare": {
        "name": "Ramuan Rare", "emoji": "🧪",
        "price": 1500, "description": "+30% chance Rare+ selama 1 jam",
        "duration": 60, "luck_bonus": 0, "rare_bonus": 30,
        "xp_bonus": 0, "coin_bonus": 0,
        "tier": "Premium"
    },
    "boost_xp": {
        "name": "Potion XP", "emoji": "⚗️",
        "price": 500, "description": "+100% XP selama 1 jam",
        "duration": 60, "luck_bonus": 0, "rare_bonus": 0,
        "xp_bonus": 100, "coin_bonus": 0,
        "tier": "Standard"
    },
    "boost_coin": {
        "name": "Amulet Koin", "emoji": "💰",
        "price": 600, "description": "+50% koin dari jual ikan selama 1 jam",
        "duration": 60, "luck_bonus": 0, "rare_bonus": 0,
        "xp_bonus": 0, "coin_bonus": 50,
        "tier": "Standard"
    },
    "boost_mega": {
        "name": "Boost Mega", "emoji": "🚀",
        "price": 5000, "description": "+50% semua bonus selama 2 jam",
        "duration": 120, "luck_bonus": 50, "rare_bonus": 25,
        "xp_bonus": 50, "coin_bonus": 25,
        "tier": "Elite"
    },
    "boost_vip": {
        "name": "Boost VIP", "emoji": "👑",
        "price": 10000, "description": "+100% semua bonus selama 4 jam (VIP only)",
        "duration": 240, "luck_bonus": 100, "rare_bonus": 50,
        "xp_bonus": 100, "coin_bonus": 50,
        "tier": "VIP"
    },
}

VIP_TIERS = {
    "vip_bronze": {
        "name": "VIP Bronze", "emoji": "🥉",
        "price": 10000, "duration_days": 30,
        "daily_bonus": 500, "luck_bonus": 10, "rare_bonus": 5,
        "xp_bonus": 20, "coin_bonus": 15, "bag_slots": 50,
        "description": "VIP Bronze 30 hari"
    },
    "vip_silver": {
        "name": "VIP Silver", "emoji": "🥈",
        "price": 25000, "duration_days": 30,
        "daily_bonus": 1500, "luck_bonus": 25, "rare_bonus": 15,
        "xp_bonus": 40, "coin_bonus": 30, "bag_slots": 100,
        "description": "VIP Silver 30 hari"
    },
    "vip_gold": {
        "name": "VIP Gold", "emoji": "🥇",
        "price": 60000, "duration_days": 30,
        "daily_bonus": 4000, "luck_bonus": 50, "rare_bonus": 30,
        "xp_bonus": 75, "coin_bonus": 50, "bag_slots": 200,
        "description": "VIP Gold 30 hari"
    },
    "vip_platinum": {
        "name": "VIP Platinum", "emoji": "💎",
        "price": 150000, "duration_days": 30,
        "daily_bonus": 10000, "luck_bonus": 100, "rare_bonus": 60,
        "xp_bonus": 150, "coin_bonus": 100, "bag_slots": 500,
        "description": "VIP Platinum 30 hari"
    },
}

TOPUP_PACKAGES = {
    "topup_100": {"coins": 1000, "price_idr": 10000, "bonus": 0, "label": "1.000 Koin"},
    "topup_250": {"coins": 2750, "price_idr": 25000, "bonus": 10, "label": "2.750 Koin (+10%)"},
    "topup_500": {"coins": 5750, "price_idr": 50000, "bonus": 15, "label": "5.750 Koin (+15%)"},
    "topup_1000": {"coins": 12000, "price_idr": 100000, "bonus": 20, "label": "12.000 Koin (+20%)"},
    "topup_2500": {"coins": 32500, "price_idr": 250000, "bonus": 30, "label": "32.500 Koin (+30%)"},
    "topup_5000": {"coins": 70000, "price_idr": 500000, "bonus": 40, "label": "70.000 Koin (+40%)"},
}

# Map locations with fish availability
MAPS = {
    "map_kolam": {
        "name": "🏞️ Kolam Desa", "emoji": "🏞️",
        "description": "Kolam tenang di desa, cocok untuk pemula",
        "level_req": 1, "unlock_cost": 0,
        "fish_types": ["Common", "Uncommon"],
        "rare_multiplier": 1.0, "coin_multiplier": 1.0,
        "catch_time": 15,  # seconds cooldown
    },
    "map_sungai": {
        "name": "🌊 Sungai Jernih", "emoji": "🌊",
        "description": "Sungai jernih dengan ikan yang beragam",
        "level_req": 5, "unlock_cost": 1000,
        "fish_types": ["Common", "Uncommon", "Rare"],
        "rare_multiplier": 1.3, "coin_multiplier": 1.2,
        "catch_time": 20,
    },
    "map_danau": {
        "name": "🏔️ Danau Gunung", "emoji": "🏔️",
        "description": "Danau di pegunungan dengan ikan langka",
        "level_req": 15, "unlock_cost": 5000,
        "fish_types": ["Uncommon", "Rare", "Epic"],
        "rare_multiplier": 1.6, "coin_multiplier": 1.5,
        "catch_time": 25,
    },
    "map_laut": {
        "name": "🌊 Laut Biru", "emoji": "🌊",
        "description": "Laut luas dengan ikan besar dan berharga",
        "level_req": 25, "unlock_cost": 15000,
        "fish_types": ["Rare", "Epic", "Legendary"],
        "rare_multiplier": 2.0, "coin_multiplier": 2.0,
        "catch_time": 30,
    },
    "map_deep": {
        "name": "🕳️ Laut Dalam", "emoji": "🕳️",
        "description": "Kedalaman laut tempat monster laut bersarang",
        "level_req": 40, "unlock_cost": 40000,
        "fish_types": ["Epic", "Legendary", "Mythic"],
        "rare_multiplier": 3.0, "coin_multiplier": 3.0,
        "catch_time": 40,
    },
    "map_divine": {
        "name": "✨ Danau Surgawi", "emoji": "✨",
        "description": "Tempat misterius tempat ikan ilahi berenang",
        "level_req": 60, "unlock_cost": 100000,
        "fish_types": ["Mythic", "Divine"],
        "rare_multiplier": 5.0, "coin_multiplier": 5.0,
        "catch_time": 60,
    },
}

# XP needed per level
def xp_for_level(level: int) -> int:
    return int(100 * (level ** 1.5))

# Level titles
LEVEL_TITLES = {
    1: "🪨 Pemancing Pemula",
    5: "🎣 Pemancing Desa",
    10: "🌊 Pemancing Sungai",
    15: "⚓ Pelaut Muda",
    20: "🐟 Pemburu Ikan",
    30: "🦈 Pemburu Laut",
    40: "🐲 Penguasa Danau",
    50: "👑 Raja Pemancing",
    60: "🌟 Legenda Laut",
    70: "✨ Dewa Pancing",
    80: "💎 Pemancing Surgawi",
    100: "🌌 Raja Samudra Abadi",
}

def get_level_title(level: int) -> str:
    title = "🪨 Pemancing Pemula"
    for lvl, t in LEVEL_TITLES.items():
        if level >= lvl:
            title = t
    return title
