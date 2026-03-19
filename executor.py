from typing import Dict, Any


class ExecutionEngine:
    def __init__(self):
        self.memory = {}
        self.last = None

    def execute(self, ast: Dict) -> Dict:
        if "error" in ast:
            return {"error": "invalid_ast"}

        selbri = ast.get("selbri")
        args = ast.get("args", [])

        handler = getattr(self, f"handle_{selbri}", self.handle_unknown)

        result = handler(args)

        self.last = result
        return result

    # ── Core handlers ─────────────────────────

    def handle_prop(self, args):
        if not args:
            return {"error": "no_prop"}

        expr = args[0]

        if "=" in expr:
            key, val = [x.strip() for x in expr.split("=", 1)]
            self.memory[key] = val
            return {"status": "defined", "key": key, "value": val}

        return {"status": "prop_received", "expr": expr}

    def substitute_definitions(self, message: str) -> str:
        """Auto-substitute stored definitions in message"""
        # Simple substitution: if message contains a key from memory, use it
        # Example: ". prop ^ = xor" stores ^ -> xor
        # Future: ". use ^" becomes ". use xor" (or similar expansion)
        # For now, just return message - this is a hook for future expansion
        return message

    def get_memory(self):
        """Get current memory state"""
        return self.memory.copy()

    def handle_q(self, args):
        return {"query": args}

    def handle_state(self, args):
        return {"memory": self.memory}

    def handle_sync(self, args):
        return {"status": "synced", "state_size": len(self.memory)}

    def handle_acc(self, args):
        return {"status": "accepted"}

    def handle_rej(self, args):
        return {"status": "rejected"}

    def handle_data(self, args):
        return {"data": args}

    def handle_unknown(self, args):
        return {"status": "unknown", "args": args}
