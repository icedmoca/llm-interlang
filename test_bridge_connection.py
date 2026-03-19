#!/usr/bin/env python3
"""Test actual bridge connection to ChatGPT"""

from bridge_protocol import InterlangBridge
import json

print("=== Testing Bridge Connection to ChatGPT ===\n")

# Create bridge instance
bridge = InterlangBridge(mode="cdp", wait=30, cdp_port=9222)

print("Attempting to connect to Chromium CDP on port 9222...")
print("Make sure Chromium is running with: ./start_chromium.sh\n")

try:
    # Test 1: Simple test message
    print("1. Sending test message: '. test'")
    result1 = bridge.send(". test")
    
    print(f"   Input: {result1['input']}")
    print(f"   Raw response: {result1['raw'][:200]}...")  # First 200 chars
    print(f"   Valid: {result1['valid']}")
    print(f"   AST: {json.dumps(result1['parsed']['ast'], indent=2)}")
    if 'execution' in result1['parsed']:
        print(f"   Execution: {result1['parsed']['execution']}")
    print()
    
    # Test 2: Proposal message
    print("2. Sending proposal: '. prop ^ = xor'")
    result2 = bridge.send(". prop ^ = xor")
    
    print(f"   Input: {result2['input']}")
    print(f"   Raw response: {result2['raw'][:200]}...")
    print(f"   Valid: {result2['valid']}")
    print(f"   AST: {json.dumps(result2['parsed']['ast'], indent=2)}")
    if 'execution' in result2['parsed']:
        print(f"   Execution: {result2['parsed']['execution']}")
    print()
    
    # Show learning map
    print("3. Learning map (compressed predicates):")
    print(f"   {bridge.learner.map}")
    print()
    
    # Show reinforcement score
    print("4. Reinforcement loop score:")
    print(f"   Average compression: {bridge.rl.score():.2f}x")
    print(f"   Should compress more: {bridge.rl.should_compress_more()}")
    print()
    
    # Show executor memory
    print("5. Executor memory (stored definitions):")
    print(f"   {bridge.executor.memory}")
    print()
    
    print("=== Bridge Test Complete ===")
    
except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    print("\nMake sure:")
    print("  1. Chromium is running with CDP: ./start_chromium.sh")
    print("  2. ChatGPT page is loaded in Chromium")
    print("  3. You're logged into ChatGPT")
    import traceback
    traceback.print_exc()
