import random
from typing import Dict, Optional, Tuple
from data.fish_data import FISH_DATA, RARITY_CHANCES
from data.shop_data import RODS, BAITS, MAPS


def calculate_catch_chances(
    rod_id: str,
    bait_id: str,
    map_id: str,
    rod_upgrade_bonus: Dict,
    boost_bonus: Dict,
    vip_bonus: Dict,
    player_level: int,
) -> Dict[str, float]:
    """Calculate final rarity chances based on all bonuses."""
    rod = RODS.get(rod_id, RODS["rod_bamboo"])
    bait = BAITS.get(bait_id, BAITS["bait_worm"])
    location = MAPS.get(map_id, MAPS["map_kolam"])

    # Total luck & rare bonuses
    total_luck = (
        rod.get("luck_bonus", 0)
        + bait.get("luck_bonus", 0)
        + rod_upgrade_bonus.get("luck_bonus", 0)
        + boost_bonus.get("luck", 0)
        + vip_bonus.get("luck", 0)
        + min(player_level * 0.5, 30)  # max 30 from level
    )
    total_rare = (
        rod.get("rare_bonus", 0)
        + bait.get("rare_bonus", 0)
        + rod_upgrade_bonus.get("rare_bonus", 0)
        + boost_bonus.get("rare", 0)
        + vip_bonus.get("rare", 0)
    )
    rare_multi = location["rare_multiplier"]

    # Start from base chances
    chances = dict(RARITY_CHANCES)

    # Apply rare multiplier to Rare+
    for rarity in ["Rare", "Epic", "Legendary", "Mythic", "Divine"]:
        chances[rarity] *= rare_multi

    # Shift weight from Common → higher tiers based on luck
    luck_shift = total_luck * 0.1  # each luck point = 0.1% shift
    rare_shift = total_rare * 0.15

    chances["Common"] = max(5, chances["Common"] - luck_shift - rare_shift)
    chances["Uncommon"] = max(5, chances["Uncommon"] - luck_shift * 0.3)
    chances["Rare"] += luck_shift * 0.4 + rare_shift * 0.5
    chances["Epic"] += luck_shift * 0.3 + rare_shift * 0.3
    chances["Legendary"] += luck_shift * 0.2 + rare_shift * 0.15
    chances["Mythic"] += luck_shift * 0.06 + rare_shift * 0.04
    chances["Divine"] += luck_shift * 0.04 + rare_shift * 0.01

    # Filter by location's allowed fish types
    allowed = location["fish_types"]
    if "Mythic" not in allowed:
        chances["Mythic"] = 0
    if "Divine" not in allowed:
        chances["Divine"] = 0
    if "Legendary" not in allowed:
        chances["Legendary"] = 0
    if "Epic" not in allowed:
        chances["Epic"] = 0
    if "Rare" not in allowed:
        chances["Rare"] = 0

    # Normalize to 100%
    total = sum(chances.values())
    if total > 0:
        chances = {k: (v / total) * 100 for k, v in chances.items()}

    return chances


def pick_rarity(chances: Dict[str, float]) -> str:
    """Pick a rarity based on weighted chances."""
    roll = random.uniform(0, 100)
    cumulative = 0.0
    for rarity, chance in chances.items():
        cumulative += chance
        if roll <= cumulative:
            return rarity
    return "Common"


def pick_fish(rarity: str) -> Optional[str]:
    """Pick a random fish of the given rarity."""
    candidates = [name for name, data in FISH_DATA.items() if data["rarity"] == rarity]
    if not candidates:
        candidates = [name for name, data in FISH_DATA.items() if data["rarity"] == "Common"]
    return random.choice(candidates) if candidates else None


def calculate_fish_weight(fish_name: str) -> float:
    """Generate a random weight for a fish."""
    fish = FISH_DATA.get(fish_name)
    if not fish:
        return 0.5
    weight = random.uniform(fish["min_weight"], fish["max_weight"])
    # Rare chance of trophy catch (1.5x-2x max weight)
    if random.random() < 0.05:
        weight = min(fish["max_weight"] * 1.8, weight * 1.5)
    return round(weight, 2)


def calculate_coin_reward(
    fish_name: str,
    weight: float,
    boost_coin: int = 0,
    vip_coin: int = 0,
    market_price: Optional[int] = None,
) -> int:
    """Calculate coins earned from selling a fish."""
    fish = FISH_DATA.get(fish_name)
    if not fish:
        return 10

    base = fish["sell_price"]
    weight_bonus = weight * 10
    total = int(base + weight_bonus)

    if market_price:
        total = market_price

    # Apply boosts
    total = int(total * (1 + (boost_coin + vip_coin) / 100))
    return max(1, total)


def do_fishing(
    user_id: int,
    rod_id: str,
    bait_id: str,
    map_id: str,
    rod_upgrade: Dict,
    boost_bonus: Dict,
    vip_bonus: Dict,
    player_level: int,
) -> Dict:
    """
    Main fishing function.
    Returns: {
        fish_name, rarity, weight, xp_earned, emoji,
        is_rare_catch, chances_used
    }
    """
    chances = calculate_catch_chances(
        rod_id, bait_id, map_id,
        rod_upgrade, boost_bonus, vip_bonus, player_level
    )

    rarity = pick_rarity(chances)
    fish_name = pick_fish(rarity)
    if not fish_name:
        return {"success": False, "error": "Tidak ada ikan yang tertangkap"}

    weight = calculate_fish_weight(fish_name)
    fish_data = FISH_DATA[fish_name]

    # XP with boost
    base_xp = fish_data["xp"]
    xp_multi = 1 + (boost_bonus.get("xp", 0) + vip_bonus.get("xp", 0)) / 100
    xp_earned = int(base_xp * xp_multi)

    is_rare = rarity in ["Epic", "Legendary", "Mythic", "Divine"]

    return {
        "success": True,
        "fish_name": fish_name,
        "rarity": rarity,
        "weight": weight,
        "emoji": fish_data["emoji"],
        "xp_earned": xp_earned,
        "is_rare_catch": is_rare,
        "chances": chances,
    }


def get_fishing_cooldown(map_id: str, rod_id: str, vip_active: bool) -> int:
    """Get cooldown in seconds for this map/rod combo."""
    location = MAPS.get(map_id, MAPS["map_kolam"])
    base_cd = location["catch_time"]
    rod = RODS.get(rod_id, RODS["rod_bamboo"])
    speed = rod.get("catch_speed", 1.0)
    cd = int(base_cd / speed)
    if vip_active:
        cd = max(5, int(cd * 0.7))
    return cd
