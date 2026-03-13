# ============================================================
# FISH DATA - All fish with rarity, weight, price, emoji
# ============================================================

FISH_DATA = {
    # ─── COMMON (40% base chance) ───────────────────────────
    "Ikan Lele": {
        "rarity": "Common", "emoji": "🐟", "min_weight": 0.3, "max_weight": 2.5,
        "base_price": 50, "sell_price": 30, "xp": 5, "color": "⬜"
    },
    "Ikan Nila": {
        "rarity": "Common", "emoji": "🐠", "min_weight": 0.2, "max_weight": 1.8,
        "base_price": 60, "sell_price": 35, "xp": 5, "color": "⬜"
    },
    "Ikan Gurame": {
        "rarity": "Common", "emoji": "🐡", "min_weight": 0.5, "max_weight": 3.0,
        "base_price": 80, "sell_price": 50, "xp": 8, "color": "⬜"
    },
    "Ikan Mas": {
        "rarity": "Common", "emoji": "🟡", "min_weight": 0.3, "max_weight": 2.0,
        "base_price": 70, "sell_price": 40, "xp": 6, "color": "⬜"
    },
    "Ikan Mujair": {
        "rarity": "Common", "emoji": "🐟", "min_weight": 0.2, "max_weight": 1.5,
        "base_price": 55, "sell_price": 30, "xp": 5, "color": "⬜"
    },

    # ─── UNCOMMON (25% base chance) ─────────────────────────
    "Ikan Bawal": {
        "rarity": "Uncommon", "emoji": "🐟", "min_weight": 0.8, "max_weight": 4.0,
        "base_price": 150, "sell_price": 90, "xp": 15, "color": "🟩"
    },
    "Ikan Gabus": {
        "rarity": "Uncommon", "emoji": "🐍", "min_weight": 0.5, "max_weight": 3.5,
        "base_price": 160, "sell_price": 95, "xp": 15, "color": "🟩"
    },
    "Ikan Patin": {
        "rarity": "Uncommon", "emoji": "🐟", "min_weight": 1.0, "max_weight": 5.0,
        "base_price": 180, "sell_price": 110, "xp": 18, "color": "🟩"
    },
    "Ikan Tambakan": {
        "rarity": "Uncommon", "emoji": "🐠", "min_weight": 0.5, "max_weight": 2.5,
        "base_price": 140, "sell_price": 85, "xp": 14, "color": "🟩"
    },
    "Ikan Sepat": {
        "rarity": "Uncommon", "emoji": "🐟", "min_weight": 0.1, "max_weight": 0.8,
        "base_price": 120, "sell_price": 75, "xp": 12, "color": "🟩"
    },

    # ─── RARE (18% base chance) ──────────────────────────────
    "Ikan Toman": {
        "rarity": "Rare", "emoji": "🦎", "min_weight": 2.0, "max_weight": 10.0,
        "base_price": 400, "sell_price": 250, "xp": 40, "color": "🟦"
    },
    "Ikan Arwana": {
        "rarity": "Rare", "emoji": "🥇", "min_weight": 1.5, "max_weight": 6.0,
        "base_price": 500, "sell_price": 320, "xp": 50, "color": "🟦"
    },
    "Ikan Belida": {
        "rarity": "Rare", "emoji": "🐟", "min_weight": 1.0, "max_weight": 5.0,
        "base_price": 380, "sell_price": 240, "xp": 38, "color": "🟦"
    },
    "Ikan Sidat": {
        "rarity": "Rare", "emoji": "🐍", "min_weight": 0.5, "max_weight": 4.0,
        "base_price": 450, "sell_price": 280, "xp": 45, "color": "🟦"
    },
    "Ikan Kakap Merah": {
        "rarity": "Rare", "emoji": "🔴", "min_weight": 1.5, "max_weight": 8.0,
        "base_price": 480, "sell_price": 300, "xp": 48, "color": "🟦"
    },

    # ─── EPIC (10% base chance) ──────────────────────────────
    "Ikan Kalajengking": {
        "rarity": "Epic", "emoji": "🦂", "min_weight": 0.5, "max_weight": 3.0,
        "base_price": 1000, "sell_price": 700, "xp": 100, "color": "🟪"
    },
    "Ikan Layaran": {
        "rarity": "Epic", "emoji": "⛵", "min_weight": 5.0, "max_weight": 20.0,
        "base_price": 1200, "sell_price": 850, "xp": 120, "color": "🟪"
    },
    "Hiu Paus Mini": {
        "rarity": "Epic", "emoji": "🦈", "min_weight": 10.0, "max_weight": 30.0,
        "base_price": 1500, "sell_price": 1000, "xp": 150, "color": "🟪"
    },
    "Ikan Swordfish": {
        "rarity": "Epic", "emoji": "⚔️", "min_weight": 8.0, "max_weight": 25.0,
        "base_price": 1300, "sell_price": 900, "xp": 130, "color": "🟪"
    },

    # ─── LEGENDARY (5% base chance) ─────────────────────────
    "Arwana Super Red": {
        "rarity": "Legendary", "emoji": "🔥", "min_weight": 3.0, "max_weight": 8.0,
        "base_price": 5000, "sell_price": 3500, "xp": 500, "color": "🟧"
    },
    "Ikan Sturgeon Emas": {
        "rarity": "Legendary", "emoji": "👑", "min_weight": 15.0, "max_weight": 50.0,
        "base_price": 7000, "sell_price": 5000, "xp": 700, "color": "🟧"
    },
    "Ikan Naga Merah": {
        "rarity": "Legendary", "emoji": "🐲", "min_weight": 5.0, "max_weight": 15.0,
        "base_price": 8000, "sell_price": 5500, "xp": 800, "color": "🟧"
    },
    "Ikan Phoenix": {
        "rarity": "Legendary", "emoji": "🦅", "min_weight": 4.0, "max_weight": 12.0,
        "base_price": 6000, "sell_price": 4200, "xp": 600, "color": "🟧"
    },

    # ─── MYTHIC (2% base chance) ─────────────────────────────
    "Leviathan Kecil": {
        "rarity": "Mythic", "emoji": "🌊", "min_weight": 50.0, "max_weight": 200.0,
        "base_price": 25000, "sell_price": 18000, "xp": 2500, "color": "🔴"
    },
    "Naga Laut Purba": {
        "rarity": "Mythic", "emoji": "🐉", "min_weight": 30.0, "max_weight": 100.0,
        "base_price": 30000, "sell_price": 22000, "xp": 3000, "color": "🔴"
    },
    "Ikan Bintang Abadi": {
        "rarity": "Mythic", "emoji": "⭐", "min_weight": 10.0, "max_weight": 40.0,
        "base_price": 20000, "sell_price": 15000, "xp": 2000, "color": "🔴"
    },

    # ─── DIVINE (0.5% base chance) ───────────────────────────
    "Dewa Laut": {
        "rarity": "Divine", "emoji": "🌟", "min_weight": 100.0, "max_weight": 500.0,
        "base_price": 100000, "sell_price": 75000, "xp": 10000, "color": "✨"
    },
    "Ikan Kristal Surgawi": {
        "rarity": "Divine", "emoji": "💎", "min_weight": 20.0, "max_weight": 80.0,
        "base_price": 80000, "sell_price": 60000, "xp": 8000, "color": "✨"
    },
    "Raja Samudra Abadi": {
        "rarity": "Divine", "emoji": "👸", "min_weight": 200.0, "max_weight": 1000.0,
        "base_price": 150000, "sell_price": 110000, "xp": 15000, "color": "✨"
    },
}

# Rarity chances (base, modified by rod/location)
RARITY_CHANCES = {
    "Common":    40.0,
    "Uncommon":  25.0,
    "Rare":      18.0,
    "Epic":      10.0,
    "Legendary":  5.0,
    "Mythic":     1.5,
    "Divine":     0.5,
}

RARITY_COLORS = {
    "Common":    "⬜",
    "Uncommon":  "🟩",
    "Rare":      "🟦",
    "Epic":      "🟪",
    "Legendary": "🟧",
    "Mythic":    "🔴",
    "Divine":    "✨",
}

RARITY_EMOJIS = {
    "Common":    "◽",
    "Uncommon":  "🟢",
    "Rare":      "🔵",
    "Epic":      "🟣",
    "Legendary": "🟠",
    "Mythic":    "🔴",
    "Divine":    "💫",
}
