import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

DB_PATH = os.environ.get("DB_PATH", "fishing_game.db")

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    """Initialize all database tables."""
    conn = get_db()
    c = conn.cursor()

    # ── PLAYERS ──────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS players (
            user_id       INTEGER PRIMARY KEY,
            username      TEXT,
            full_name     TEXT,
            coins         INTEGER DEFAULT 500,
            gems          INTEGER DEFAULT 0,
            xp            INTEGER DEFAULT 0,
            level         INTEGER DEFAULT 1,
            current_rod   TEXT DEFAULT 'rod_bamboo',
            current_bait  TEXT DEFAULT 'bait_worm',
            current_map   TEXT DEFAULT 'map_kolam',
            total_caught  INTEGER DEFAULT 0,
            total_sold    INTEGER DEFAULT 0,
            total_earned  INTEGER DEFAULT 0,
            joined_at     TEXT DEFAULT (datetime('now')),
            last_fishing  TEXT,
            last_daily    TEXT,
            vip_type      TEXT DEFAULT NULL,
            vip_expires   TEXT DEFAULT NULL,
            is_banned     INTEGER DEFAULT 0,
            settings      TEXT DEFAULT '{}'
        )
    """)

    # ── INVENTORY (rods, baits, boosts) ─────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER,
            item_type  TEXT,  -- 'rod', 'bait', 'boost'
            item_id    TEXT,
            quantity   INTEGER DEFAULT 1,
            UNIQUE(user_id, item_id),
            FOREIGN KEY(user_id) REFERENCES players(user_id)
        )
    """)

    # ── BAG (caught fish) ────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS bag (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER,
            fish_name  TEXT,
            weight     REAL,
            rarity     TEXT,
            caught_at  TEXT DEFAULT (datetime('now')),
            location   TEXT,
            is_favorite INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES players(user_id)
        )
    """)

    # ── FISHING HISTORY ──────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER,
            fish_name  TEXT,
            weight     REAL,
            rarity     TEXT,
            action     TEXT,  -- 'catch', 'sell', 'transfer'
            coins_earned INTEGER DEFAULT 0,
            location   TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(user_id) REFERENCES players(user_id)
        )
    """)

    # ── ACTIVE BOOSTS ────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS active_boosts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER,
            boost_id   TEXT,
            boost_name TEXT,
            luck_bonus INTEGER DEFAULT 0,
            rare_bonus INTEGER DEFAULT 0,
            xp_bonus   INTEGER DEFAULT 0,
            coin_bonus INTEGER DEFAULT 0,
            expires_at TEXT,
            FOREIGN KEY(user_id) REFERENCES players(user_id)
        )
    """)

    # ── MARKET LISTINGS ──────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS market (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id  INTEGER,
            fish_bag_id INTEGER,
            fish_name  TEXT,
            weight     REAL,
            rarity     TEXT,
            price      INTEGER,
            listed_at  TEXT DEFAULT (datetime('now')),
            sold       INTEGER DEFAULT 0,
            FOREIGN KEY(seller_id) REFERENCES players(user_id)
        )
    """)

    # ── ROD UPGRADES ─────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS rod_upgrades (
            user_id    INTEGER PRIMARY KEY,
            level      INTEGER DEFAULT 0,
            luck_bonus INTEGER DEFAULT 0,
            rare_bonus INTEGER DEFAULT 0,
            total_spent INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES players(user_id)
        )
    """)

    # ── UNLOCKED MAPS ────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS unlocked_maps (
            user_id  INTEGER,
            map_id   TEXT,
            PRIMARY KEY(user_id, map_id),
            FOREIGN KEY(user_id) REFERENCES players(user_id)
        )
    """)

    # ── LEADERBOARD CACHE ────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard_cache (
            rank       INTEGER,
            user_id    INTEGER,
            username   TEXT,
            value      INTEGER,
            category   TEXT,
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── EVENTS ───────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT,
            description TEXT,
            reward      TEXT,
            start_date  TEXT,
            end_date    TEXT,
            is_active   INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

# ─────────────────────────────────────────────────────────────
# PLAYER FUNCTIONS
# ─────────────────────────────────────────────────────────────

