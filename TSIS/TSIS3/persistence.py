import json, os

SETTINGS_FILE    = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"

DEFAULTS = {"sound": True, "car_color": "blue", "difficulty": "medium", "username": ""}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            d = json.load(open(SETTINGS_FILE))
            return {**DEFAULTS, **d}
        except: pass
    return DEFAULTS.copy()

def save_settings(s):
    json.dump(s, open(SETTINGS_FILE, "w"), indent=2)

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try: return json.load(open(LEADERBOARD_FILE))
        except: pass
    return []

def save_score(name, score, dist, coins=0, hp=0):
    """Save a game result to leaderboard.json.
    Stores: name, score, dist, coins, hp_remaining, difficulty.
    Keeps top 10 sorted by score descending.
    """
    from persistence import load_settings   # avoid circular at module level
    cfg = load_settings()
    board = load_leaderboard()
    board.append({
        "name":         name,
        "score":        score,
        "dist":         int(dist),
        "coins":        int(coins),
        "hp":           int(hp),
        "difficulty":   cfg.get("difficulty", "medium"),
    })
    board = sorted(board, key=lambda x: x["score"], reverse=True)[:10]
    json.dump(board, open(LEADERBOARD_FILE, "w"), indent=2)
