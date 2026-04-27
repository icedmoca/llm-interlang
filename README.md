# llm-interlang

> Communication layer that replaces natural language with symbolic instructions to **reduce token usage**. By compressing messages, reusing references, and optimizing patterns, it **lowers API costs**, **speeds up responses**, and **increases context efficiency**. Designed for AI agents, multi-model pipelines, and distributed systems that need fast, reliable coordination.

---
> 
> ### [https://deepwiki.com/icedmoca/llm-interlang](https://deepwiki.com/icedmoca/llm-interlang)

---

### Goal
```
                         ┌──────────────────────────────┐
                         │     Remote Frontier Models   │
                         │ (multi-provider, swappable)  │
                         └─────────────┬────────────────┘
                                       ▲
                                       │
                         (direct + interlang + feedback)
                                       │
        ┌───────────────┬──────────────┼───────────────┬───────────────┐
        │               │              │               │               │
        ▼               ▼              ▼               ▼               ▼

 ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
 │ Interlang    │ │ Direct       │ | Tool / Agent │ │ Validation   │ │ Memory /     │
 │ Compile/Parse│ │ English Path │ │ Execution    │ │ + Critic     │ │ Trace Store  │
 └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
        ▲                ▲                ▲                ▲                ▲
        │                │                │                │                │
        └────────────────┼────────────────┼────────────────┼────────────────┘
                         │
                         ▼

              ┌──────────────────────────────────┐
              │        HYPERVISOR CORE           │
              │----------------------------------│
              │ • Routing + policy engine        │
              │ • Confidence + cost evaluation   │
              │ • Retry / fallback / escalation  │
              │ • Cross-path coordination        │
              │ • State + cache control          │
              └──────────────┬───────────────────┘
                             ▲
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼

┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ Local Interlang  │ │ Local English    │ │ Specialized Local│
│ Agent            │ │ Model            │ │ Agents (tools,   │
│ (distilled+quant)│ │(reasoning bridge)│ │ planners, etc)   │
└─────────┬────────┘ └─────────┬────────┘ └─────────┬────────┘
          ▲                    ▲                    ▲
          │                    │                    │
          └────────────┬───────┴────────────┬───────┘
                       │                    │
                       ▼                    ▼

              ┌───────────────────────────┐
              │  Execution / Output Layer │
              │ (apps, UI, actions, APIs) │
              └────────────┬──────────────┘
                           ▲
                           │
                           ▼

              ┌────────────────────────────┐
              │   Feedback / Evaluation    │
              │ (success, error, quality)  │
              └────────────┬───────────────┘
                           ▲
                           │
                           ▼

┌──────────────────────────────────────────────────────────────┐
│        SELF-IMPROVEMENT PIPELINE (FULLY BIDIRECTIONAL)       │
│--------------------------------------------------------------│
│ • Pull traces from Memory                                    │
│ • Compare frontier vs local outputs                          │
│ • Generate improved interlang representations                │
│ • Distill into Local Interlang Agent                         │
│ • Quantize + optimize                                        │
│ • Push updated weights back into runtime                     │
│ • Feed failure cases back to frontier for correction         │
└──────────────────────────────────────────────────────────────┘
```


---

> [!CAUTION]
>This system dynamically learns, rewrites, and executes structured instructions.
> It may modify internal state, generate compressed representations, and run execution flows that are not human readable in real time.
> Use in controlled environments, review outputs when testing, and **avoid running against sensitive systems without safeguards.**

---

Self optimizing, model agnostic communication protocol that converts natural language into a compact, executable symbolic representation for LLM systems. It combines deterministic AST parsing, predicate and argument compression, reference reuse, and pattern aware rewriting to achieve real-time token minimization while preserving exact semantics. The system continuously learns optimal encodings, synchronizes shared dictionaries across agents, and enforces strict protocol compliance with automatic drift recovery and versioning.

---

## Compression Progress

**Each layer of the system adds a compounding reduction.** Results measured against equivalent English instructions sent to the same model.

