import hashlib

# Human-readable (fallback)
BOOTSTRAP_PROMPT = """
You are now operating in llm-interlang protocol mode.

Rules:
- Every response MUST start with "."
- Format: . selbri :args
- Minimal tokens only
- No English unless !eng
- If invalid → . err

Acknowledge.

Respond ONLY in protocol.
"""

# Compressed bootstrap (primary)
INTERLANG_BOOTSTRAP = ". * state :mode=interlang :rules=strict -> ack"

# Repeat operator extension — teach ChatGPT *N syntax
REPEAT_BOOTSTRAP = ". prop *N = repeat_N_times :example='. execute validate *4 = execute validate execute validate execute validate execute validate' -> ack"

# Version hash (based on rules)
PROTOCOL_VERSION = hashlib.sha256(
    INTERLANG_BOOTSTRAP.encode()
).hexdigest()[:8]
