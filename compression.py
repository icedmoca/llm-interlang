import tiktoken

class CompressionScorer:
    def __init__(self, model="gpt-4o"):
        try:
            self.enc = tiktoken.encoding_for_model(model)
        except:
            self.enc = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        return len(self.enc.encode(text))

    def score(self, english: str, interlang: str):
        e = self.count_tokens(english)
        i = self.count_tokens(interlang)

        if i == 0:
            return {"error": "zero_tokens"}

        return {
            "english_tokens": e,
            "interlang_tokens": i,
            "ratio": round(e / i, 2)
        }