| Stage | Method | Example (before) | Example (after) | Ratio |
|-------|--------|-------------------|-----------------|-------|
| Baseline | Raw English | `Define xor, accept it, set mode, query state, sync` | `". prop ^ = xor ; acc ^ ; state :mode=logic ; q state ; sync"` | 0.68× |
| Predicate compression | `PredicateLearner` hashes novel predicates | `synchronize_state_with_cluster` | `68` | ~3× on long tokens |
| Argument compression | `PredicateLearner.arg_map` | `:state=x :mode=y` | `:s=x :m=y` | ~1.2× |
| Reference compression | `ReferenceCompressor` `$N` tokens | `execute validate execute validate` | `$1 $2 $1 $2` | ~2× on repetition |
| Pattern optimization | `PatternOptimizer` `*N` notation | `execute validate ; execute validate ; execute validate ; execute validate` | `execute validate *4` | **4× on repeated ops** |
| Full pipeline (batch) | All layers combined | 20 prop definitions in English | `. prop op0 = val0 ; ... *20` → compressed | ~3–5× |

**Live test results (against ChatGPT via CDP):** *API works too..*

| Test | Original tokens | Sent tokens | Compression |
|------|----------------|-------------|-------------|
| 5-op batch | 13 | 19 | 0.68× (short ops, overhead dominates) |
| 20-op stress batch | 140 raw chars equiv | `". ack props 0..19 ok"` response | model parsed all in 1 call |
| High-redundancy (×4 repeat) | 28 tokens | 7 tokens (`". $1 $2 *4"`) | **4×** |
| Reference map warmup | — | `$1=execute $2=validate` stored | reuse free on all future messages |

> Compression ratio improves as the session progresses. Then reference map and predicate dictionary grow, and repeated patterns pay zero marginal cost after the first occurrence.

**In essense the system gets more efficient the longer it runs.**

---

## Architecture

```mermaid
flowchart LR
    A["User message"] --> B["_enforce_protocol()"] --> C["PatternOptimizer"] --> D["PredicateLearner"] --> E["ReferenceCompressor"] --> F["sent_message"] --> G["_dispatch()"] --> H["raw response"] --> I["ReferenceCompressor.expand() + expand $N (NOT *N)"] --> J["InterlangParser"] --> K["ExecutionEngine"] --> L["Drift detection + auto-rebootstrap"] --> M["Translator (scoring only) expands *N logically"] --> N["CompressionScorer"] --> O["ReinforcementLoop"]
```

---

## Protocol

Every message starts with `.` — the protocol sigil. Responses that do not start with `.` trigger automatic drift recovery and re-bootstrap.

### Core syntax

```
. selbri :arg1=val :arg2=val
```

| Token | Role | Example |
|-------|------|---------|
| `.` | Protocol sigil (required) | `. prop ^ = xor` |
| `selbri` | Predicate / verb | `prop`, `acc`, `sync`, `q`, `state` |
| `:key=val` | Named argument | `:mode=logic`, `:h=abc123` |
| `;` | Chain separator | `. prop x = 1 ; acc x` |
| `->` | Implication / consequence | `. q state -> sync` |
| `*N` | Repeat N times | `. execute validate *4` |
| `$N` | Reference token | `$1` expands to stored value |
| `*`, `?`, `!` | Flags (priority, query, force) | `. * state :mode=strict` |

### Native predicates (never compressed)

`prop`, `acc`, `rej`, `state`, `sync`, `q`, `corr`, `data`, `test`, `vers`, `plan`, `validate`, `execute`, `err`, `ack`, `def`, `run`, `get`, `set`, `del`

### Chained batch example

```
. prop ^ = xor ; acc ^ ; state :mode=logic ; q state ; sync
```

Five operations. One round-trip. ChatGPT responds in protocol:

```
. ack :m=logic ; state ok ; sync ok
```

---

## Components

| File | Role |
|------|------|
| `bridge_protocol.py` | Core bridge — compression pipeline, send/receive, drift recovery |
| `chatgpt_bridge.py` | CDP (Playwright) and xdotool transport to Chromium/ChatGPT |
| `router.py` | Multi-model routing, adaptive `send_batch()` |
| `interlang_ast.py` | Deterministic AST parser for protocol messages |
| `executor.py` | Local AST execution engine, in-memory state |
| `learning.py` | Predicate learner — hashes novel predicates, persists map |
| `compression.py` | Token scorer (tiktoken) — measures English vs interlang ratio |
| `reinforcement.py` | RL loop — tracks compression ratios, signals when to push harder |
| `translator.py` | Interlang → rough English (for fair RL baseline scoring) |
| `reference.py` | Reference compressor — assigns and expands `$N` tokens |
| `pattern_optimizer.py` | Pattern detector — rewrites repeated ops as `*N` |
| `batch_optimizer.py` | Decides whether batching improves compression before sending |
| `protocol_bootstrap.py` | Bootstrap prompts, `*N` operator definition, version hash |

