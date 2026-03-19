from core.router import ModelRouter

print("\n=== LLM-INTERLANG FULL VALIDATION ===\n")

router = ModelRouter()
bridge = router.models["chatgpt"]

# ── Step 1: bootstrap + ping ──
print("\n[1] Bootstrap + Test")
r1 = router.send(". test")
print("RAW:", r1["parsed"]["raw"])
print("VALID:", r1["valid"])

# ── Step 2: AST + execution ──
print("\n[2] AST + Execution")
r2 = router.send(". prop ^ = xor")
print("AST:", r2["parsed"]["ast"])
print("EXEC:", r2["parsed"]["execution"])

# ── Step 3: compression scoring ──
print("\n[3] Compression")
english = "Define a new logical XOR operator"
interlang = ". prop ^ = xor"

score = bridge.score_compression(english, interlang)
print("SCORE:", score)

# ── Step 4: learning system ──
print("\n[4] Learning (predicate compression)")
compressed = bridge.learner.compress(". prop testop = value")
expanded = bridge.learner.expand(compressed)

print("COMPRESSED:", compressed)
print("EXPANDED:", expanded)
print("MAP:", bridge.learner.map)

# ── Step 5: reinforcement ──
print("\n[5] Reinforcement")
print("AVG SCORE:", bridge.rl.score())
print("SHOULD COMPRESS MORE:", bridge.rl.should_compress_more())

# ── Step 6: drift test ──
print("\n[6] Drift Detection Test")
r3 = router.send("This is invalid English message")
print("RECOVERED RAW:", r3["parsed"]["raw"])

# ── Step 7: version sync ──
print("\n[7] Version Sync")
v = bridge.version_sync()
print("VERSION MSG:", v)

print("\n=== DONE ===\n")
