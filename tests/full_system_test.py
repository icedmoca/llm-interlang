from core.router import ModelRouter

router = ModelRouter()

print("=== FULL SYSTEM TEST ===\n")

msg = ". prop newop = logical-xor"

resp = router.send(msg)

print("RAW:", resp["parsed"]["raw"])
print("AST:", resp["parsed"]["ast"])
print("EXEC:", resp["parsed"]["execution"])

bridge = router.models["chatgpt"]

print("\nCompression score:")
print(bridge.rl.score())

print("\nShould compress more?:")
print(bridge.rl.should_compress_more())

print("\nDone.")
