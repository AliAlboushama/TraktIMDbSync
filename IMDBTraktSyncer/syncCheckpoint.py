import hashlib
import json
import os
from datetime import datetime, timezone


def _utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


class SyncCheckpointManager:
    def __init__(self, base_directory):
        self.file_path = os.path.join(base_directory, "sync_checkpoint.json")

    def _load(self):
        if not os.path.exists(self.file_path):
            return {"phases": {}}

        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, dict):
                    data.setdefault("phases", {})
                    return data
        except (OSError, json.JSONDecodeError):
            pass

        return {"phases": {}}

    def _save(self, data):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, separators=(", ", ": "))

    def _ensure_phase(self, phase_name, total_items):
        data = self._load()
        phase = data["phases"].setdefault(
            phase_name,
            {
                "started_at": _utc_now_iso(),
                "updated_at": _utc_now_iso(),
                "total_items": total_items,
                "completed_keys": [],
            },
        )
        phase["total_items"] = total_items
        phase["updated_at"] = _utc_now_iso()
        self._save(data)
        return phase

    def _item_key(self, item):
        key_data = {
            "IMDB_ID": item.get("IMDB_ID"),
            "Type": item.get("Type"),
            "Rating": item.get("Rating"),
            "WatchedAt": item.get("WatchedAt"),
            "Spoiler": item.get("Spoiler"),
        }

        comment = item.get("Comment")
        if comment is not None:
            key_data["CommentHash"] = hashlib.sha1(comment.encode("utf-8")).hexdigest()

        serialized = json.dumps(key_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha1(serialized.encode("utf-8")).hexdigest()

    def get_pending_items(self, phase_name, items):
        phase = self._ensure_phase(phase_name, len(items))
        completed = set(phase.get("completed_keys", []))
        pending_items = [
            item for item in items if self._item_key(item) not in completed
        ]
        completed_count = len(items) - len(pending_items)
        return pending_items, completed_count

    def mark_item_completed(self, phase_name, item):
        data = self._load()
        phase = data["phases"].setdefault(
            phase_name,
            {
                "started_at": _utc_now_iso(),
                "updated_at": _utc_now_iso(),
                "total_items": 0,
                "completed_keys": [],
            },
        )
        item_key = self._item_key(item)
        completed_keys = phase.setdefault("completed_keys", [])
        if item_key not in completed_keys:
            completed_keys.append(item_key)
        phase["updated_at"] = _utc_now_iso()
        self._save(data)

    def mark_items_completed(self, phase_name, items):
        if not items:
            return
        data = self._load()
        phase = data["phases"].setdefault(
            phase_name,
            {
                "started_at": _utc_now_iso(),
                "updated_at": _utc_now_iso(),
                "total_items": len(items),
                "completed_keys": [],
            },
        )
        completed_keys = set(phase.setdefault("completed_keys", []))
        for item in items:
            completed_keys.add(self._item_key(item))
        phase["completed_keys"] = list(completed_keys)
        phase["updated_at"] = _utc_now_iso()
        self._save(data)

    def complete_phase(self, phase_name):
        data = self._load()
        if phase_name in data.get("phases", {}):
            del data["phases"][phase_name]
            self._save(data)

    def clear_all(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