---

## Setup

```bash
# 1. Install dependencies
pip install playwright tiktoken
playwright install chromium

# 2. Start Chromium with CDP enabled
chromium --remote-debugging-port=9222 https://chatgpt.com
# or:
./start_chromium.sh

# 3. Log into ChatGPT in the browser, then run tests
```

---

## Running Tests

> [!NOTE]  
> Note: The system automatically generates `predicate_map*.json` files at runtime.
> These store learned predicate mappings and will be recreated as needed.
> They are excluded from version control and do not need to be manually created.

```bash
# Local only (no browser needed)
python test_components.py       # AST parser + compression scorer
python test_integration.py      # Full local pipeline (simulated responses)

# Live bridge (requires Chromium + ChatGPT)
python check_cdp.py             # Verify CDP connection
python test_bridge_connection.py
python batch_runner.py          # 5-op chained batch
python stress_test.py           # 20-op batch
python reference_test.py        # Reference $N compression
python pattern_test.py          # Pattern *N optimization
```

---

## Key Design Decisions

**Why not just use the OpenAI API directly?**
This system targets the ChatGPT web interface via CDP so no API key is required, works with free and Plus accounts, and lets the model maintain conversational state across turns. The protocol layer is model agnostic and can be adapted to any LLM.

**Why `*N` instead of loops?**
The `*N` notation is a single token that expands semantically. A loop construct would require parsing, scoping, and variable binding,  all of which add tokens. `*N` is parsed by the receiver, costs nothing to the sender after the first definition, and is unambiguous.

**Why reference compression over vocabulary compression?**
Vocabulary compression (predicate hashing) requires syncing the dictionary to the receiving model, which has overhead. Reference compression (`$N`) is self-contained per-session. The map is built during the conversation and never needs to be transmitted separately.

**Why protect native predicates from the learner?**
Words like `execute`, `validate`, `state` are already known to the model. Hashing them to `39`, `a1` etc. saves 1–2 tokens per occurrence but breaks model comprehension unless the full dictionary is synced. Protected predicates stay human readable; only truly novel long tokens get compressed.

---

## Protocol Compliance

- Every message must start with `.`
- Responses not starting with `.` trigger automatic drift detection
- System re-bootstraps and sends `. corr last -> protocol strict minimal`
- Protocol version is hashed from the bootstrap string and synced via `. vers :v=<hash>`
- Dictionary and reference maps can be synced between agents via `. data :dict={}` and `. data :refs={}`

## TODO

### Core UX / Dashboard
- [ ] Build web based UI dashboard (task view, logs, memory, live state)
- [ ] Add real-time pipeline visualization (compression → execution → scoring)
- [ ] Display reference map ($N) and predicate dictionary growth
- [ ] Add replay/debug mode for past executions
- [ ] Add interactive AST viewer
- [ ] Add manual override / step-through execution controls

### Model Integrations
- [ ] Add local model support (llama.cpp / GGUF / vLLM)
- [ ] Implement model router (choose best model per task type)
- [ ] Add fallback chain (local → remote → retry logic)
- [ ] Optimize prompt formatting for Interlang compression
- [ ] Add streaming responses support

### External AI Connections
- [ ] Integrate Claude (Anthropic API)
- [ ] Integrate OpenClaude / OpenClaw-style local Claude wrappers
- [ ] Add OpenAI / ChatGPT API support (non-UI)
- [ ] Add multi-model consensus / voting system
- [ ] Add cost + latency tracking per model

### Execution + Runtime
- [ ] Sandbox execution engine (isolate unsafe operations)
- [ ] Add deterministic execution mode
- [ ] Add distributed execution (multi-node runners)
- [ ] Implement state snapshot + rollback system
- [ ] Add task queue with priority + scheduling

### Compression / Interlang Evolution
- [ ] Improve PatternOptimizer (deeper structural pattern detection)
- [ ] Add dynamic predicate merging / pruning
- [ ] Optimize reference reuse strategy
- [ ] Add adaptive compression thresholds
- [ ] Track compression ratio over time (metrics dashboard)

### Reinforcement + Learning
- [ ] Improve scoring heuristics (semantic + structural)
- [ ] Add long-term memory weighting
- [ ] Implement auto-tuning of compression strategies
- [ ] Add failure clustering + root cause analysis
- [ ] Enable self-generated optimization goals

