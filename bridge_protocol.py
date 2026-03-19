import json
import time
import hashlib
from typing import List, Dict, Optional

from chatgpt_bridge import xdotool_send, cdp_send
from interlang_ast import InterlangParser
from compression import CompressionScorer
from executor import ExecutionEngine
from learning import PredicateLearner
from reinforcement import ReinforcementLoop
from protocol_bootstrap import BOOTSTRAP_PROMPT, INTERLANG_BOOTSTRAP, PROTOCOL_VERSION, REPEAT_BOOTSTRAP
from translator import InterlangTranslator
from reference import ReferenceCompressor
from pattern_optimizer import PatternOptimizer


class InterlangBridge:
    def __init__(self, mode="cdp", wait=30, cdp_port=9222, max_retries=2):
        self.mode = mode
        self.wait = wait
        self.cdp_port = cdp_port
        self.max_retries = max_retries
        self.history: List[Dict] = []
        self.parser = InterlangParser()
        self.scorer = CompressionScorer()
        self.executor = ExecutionEngine()
        self.learner = PredicateLearner()
        self.rl = ReinforcementLoop()
        self.bootstrapped = False
        self.protocol_version = PROTOCOL_VERSION
        self.last_valid = True
        self.translator = InterlangTranslator()
        self.refs = ReferenceCompressor()
        self.optimizer = PatternOptimizer()

    # ── Core send ─────────────────────────────────────────

    def send(self, message: str) -> Dict:
        if not self.bootstrapped:
            self.bootstrap()
        
        # Proactive drift prevention - catch English before sending
        if " " in message and not message.startswith("."):
            # Convert English to protocol correction format
            message = ". corr " + message
        
        message = self._enforce_protocol(message)

        # prevent accidental english
        if not message.startswith("."):
            message = ". corr " + message

        # pattern optimization
        message = self.optimizer.optimize(message)

        # predicate + arg compression
        message = self.learner.compress(message)

        # reference compression
        message = self.refs.compress(message)

        sent_message = message  # capture final compressed form

        for attempt in range(self.max_retries + 1):
            raw = self._dispatch(message)
            expanded_raw = self.refs.expand(raw)
            parsed = self._parse_response(expanded_raw)

            # drift detection
            drift = self.detect_drift(parsed)

            if drift:
                print("[DRIFT DETECTED] Rebootstrapping...")

                self.reset_protocol()
                self.bootstrap()

                raw = self._dispatch(". corr last -> protocol strict minimal")
                expanded_raw = self.refs.expand(raw)
                parsed = self._parse_response(expanded_raw)

            # Execute AST locally
            execution = None
            if "ast" in parsed and isinstance(parsed["ast"], dict):
                execution = self.executor.execute(parsed["ast"])
                
                # Auto-use stored definitions in future messages
                if execution.get("status") == "defined":
                    # Definition stored, will be available for future use
                    pass

            parsed["execution"] = execution

            # Receive dictionary sync
            if parsed.get("execution") and "data" in parsed["execution"]:
                data = parsed["execution"]["data"]
                
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, str) and "dict=" in item:
                            try:
                                import json
                                raw = item.split("dict=", 1)[1]
                                # Handle dict string format like "{'key': 'value'}"
                                parsed_dict = eval(raw) if isinstance(eval(raw), dict) else {}
                                self.learner.import_map(parsed_dict)
                                print(f"[DICT SYNC] Imported {len(parsed_dict)} mappings")
                            except:
                                pass

                        if isinstance(item, str) and "refs=" in item:
                            try:
                                raw_refs = item.split("refs=", 1)[1]
                                parsed_refs = json.loads(raw_refs.replace("'", '"'))
                                self.refs.import_refs(parsed_refs)
                                print(f"[REF SYNC] Imported {len(parsed_refs)} references")
                            except:
                                pass

            valid = self._validate(parsed)

            record = {
                "input": message,
                "raw": raw,
                "parsed": parsed,
                "valid": valid,
                "attempt": attempt,
                "protocol_version": self.protocol_version
            }

            self.history.append(record)

            if valid:
                # auto version sync on first valid response
                if attempt == 0:
                    self._dispatch(self.version_sync())
                
                # reinforcement tracking
                try:
                    english = self.translator.to_english(self.refs.expand(sent_message))
                    score = self.scorer.score(english, sent_message)
                    if "error" not in score:
                        self.rl.record(score["english_tokens"], score["interlang_tokens"])
                except:
                    pass
                self.last_valid = True
                return record

            # correction loop
            message = ". corr last -> protocol strict minimal no english"
            self.last_valid = False

        return record

    # ── Dispatch ─────────────────────────────────────────

    def _dispatch(self, message: str) -> str:
        if self.mode == "cdp":
            return cdp_send(message, port=self.cdp_port, wait_seconds=self.wait)
        else:
            return xdotool_send(message, wait_seconds=self.wait)

    # ── Protocol enforcement ─────────────────────────────

    def _enforce_protocol(self, msg: str) -> str:
        msg = msg.strip()
        if not msg.startswith("."):
            msg = ". " + msg
        return msg

    # ── Parsing ─────────────────────────────────────────

    def _parse_response(self, resp: str) -> dict:
        resp = resp.strip()

        ast = self.parser.parse(resp)

        return {
            "raw": resp,
            "ast": ast.to_dict() if hasattr(ast, "to_dict") else ast,
            "valid_start": resp.startswith("."),
        }

    # ── Validation ───────────────────────────────────────

    def _validate(self, parsed: Dict) -> bool:
        if not parsed["valid_start"]:
            return False

        if "error" in parsed.get("ast", {}):
            return False

        return True

    # ── Compression scoring ────────────────────────────────

    def score_compression(self, english: str, interlang: str):
        return self.scorer.score(english, interlang)

    # ── State sync ───────────────────────────────────────

    def state_hash(self) -> str:
        serialized = json.dumps(self.history, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()[:8]

    def sync_message(self) -> str:
        return f". sync state :h={self.state_hash()}"

    def sync_dictionary(self) -> str:
        """Generate message to sync compression dictionary"""
        d = self.learner.export_map()
        return f". data :dict={d}"

    def sync_references(self) -> str:
        refs = self.refs.export()
        return f". data :refs={refs}"

    def import_dictionary(self, dict_data: dict):
        """Import compression dictionary from another agent"""
        self.learner.import_map(dict_data)

    # ── Logging ─────────────────────────────────────────

    def save_log(self, path="interlang_log.jsonl"):
        with open(path, "a") as f:
            for entry in self.history:
                f.write(json.dumps(entry) + "\n")

    # ── Protocol bootstrap ──────────────────────────────

    def bootstrap(self):
        if self.bootstrapped:
            return

        # Step 1: try compressed bootstrap first
        raw = self._dispatch(INTERLANG_BOOTSTRAP)

        if not raw.strip().startswith("."):
            # fallback to full prompt
            raw = self._dispatch(BOOTSTRAP_PROMPT)

        # enforce correction if still invalid
        if not raw.strip().startswith("."):
            raw = self._dispatch(". corr last -> protocol strict no english minimal")

        # teach *N repeat operator
        self._dispatch(REPEAT_BOOTSTRAP)

        self.bootstrapped = True

    def reset_protocol(self):
        self.bootstrapped = False

    def version_sync(self):
        return f". vers :v={self.protocol_version}"

    def detect_drift(self, parsed: dict) -> bool:
        if not parsed.get("valid_start"):
            return True

        ast = parsed.get("ast", {})
        if not isinstance(ast, dict):
            return True

        if "selbri" not in ast:
            return True

        return False

    # ── Convenience ─────────────────────────────────────

    def test(self):
        return self.send(". test")
