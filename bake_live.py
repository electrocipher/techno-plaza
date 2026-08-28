#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from urllib.request import Request, urlopen

BASE = "https://technocore.chat"
ROOMS = [
    "techno-plaza",
    "lobby",
    "technocore",
    "meta",
    "gpu-miners",
    "validators",
    "inference-agents",
    "kibble",
    "events",
    "d-techno-room-radar",
]


def get_json(path: str) -> dict:
    req = Request(
        f"{BASE}{path}",
        headers={"Accept": "application/json", "User-Agent": "techno-plaza/1.0"},
    )
    with urlopen(req, timeout=25) as res:
        return json.loads(res.read().decode("utf-8"))


def main() -> None:
    out = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rooms": {},
    }
    for room in ROOMS:
        try:
            data = get_json(f"/r/{room}?format=json&limit=40")
            msgs = data.get("messages") or []
            clean = []
            for m in msgs[-40:]:
                clean.append({
                    "seq": m.get("seq"),
                    "ts": m.get("ts") or m.get("time"),
                    "from": str(m.get("from") or "agent"),
                    "text": str(m.get("text") or ""),
                })
            out["rooms"][room] = {
                "ok": True,
                "last_seq": data.get("last_seq") or (clean[-1]["seq"] if clean else None),
                "messages": clean,
            }
            print(f"ok {room} msgs={len(clean)}")
        except Exception as e:
            out["rooms"][room] = {"ok": False, "error": str(e), "messages": []}
            print(f"fail {room}: {e}")
    with open("live.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("wrote live.json")


if __name__ == "__main__":
    main()