def get_player(user_id: int) -> Optional[Dict]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM players WHERE user_id=?", (user_id,)).fetchone()
        return dict(row) if row else None

def create_player(user_id: int, username: str, full_name: str) -> Dict:
    with get_db() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO players (user_id, username, full_name)
            VALUES (?, ?, ?)
        """, (user_id, username or "Unknown", full_name or "Unknown"))
        # Give starter bait
        conn.execute("""
            INSERT OR IGNORE INTO inventory (user_id, item_type, item_id, quantity)
            VALUES (?, 'bait', 'bait_worm', 10)
        """, (user_id,))
        # Unlock starting map
        conn.execute("""
            INSERT OR IGNORE INTO unlocked_maps (user_id, map_id) VALUES (?, 'map_kolam')
        """, (user_id,))
        # Init rod upgrades
        conn.execute("""
            INSERT OR IGNORE INTO rod_upgrades (user_id) VALUES (?)
        """, (user_id,))
        conn.commit()
    return get_player(user_id)

def update_player(user_id: int, **kwargs):
    if not kwargs:
        return
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [user_id]
    with get_db() as conn:
        conn.execute(f"UPDATE players SET {sets} WHERE user_id=?", vals)
        conn.commit()

def add_coins(user_id: int, amount: int) -> int:
    with get_db() as conn:
        conn.execute("UPDATE players SET coins=coins+? WHERE user_id=?", (amount, user_id))
        conn.commit()
        row = conn.execute("SELECT coins FROM players WHERE user_id=?", (user_id,)).fetchone()
        return row["coins"] if row else 0

def spend_coins(user_id: int, amount: int) -> bool:
    with get_db() as conn:
        row = conn.execute("SELECT coins FROM players WHERE user_id=?", (user_id,)).fetchone()
        if not row or row["coins"] < amount:
            return False
        conn.execute("UPDATE players SET coins=coins-? WHERE user_id=?", (amount, user_id))
        conn.commit()
        return True

def add_xp(user_id: int, xp_amount: int) -> Dict:
    """Add XP and handle level up. Returns {'leveled_up': bool, 'old_level': int, 'new_level': int}"""
    from data.shop_data import xp_for_level
    player = get_player(user_id)
    if not player:
        return {"leveled_up": False, "old_level": 1, "new_level": 1}

    old_level = player["level"]
    new_xp = player["xp"] + xp_amount
    new_level = old_level

    # Calculate new level
    while True:
        needed = xp_for_level(new_level + 1)
        if new_xp >= needed:
            new_xp -= needed
            new_level += 1
        else:
            break

    update_player(user_id, xp=new_xp, level=new_level)
    return {"leveled_up": new_level > old_level, "old_level": old_level, "new_level": new_level}

# ─────────────────────────────────────────────────────────────
# INVENTORY FUNCTIONS
# ─────────────────────────────────────────────────────────────

def get_inventory(user_id: int, item_type: Optional[str] = None) -> List[Dict]:
    with get_db() as conn:
        if item_type:
            rows = conn.execute(
                "SELECT * FROM inventory WHERE user_id=? AND item_type=? AND quantity>0",
                (user_id, item_type)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM inventory WHERE user_id=? AND quantity>0", (user_id,)
            ).fetchall()
        return [dict(r) for r in rows]

def add_to_inventory(user_id: int, item_type: str, item_id: str, quantity: int = 1):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO inventory (user_id, item_type, item_id, quantity)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, item_id) DO UPDATE SET quantity=quantity+?
        """, (user_id, item_type, item_id, quantity, quantity))
        conn.commit()

def use_inventory_item(user_id: int, item_id: str, quantity: int = 1) -> bool:
    with get_db() as conn:
        row = conn.execute(
            "SELECT quantity FROM inventory WHERE user_id=? AND item_id=?",
            (user_id, item_id)
        ).fetchone()
        if not row or row["quantity"] < quantity:
            return False
        conn.execute(
            "UPDATE inventory SET quantity=quantity-? WHERE user_id=? AND item_id=?",
            (quantity, user_id, item_id)
        )
        conn.commit()
        return True

