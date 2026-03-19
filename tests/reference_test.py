from core.router import ModelRouter

router = ModelRouter()
bridge = router.models["chatgpt"]

print("\n=== REFERENCE COMPRESSION TEST ===\n")

msg = ". prop op1 = value1 ; prop op2 = value2 ; prop op3 = value3"

resp = router.send(msg)

print("RAW:", resp["parsed"]["raw"])

print("\nREFERENCE MAP:")
print(bridge.refs.export())

print("\nCOMPRESSION SCORE:")
english = "define op value three times"
compressed = bridge.refs.compress(
    bridge.learner.compress(msg)
)
expanded = bridge.refs.expand(compressed)
score = bridge.score_compression(expanded, compressed)
print("Compressed:", compressed)
print("Expanded:", expanded)
print("Score:", score)

print("\nDone.")
