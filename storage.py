import json
import os
from pathlib import Path

STORAGE_DIR = Path("run_sessions")
STORAGE_DIR.mkdir(exist_ok=True)


def save_session(session: dict):
    session_id = session.get("session_id", "unknown")
    file_path = STORAGE_DIR / f"{session_id}.json"
    with open(file_path, "w") as f:
        json.dump(session, f, indent=2)


def load_session(session_id: str) -> dict:
    file_path = STORAGE_DIR / f"{session_id}.json"
    if not file_path.exists():
        return {}
    with open(file_path) as f:
        return json.load(f)


def load_all_sessions() -> list:
    sessions = []
    for file_path in sorted(STORAGE_DIR.glob("*.json")):
        with open(file_path) as f:
            try:
                sessions.append(json.load(f))
            except json.JSONDecodeError:
                pass
    return sessions


def clear_all_sessions():
    for file_path in STORAGE_DIR.glob("*.json"):
        file_path.unlink()