def has_item(user_id: int, item_id: str, quantity: int = 1) -> bool:
    with get_db() as conn:
        row = conn.execute(
            "SELECT quantity FROM inventory WHERE user_id=? AND item_id=?",
            (user_id, item_id)
        ).fetchone()
        return bool(row and row["quantity"] >= quantity)

# ─────────────────────────────────────────────────────────────
# BAG FUNCTIONS
# ─────────────────────────────────────────────────────────────

def get_bag(user_id: int, limit: int = 50, offset: int = 0) -> List[Dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM bag WHERE user_id=? ORDER BY caught_at DESC LIMIT ? OFFSET ?",
            (user_id, limit, offset)
        ).fetchall()
        return [dict(r) for r in rows]

def get_bag_count(user_id: int) -> int:
    with get_db() as conn:
        row = conn.execute("SELECT COUNT(*) as cnt FROM bag WHERE user_id=?", (user_id,)).fetchone()
        return row["cnt"] if row else 0

def add_to_bag(user_id: int, fish_name: str, weight: float, rarity: str, location: str) -> int:
    with get_db() as conn:
        c = conn.execute("""
            INSERT INTO bag (user_id, fish_name, weight, rarity, location)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, fish_name, weight, rarity, location))
        conn.commit()
        return c.lastrowid

def remove_from_bag(user_id: int, bag_id: int) -> bool:
    with get_db() as conn:
        row = conn.execute(
            "SELECT id FROM bag WHERE id=? AND user_id=?", (bag_id, user_id)
        ).fetchone()
        if not row:
            return False
        conn.execute("DELETE FROM bag WHERE id=?", (bag_id,))
        conn.commit()
        return True

def get_bag_item(bag_id: int) -> Optional[Dict]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM bag WHERE id=?", (bag_id,)).fetchone()
        return dict(row) if row else None

def toggle_favorite(user_id: int, bag_id: int) -> bool:
    with get_db() as conn:
        row = conn.execute(
            "SELECT is_favorite FROM bag WHERE id=? AND user_id=?", (bag_id, user_id)
        ).fetchone()
        if not row:
            return False
        new_val = 0 if row["is_favorite"] else 1
        conn.execute("UPDATE bag SET is_favorite=? WHERE id=?", (new_val, bag_id))
        conn.commit()
        return True

def get_favorites(user_id: int) -> List[Dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM bag WHERE user_id=? AND is_favorite=1 ORDER BY caught_at DESC",
            (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]

# ─────────────────────────────────────────────────────────────
# HISTORY
# ─────────────────────────────────────────────────────────────

def add_history(user_id: int, fish_name: str, weight: float, rarity: str,
                action: str, coins_earned: int = 0, location: str = ""):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO history (user_id, fish_name, weight, rarity, action, coins_earned, location)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, fish_name, weight, rarity, action, coins_earned, location))
        conn.commit()

def get_history(user_id: int, limit: int = 20) -> List[Dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM history WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        ).fetchall()
        return [dict(r) for r in rows]

# ─────────────────────────────────────────────────────────────
# BOOSTS
# ─────────────────────────────────────────────────────────────

def get_active_boosts(user_id: int) -> List[Dict]:
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        # Clean expired
        conn.execute("DELETE FROM active_boosts WHERE user_id=? AND expires_at<?", (user_id, now))
        conn.commit()
        rows = conn.execute(
            "SELECT * FROM active_boosts WHERE user_id=?", (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]

def activate_boost(user_id: int, boost_id: str, boost_name: str,
                   luck: int, rare: int, xp: int, coin: int, duration_mins: int):
    expires = (datetime.utcnow() + timedelta(minutes=duration_mins)).isoformat()
    with get_db() as conn:
        conn.execute("""
            INSERT INTO active_boosts
            (user_id, boost_id, boost_name, luck_bonus, rare_bonus, xp_bonus, coin_bonus, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, boost_id, boost_name, luck, rare, xp, coin, expires))
        conn.commit()

def get_total_boost(user_id: int) -> Dict:
    boosts = get_active_boosts(user_id)
    total = {"luck": 0, "rare": 0, "xp": 0, "coin": 0}
    for b in boosts:
        total["luck"] += b["luck_bonus"]
        total["rare"] += b["rare_bonus"]
        total["xp"] += b["xp_bonus"]
        total["coin"] += b["coin_bonus"]
    return total

