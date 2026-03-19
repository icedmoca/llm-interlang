#!/usr/bin/env python3
"""Test integration without requiring bridge connection"""

from bridge.bridge_protocol import InterlangBridge
from core.interlang_ast import InterlangParser
from core.executor import ExecutionEngine
from core.learning import PredicateLearner
from core.reinforcement import ReinforcementLoop
import json

print("=== INTEGRATION TEST (No Bridge Required) ===\n")

# Create bridge instance
bridge = InterlangBridge(mode="cdp", wait=30)

# Test 1: Learning compression
print("1. Testing Predicate Learning:")
msg1 = ". prop test"
msg2 = ". prop test"
compressed1 = bridge.learner.compress(msg1)
compressed2 = bridge.learner.compress(msg2)
print(f"   Original: {msg1}")
print(f"   Compressed 1: {compressed1}")
print(f"   Compressed 2: {compressed2}")
print(f"   Learner map: {bridge.learner.map}")
print()

# Test 2: AST parsing
print("2. Testing AST Parsing:")
test_msg = ". prop newop = logical-xor"
ast = bridge.parser.parse(test_msg)
ast_dict = ast.to_dict() if hasattr(ast, "to_dict") else ast
print(f"   Message: {test_msg}")
print(f"   AST: {json.dumps(ast_dict, indent=2)}")
print()

# Test 3: Execution
print("3. Testing Execution Engine:")
execution = bridge.executor.execute(ast_dict)
print(f"   Execution result: {execution}")
print(f"   Memory: {bridge.executor.memory}")
print()

# Test 4: Compression scoring
print("4. Testing Compression Scoring:")
score = bridge.score_compression("Propose a new operator for logical XOR", test_msg)
print(f"   Score: {score}")
print()

# Test 5: Reinforcement loop
print("5. Testing Reinforcement Loop:")
bridge.rl.record(10, 5)
bridge.rl.record(8, 4)
bridge.rl.record(12, 6)
print(f"   Average compression ratio: {bridge.rl.score():.2f}")
print(f"   Should compress more: {bridge.rl.should_compress_more()}")
print()

# Test 6: Full pipeline (simulated)
print("6. Testing Full Pipeline (Simulated):")
# Simulate what happens in send()
message = ". prop newop = logical-xor"
message = bridge._enforce_protocol(message)
compressed = bridge.learner.compress(message)
print(f"   Original: {message}")
print(f"   Compressed: {compressed}")

# Simulate parsing a response
simulated_response = ". ack prop newop"
parsed = bridge._parse_response(simulated_response)
print(f"   Simulated response: {simulated_response}")
print(f"   Parsed AST: {json.dumps(parsed['ast'], indent=2)}")

# Execute
if "ast" in parsed and isinstance(parsed["ast"], dict):
    execution = bridge.executor.execute(parsed["ast"])
    parsed["execution"] = execution
    print(f"   Execution: {execution}")

print("\n=== All Integration Tests Passed ===")
