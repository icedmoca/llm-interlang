class BatchOptimizer:
    def should_batch(self, messages, scorer):
        if len(messages) < 3:
            return False

        combined = ". " + " ; ".join([m[2:] if m.startswith(". ") else m for m in messages])

        english = " ".join(messages)

        score = scorer.score(english, combined)

        if "error" in score:
            return False

        return score["ratio"] > 1.2
