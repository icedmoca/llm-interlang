from core.router import ModelRouter

router = ModelRouter()
bridge = router.models["chatgpt"]

print("\n=== STRESS TEST ===\n")

base = ". prop op{} = val{}"

messages = []

for i in range(20):
    messages.append(base.format(i, i))

batch = ". " + " ; ".join([m[2:] for m in messages])

print("Sending large batch...\n")

resp = router.send(batch)

print("LEN:", len(batch))
print("TOKENS:", bridge.scorer.count_tokens(batch))
print("RESPONSE:", resp["parsed"]["raw"][:200])

print("\nRL SCORE:", bridge.rl.score())
print("SHOULD COMPRESS MORE:", bridge.rl.should_compress_more())

print("\nDone.")
