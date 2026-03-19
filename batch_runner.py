from router import ModelRouter

router = ModelRouter()
bridge = router.models["chatgpt"]

print("\n=== BATCH TEST ===\n")

messages = [
    ". prop ^ = xor",
    ". acc ^",
    ". state :mode=logic",
    ". q state",
    ". sync"
]

# combine into one chained message
batch = ". " + " ; ".join([m[2:] for m in messages])

print("BATCH MESSAGE:")
print(batch)

resp = router.send(batch)

print("\nRESPONSE:")
print(resp["parsed"]["raw"])

print("\nAST:")
print(resp["parsed"]["ast"])

print("\nEXEC:")
print(resp["parsed"]["execution"])

print("\nCOMPRESSION:")
score = bridge.score_compression(
    "Define xor, accept it, set mode, query state, sync",
    batch
)
print(score)

print("\nDone.")
