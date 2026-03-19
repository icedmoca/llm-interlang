import re


class InterlangTranslator:
    def to_english(self, message: str) -> str:
        message = message.replace(".", "").strip()

        parts = message.split(";")

        english_parts = []

        for p in parts:
            p = p.strip()

            if not p:
                continue

            tokens = p.split()

            if not tokens:
                continue

            # handle reference tokens
            if tokens[0].startswith("$"):
                english_parts.append(f"ref {tokens[0]}")
                continue

            # handle *N repeat patterns
            match = re.search(r"\*(\d+)", p)
            if match:
                count = int(match.group(1))
                base = p.split("*")[0].strip()
                english_parts.append(" ".join([base] * count))
                continue

            selbri = tokens[0]

            if selbri in ["prop"]:
                english_parts.append(f"define {p}")
            elif selbri in ["acc"]:
                english_parts.append(f"accept {p}")
            elif selbri in ["state"]:
                english_parts.append(f"set state {p}")
            elif selbri in ["sync"]:
                english_parts.append("synchronize state")
            elif selbri in ["q"]:
                english_parts.append(f"query {p}")
            else:
                english_parts.append(f"execute {p}")

        return ". ".join(english_parts)
