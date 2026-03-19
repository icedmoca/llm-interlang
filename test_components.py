#!/usr/bin/env python3
"""Test AST parser and compression scorer without requiring bridge connection"""

from interlang_ast import InterlangParser
from compression import CompressionScorer
import json

print("Testing AST Parser...\n")

parser = InterlangParser()

test_cases = [
    ". prop ^ = xor",
    ". ? q vers -> state",
    ". * prop ^ = xor -> sync",
    ". test",
    ". sync state :h=abc123",
]

for test in test_cases:
    result = parser.parse(test)
    if hasattr(result, "to_dict"):
        print(f"Input: {test}")
        print(f"AST: {json.dumps(result.to_dict(), indent=2)}")
        print()
    else:
        print(f"Input: {test}")
        print(f"Error: {result}")
        print()

print("=" * 60)
print("\nTesting Compression Scorer...\n")

scorer = CompressionScorer()

test_pairs = [
    ("Propose a new operator for XOR logic", ". prop ^ = xor"),
    ("What is the current version and state?", ". ? q vers -> state"),
    ("Test message", ". test"),
    ("Synchronize state with hash abc123", ". sync state :h=abc123"),
]

for english, interlang in test_pairs:
    score = scorer.score(english, interlang)
    print(f"English: {english}")
    print(f"Interlang: {interlang}")
    print(f"Score: {score}")
    print()

print("Done!")