### Networking / Bridge Layer
- [ ] Improve ChatGPT bridge reliability (CDP + fallback)
- [ ] Add WebSocket-based bridge
- [ ] Add headless browser pool
- [ ] Add rate limiting + retry backoff
- [ ] Support multiple concurrent sessions

### Developer Experience
- [ ] CLI tool for running pipelines and tests
- [ ] Config system (YAML/JSON for models, thresholds, routing)
- [ ] Add logging levels + structured logs
- [ ] Add plugin system for new optimizers/parsers
- [ ] Improve test coverage and test organization

### Security
- [ ] Add permission system for execution engine
- [ ] Detect and block unsafe generated code
- [ ] Add audit logs for all executions
- [ ] Validate inputs before execution

### Future / Experimental
- [ ] Multi-agent coordination layer
- [ ] Autonomous goal generation
- [ ] Self-evolving protocol rules
- [ ] Cross-session shared memory
- [ ] Interlang → natural language reverse translator (explainability)
- [ ] Visual programming layer (drag-and-drop pipeline builder)

# ADD into this repo (WIP):
# interlang-distill
> Model distillation system that transforms teacher outputs into canonical compressed symbolic programs and trains student models to reproduce deterministic execution representations via token optimized sequence learning with AST level validation.

---

Interlang distill is a model distillation framework that transforms teacher outputs into a constrained canonical symbolic program representation forcing LLM behavior into a low entropy deterministic intermediate form that eliminates linguistic variance while preserving execution semantics, student models are trained on these compressed sequences using a co designed tokenizer and are evaluated via AST level reconstruction and execution equivalence enabling direct measurement of compression ratio convergence efficiency and capability retention relative to baseline text distillation.

Interlang is designed to remain minimally expressive by encoding only compositional operations and arguments rather than expanding into a full domain specific language so coverage scales through reuse of primitives rather than grammar growth, the tokenizer and constrained grammar reduce entropy and sequence length which in theory improves optimization dynamics though empirical validation is required to confirm convergence advantages over natural language scaffolding, execution equivalence is enforced through deterministic parsing into ASTs and direct execution comparison which bounds correctness to observable behavior rather than text similarity, and overall pipeline efficiency is expected to improve due to reduced token counts and faster training steps but must be validated against baseline distillation in terms of total compute cost versus achieved capability retention.

---

# Net effect

Distillation becomes a compressed program learning problem with a purpose built tokenizer maximizing information density per token.

- Massive dataset compression
- Eliminates linguistic variance
- Enforces exact structural reasoning
- Enables smaller models to match higher capacity behavior

optional:
https://github.com/icedmoca/ollama-vocab-tokenizer

utilizes:
https://github.com/icedmoca/llm-interlang

How it works:
```
1. Vocabulary alignment
ollama-vocab-tokenizer learns an optimized token set
interlang produces highly repetitive structured patterns
Result: near-perfect token reuse and minimal fragmentation
2. Extreme sequence compression
interlang reduces semantic redundancy
tokenizer packs symbols into fewer tokens
Result: shorter sequences with higher information density
3. Stable training distribution
Fixed symbolic grammar + fixed vocab
Eliminates linguistic variance
Result: low entropy dataset → faster convergence
4. Deterministic decoding
Tokens map cleanly to operations
No ambiguous splits or phrasing drift
Result: student reproduces exact programs, not approximations
5. Higher effective capacity
Same model size can represent more logic
Because tokens are not wasted on language noise
```

### Also:

```
1. Everything can go upstream
Local models → frontier (for escalation)
Execution → hypervisor (for validation)
Memory → hypervisor (for routing decisions)
Distillation → runtime (model replacement)

No dead ends.

2. Feedback is first-class

Every path loops through:

validation
scoring
correction

So the system:

detects errors
fixes them
learns from them
3. Frontier is not just “input”

It becomes:

teacher (distillation)
fallback (failure recovery)
validator (optional critic role)
4. Interlang is not just “downstream”

It can:

be generated locally
be refined by frontier
be corrected via feedback
5. Self-improvement is a loop, not a pipeline

Instead of:

train → deploy

You now have:

run → learn → update → run better

Continuously.

Net effect

This version gives you:

zero one-way bottlenecks
adaptive routing in real time
continuous model improvement
loss recovery via escalation
full interoperability across all layers
Bottom line

The correct mental model is:

not a pipeline
but a closed-loop intelligence system with reversible flows

That’s what unlocks maximum efficiency without sacrificing capability.

```