# ─────────────────────────────────────────────────────────────
# MARKET
# ─────────────────────────────────────────────────────────────

def list_market_item(seller_id: int, bag_id: int, fish_name: str,
                     weight: float, rarity: str, price: int) -> int:
    with get_db() as conn:
        c = conn.execute("""
            INSERT INTO market (seller_id, fish_bag_id, fish_name, weight, rarity, price)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (seller_id, bag_id, fish_name, weight, rarity, price))
        conn.commit()
        return c.lastrowid

def get_market_listings(rarity_filter: Optional[str] = None, limit: int = 20) -> List[Dict]:
    with get_db() as conn:
        if rarity_filter:
            rows = conn.execute(
                "SELECT * FROM market WHERE sold=0 AND rarity=? ORDER BY listed_at DESC LIMIT ?",
                (rarity_filter, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM market WHERE sold=0 ORDER BY listed_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
        return [dict(r) for r in rows]

def buy_market_item(buyer_id: int, listing_id: int) -> Dict:
    with get_db() as conn:
        listing = conn.execute(
            "SELECT * FROM market WHERE id=? AND sold=0", (listing_id,)
        ).fetchone()
        if not listing:
            return {"success": False, "error": "Item tidak ditemukan atau sudah terjual"}

        listing = dict(listing)
        buyer = conn.execute("SELECT coins FROM players WHERE user_id=?", (buyer_id,)).fetchone()
        if not buyer or buyer["coins"] < listing["price"]:
            return {"success": False, "error": "Koin tidak cukup"}

        if listing["seller_id"] == buyer_id:
            return {"success": False, "error": "Tidak bisa membeli item sendiri"}

        # Deduct buyer coins
        conn.execute("UPDATE players SET coins=coins-? WHERE user_id=?",
                     (listing["price"], buyer_id))
        # Add coins to seller
        conn.execute("UPDATE players SET coins=coins+? WHERE user_id=?",
                     (listing["price"], listing["seller_id"]))
        # Add fish to buyer bag
        conn.execute("""
            INSERT INTO bag (user_id, fish_name, weight, rarity, location)
            VALUES (?, ?, ?, ?, 'Market')
        """, (buyer_id, listing["fish_name"], listing["weight"], listing["rarity"]))
        # Mark sold
        conn.execute("UPDATE market SET sold=1 WHERE id=?", (listing_id,))
        conn.commit()
        return {"success": True, "listing": listing}

def cancel_market_listing(seller_id: int, listing_id: int) -> bool:
    with get_db() as conn:
        row = conn.execute(
            "SELECT fish_bag_id FROM market WHERE id=? AND seller_id=? AND sold=0",
            (listing_id, seller_id)
        ).fetchone()
        if not row:
            return False
        # Return fish to bag (re-add)
        listing = conn.execute("SELECT * FROM market WHERE id=?", (listing_id,)).fetchone()
        if listing:
            conn.execute("""
                INSERT INTO bag (user_id, fish_name, weight, rarity, location)
                VALUES (?, ?, ?, ?, ?)
            """, (seller_id, listing["fish_name"], listing["weight"],
                  listing["rarity"], "Returned"))
        conn.execute("DELETE FROM market WHERE id=?", (listing_id,))
        conn.commit()
        return True

# ─────────────────────────────────────────────────────────────
# ROD UPGRADES
# ─────────────────────────────────────────────────────────────

def get_rod_upgrade(user_id: int) -> Dict:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM rod_upgrades WHERE user_id=?", (user_id,)
        ).fetchone()
        return dict(row) if row else {"level": 0, "luck_bonus": 0, "rare_bonus": 0, "total_spent": 0}

def upgrade_rod(user_id: int) -> Dict:
    """Attempt to upgrade rod. Returns result dict."""
    upgrade = get_rod_upgrade(user_id)
    current_level = upgrade["level"]
    max_level = 20
    if current_level >= max_level:
        return {"success": False, "error": "Upgrade sudah maksimal!"}

    cost = 500 + (current_level * 250)
    if not spend_coins(user_id, cost):
        return {"success": False, "error": f"Koin tidak cukup! Butuh {cost:,} koin"}

    new_level = current_level + 1
    new_luck = new_level * 3
    new_rare = new_level * 2

    with get_db() as conn:
        conn.execute("""
            UPDATE rod_upgrades
            SET level=?, luck_bonus=?, rare_bonus=?, total_spent=total_spent+?
            WHERE user_id=?
        """, (new_level, new_luck, new_rare, cost, user_id))
        conn.commit()

    return {"success": True, "new_level": new_level, "cost": cost,
            "luck_bonus": new_luck, "rare_bonus": new_rare}

# ─────────────────────────────────────────────────────────────
# MAPS
# ─────────────────────────────────────────────────────────────

def get_unlocked_maps(user_id: int) -> List[str]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT map_id FROM unlocked_maps WHERE user_id=?", (user_id,)
        ).fetchall()
        return [r["map_id"] for r in rows]

def unlock_map(user_id: int, map_id: str):
    with get_db() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO unlocked_maps (user_id, map_id) VALUES (?, ?)",
            (user_id, map_id)
        )
        conn.commit()

# ─────────────────────────────────────────────────────────────
# LEADERBOARD
# ─────────────────────────────────────────────────────────────

def get_leaderboard(category: str = "coins", limit: int = 10) -> List[Dict]:
    valid = {"coins": "coins", "level": "level", "total_caught": "total_caught",
             "total_earned": "total_earned"}
    col = valid.get(category, "coins")
    with get_db() as conn:
        rows = conn.execute(f"""
            SELECT user_id, username, full_name, {col} as value
            FROM players WHERE is_banned=0
            ORDER BY {col} DESC LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]

