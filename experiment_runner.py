from router import ModelRouter

router = ModelRouter()

print("Running full system test...\n")

# Step 1: English vs interlang
english = "Propose a new operator for XOR logic"
interlang = ". prop ^ = xor"

resp = router.send(interlang)

print("Response:", resp["parsed"]["raw"])

# Step 2: Compression test
bridge = router.models["chatgpt"]
score = bridge.score_compression(english, interlang)

print("\nCompression Score:")
print(score)

# Step 3: AST output
print("\nAST:")
print(resp["parsed"]["ast"])

print("\nDone.")
