from router import ModelRouter

router = ModelRouter()
bridge = router.models["chatgpt"]

print("\n=== PATTERN OPTIMIZATION TEST ===\n")

msg = ". execute validate ; execute validate ; execute validate ; execute validate"

print("ORIGINAL:", msg)

resp = router.send(msg)

print("\nRESPONSE:", resp["parsed"]["raw"])

compressed = bridge.refs.compress(
    bridge.learner.compress(
        bridge.optimizer.optimize(msg)
    )
)

expanded = bridge.refs.expand(compressed)

score = bridge.score_compression(expanded, compressed)

print("\nCOMPRESSED:", compressed)
print("EXPANDED:", expanded)
print("SCORE:", score)

print("\nDone.")