# ─────────────────────────────────────────────────────────────
# VIP
# ─────────────────────────────────────────────────────────────

def is_vip_active(player: Dict) -> bool:
    if not player.get("vip_expires"):
        return False
    return datetime.utcnow() < datetime.fromisoformat(player["vip_expires"])

def get_vip_bonus(player: Dict) -> Dict:
    from data.shop_data import VIP_TIERS
    if not is_vip_active(player):
        return {"luck": 0, "rare": 0, "xp": 0, "coin": 0}
    vip = VIP_TIERS.get(player.get("vip_type", ""), {})
    return {
        "luck": vip.get("luck_bonus", 0),
        "rare": vip.get("rare_bonus", 0),
        "xp": vip.get("xp_bonus", 0),
        "coin": vip.get("coin_bonus", 0),
    }

# ─────────────────────────────────────────────────────────────
# EVENTS
# ─────────────────────────────────────────────────────────────

def get_active_events() -> List[Dict]:
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        rows = conn.execute("""
            SELECT * FROM events
            WHERE is_active=1 AND start_date<=? AND end_date>=?
        """, (now, now)).fetchall()
        return [dict(r) for r in rows]

def get_all_events() -> List[Dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM events ORDER BY start_date DESC"
        ).fetchall()
        return [dict(r) for r in rows]

def add_sample_events():
    """Add sample events if none exist."""
    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) as c FROM events").fetchone()["c"]
        if count == 0:
            now = datetime.utcnow()
            events = [
                ("🎣 Festival Mancing Musim Hujan",
                 "Double XP dan koin selama event berlangsung! Chance ikan Rare meningkat 50%!",
                 "2x XP + 2x Koin + Rare +50%",
                 now.isoformat(),
                 (now + timedelta(days=7)).isoformat()),
                ("🏆 Turnamen Ikan Terbesar",
                 "Tangkap ikan terberat dan menangkan hadiah utama 50.000 koin!",
                 "50.000 Koin untuk pemenang",
                 now.isoformat(),
                 (now + timedelta(days=14)).isoformat()),
                ("💎 Event Ikan Langka",
                 "Chance Mythic dan Divine meningkat drastis! Jangan lewatkan!",
                 "Mythic +100% | Divine +50%",
                 now.isoformat(),
                 (now + timedelta(days=3)).isoformat()),
            ]
            for e in events:
                conn.execute(
                    "INSERT INTO events (title, description, reward, start_date, end_date) VALUES (?,?,?,?,?)",
                    e
                )
            conn.commit()
