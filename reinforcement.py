class ReinforcementLoop:
    def __init__(self):
        self.history = []

    def record(self, english_tokens, interlang_tokens):
        if interlang_tokens == 0:
            return

        # ignore extremely small samples (noise)
        if english_tokens < 6:
            return

        self.history.append({
            "english": english_tokens,
            "interlang": interlang_tokens
        })

    def score(self):
        if not self.history:
            return 0

        ratios = [
            h["english"] / h["interlang"]
            for h in self.history
            if h["interlang"] > 0
        ]

        return sum(ratios) / len(ratios)

    def should_compress_more(self):
        return self.score() < 2.0
