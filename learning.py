import json
import hashlib
import os


class PredicateLearner:
    # Native protocol predicates — never compress these
    PROTECTED = {
        "prop", "acc", "rej", "state", "sync", "q", "corr",
        "data", "test", "vers", "plan", "validate", "execute",
        "err", "ack", "def", "run", "get", "set", "del",
    }

    def __init__(self, path="predicate_map.json"):
        self.path = path
        self.map = {}
        self.arg_map = {
            "state": "s",
            "mode": "m",
            "rules": "r",
            "value": "v",
            "data": "d"
        }
        self._load()

    # ── deterministic short token ──
    def generate_short(self, original):
        h = hashlib.sha1(original.encode()).hexdigest()
        return h[:2]

    # ── learning ──
    def learn(self, original: str) -> str:
        if original in self.PROTECTED:
            return original

        if original in self.map:
            return self.map[original]

        short = self.generate_short(original)
        self.map[original] = short
        self._save()
        return short

    # ── predicate compression ──
    def compress(self, message: str) -> str:
        parts = message.split()

        if len(parts) < 2:
            return message

        selbri = parts[1]
        parts[1] = self.learn(selbri)

        # arg compression
        for i in range(len(parts)):
            if parts[i].startswith(":"):
                arg_part = parts[i][1:]  # Remove :
                # Handle :key=value format
                if "=" in arg_part:
                    key, val = arg_part.split("=", 1)
                    if key in self.arg_map:
                        parts[i] = ":" + self.arg_map[key] + "=" + val
                else:
                    # Handle :key format
                    if arg_part in self.arg_map:
                        parts[i] = ":" + self.arg_map[arg_part]

        return " ".join(parts)

    # ── expand ──
    def expand(self, message: str) -> str:
        reverse = {v: k for k, v in self.map.items()}
        reverse_args = {v: k for k, v in self.arg_map.items()}

        parts = message.split()

        if len(parts) >= 2:
            selbri = parts[1]
            if selbri in reverse:
                parts[1] = reverse[selbri]

        for i in range(len(parts)):
            if parts[i].startswith(":"):
                arg_part = parts[i][1:]  # Remove :
                # Handle :key=value format
                if "=" in arg_part:
                    key, val = arg_part.split("=", 1)
                    if key in reverse_args:
                        parts[i] = ":" + reverse_args[key] + "=" + val
                else:
                    # Handle :key format
                    if arg_part in reverse_args:
                        parts[i] = ":" + reverse_args[arg_part]

        return " ".join(parts)

    # ── persistence ──
    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self.map, f)

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                self.map = json.load(f)

    # ── sync ──
    def export_map(self):
        return self.map

    def import_map(self, other: dict):
        self.map.update(other)
        self._save()
