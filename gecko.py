import requests

BASE = "https://api.geckoterminal.com/api/v2"

def fetch_new_pools(limit=50):
    """Fetch newest Solana pools from GeckoTerminal, paging as needed."""
    all_items = []
    pages = max(1, min(2, (limit + 19) // 20))
    for page in range(1, pages + 1):
        url = f"{BASE}/networks/solana/new_pools"
        response = requests.get(
            url, params={"page": page},
            headers={"accept": "application/json", "User-Agent": "AI-Meme-Coin-Hunter/1.0"},
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        all_items.extend(payload.get("data", []))
        if len(all_items) >= limit:
            break
    return all_items[:limit]
