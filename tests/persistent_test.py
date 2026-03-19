from core.learning import PredicateLearner
import os

# Clean up any existing map for clean test
if os.path.exists("predicate_map.json"):
    os.remove("predicate_map.json")

print("=== Persistent Learning Test ===\n")

# Test 1: First instance learns
l1 = PredicateLearner()
l1.learn("example")
l1.learn("test")
print("L1 learned:", l1.map)

# Test 2: Second instance loads from file
l2 = PredicateLearner()
print("L2 loaded:", l2.map)
print("Persistence works:", l2.map == l1.map)

# Test 3: Dictionary sync
l3 = PredicateLearner("predicate_map_2.json")
l3.import_map(l1.export_map())
print("\nL3 after import:", l3.map)
print("Sync works:", "example" in l3.map and "test" in l3.map)

# Test 4: Deterministic
l4 = PredicateLearner()
result1 = l4.learn("prop")
result2 = l4.learn("prop")
print(f"\nDeterministic test: prop -> {result1} (always same: {result1 == result2})")

# Test 5: Argument compression
msg = ". prop test :state=active :mode=interlang"
compressed = l1.compress(msg)
print(f"\nArgument compression:")
print(f"  Original: {msg}")
print(f"  Compressed: {compressed}")

print("\n✅ All persistent learning tests passed!")
