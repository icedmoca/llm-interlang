class ReferenceCompressor:
    def __init__(self):
        self.memory = {}
        self.reverse = {}
        self.counter = 1

    def _next_ref(self):
        ref = f"${self.counter}"
        self.counter += 1
        return ref

    def compress(self, message: str) -> str:
        tokens = message.split()

        new_tokens = []

        for tok in tokens:
            if tok in self.reverse:
                new_tokens.append(self.reverse[tok])
            else:
                # only store meaningful tokens (skip punctuation-like)
                if len(tok) > 3 and not tok.startswith(":"):
                    ref = self._next_ref()
                    self.memory[ref] = tok
                    self.reverse[tok] = ref
                    new_tokens.append(ref)
                else:
                    new_tokens.append(tok)

        return " ".join(new_tokens)

    def expand(self, message: str) -> str:
        tokens = message.split()

        expanded = []

        for tok in tokens:
            if tok in self.memory:
                expanded.append(self.memory[tok])
            else:
                expanded.append(tok)

        return " ".join(expanded)

    def export(self):
        return self.memory

    def import_refs(self, refs: dict):
        self.memory.update(refs)
        for k, v in refs.items():
            self.reverse[v] = k
