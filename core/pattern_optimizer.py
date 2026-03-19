import re
from collections import Counter


class PatternOptimizer:
    def __init__(self):
        pass

    def optimize(self, message: str) -> str:
        if not message.startswith("."):
            return message

        body = message[1:].strip()

        # split chained operations
        parts = [p.strip() for p in body.split(";") if p.strip()]

        if len(parts) < 2:
            return message

        # detect repeated segments
        counts = Counter(parts)

        # find high-frequency patterns
        repeated = [p for p, c in counts.items() if c > 1]

        if not repeated:
            return message

        # simple rewrite: group repeats
        optimized_parts = []
        used = set()

        for p in parts:
            if p in repeated:
                if p not in used:
                    optimized_parts.append(f"{p} *{counts[p]}")
                    used.add(p)
            else:
                optimized_parts.append(p)

        optimized = ". " + " ; ".join(optimized_parts)
        return optimized
