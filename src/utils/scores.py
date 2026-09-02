import json
from pathlib import Path

SCORES_PATH = Path(__file__).resolve().parents[2] / "data" / "scores.json"
MAX_ENTRIES = 10
DEFAULT_NAME = "Jogador"


def load_scores() -> list[dict]:
    if not SCORES_PATH.exists():
        return []

    try:
        with open(SCORES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    scores = [entry for entry in data if isinstance(entry, dict) and "name" in entry and "score" in entry]
    scores.sort(key=lambda e: e.get("score", 0), reverse=True)
    return scores


def save_score(name: str, score: int) -> list[dict]:
    clean_name = (name or "").strip()[:16] or DEFAULT_NAME

    scores = load_scores()
    scores.append({"name": clean_name, "score": int(score)})
    scores.sort(key=lambda e: e.get("score", 0), reverse=True)
    scores = scores[:MAX_ENTRIES]

    SCORES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SCORES_PATH, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)

    return scores
