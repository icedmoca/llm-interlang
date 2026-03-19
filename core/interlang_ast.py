import re

class Node:
    def __init__(self, selbri, args=None, flags=None):
        self.selbri = selbri
        self.args = args or []
        self.flags = flags or []

    def to_dict(self):
        return {
            "selbri": self.selbri,
            "args": [
                a.to_dict() if isinstance(a, Node) else a
                for a in self.args
            ],
            "flags": self.flags
        }


class InterlangParser:
    def parse(self, text: str):
        text = text.strip()
        if not text.startswith("."):
            return {"error": "invalid_start"}

        text = text[1:].strip()

        flags, text = self._parse_flags(text)
        selbri, rest = self._parse_selbri(text)
        args = self._parse_args(rest)

        return Node(selbri, args, flags)

    def _parse_flags(self, text):
        flags = []
        while text and text[0] in "*!?":
            flags.append(text[0])
            text = text[1:]
        return flags, text.strip()

    def _parse_selbri(self, text):
        parts = text.split(" ", 1)
        selbri = parts[0]
        rest = parts[1] if len(parts) > 1 else ""
        return selbri, rest.strip()

    def _parse_args(self, text):
        args = []
        tokens = re.split(r'(\(|\)|:)', text)

        stack = []
        current = []

        for tok in tokens:
            tok = tok.strip()
            if not tok:
                continue

            if tok == "(":
                stack.append(current)
                current = []
            elif tok == ")":
                node = current
                current = stack.pop() if stack else []
                current.append(node)
            elif tok == ":":
                continue
            else:
                current.append(tok)

        return current
