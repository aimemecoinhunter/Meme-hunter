from datetime import datetime, timezone
from urllib.parse import quote

def _number(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0

def score_pool(item):
    attr = item.get("attributes", {})
    relationships = item.get("relationships", {})
    name = attr.get("name") or "Token necunoscut"
    address = attr.get("address") or ""
    liquidity = _number(attr.get("reserve_in_usd"))
    volume = _number((attr.get("volume_usd") or {}).get("h1"))
    created = attr.get("pool_created_at")
    if not address or not created:
        return None
    try:
        created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
        age_hours = max(0, (datetime.now(timezone.utc) - created_dt).total_seconds() / 3600)
    except Exception:
        age_hours = 999999

    # Transparent heuristic score: liquidity 40, volume 35, freshness 25.
    liq_score = min(40, (liquidity / 50000) * 40)
    vol_score = min(35, (volume / 25000) * 35)
    age_score = max(0, 25 * (1 - age_hours / 72))
    score = round(liq_score + vol_score + age_score)
    reasons = []
    reasons.append("lichiditate bună" if liquidity >= 20000 else "lichiditate redusă")
    reasons.append("volum 1h activ" if volume >= 5000 else "volum 1h redus")
    reasons.append("pool recent" if age_hours <= 24 else "pool mai vechi")
    return {
        "Token": name,
        "Scor": int(max(0, min(100, score))),
        "Lichiditate USD": round(liquidity, 2),
        "Volum 1h USD": round(volume, 2),
        "Vechime ore": round(age_hours, 1),
        "Explicație": ", ".join(reasons),
        "Adresa pool": address,
        "DEX Screener": f"https://dexscreener.com/solana/{quote(address)}",
    }
