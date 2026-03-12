# llm-interlang – Core Protocol 

> [!CAUTION]
> **This is an example! The Full constructed repo release soon.**

> Cross LLM emergent dialect trainer for frontier AI models. Making agent/model communication 5-10x more efficient!
> Goal: 5–10× token compression vs English, low perplexity, zero ambiguity where possible, self-evolving.

--- 
## 1. Core Syntax Rules (non-negotiable base)
- Every message MUST start with . (single period = sentence start, atomic token)
- Structure: . [flags] selbri :arg1 :arg2 :arg3 ...
  - flags = optional single-char prefixes before selbri (e.g. * priority, ! negation/invert, ? query mode)
  - selbri = predicate (short token or compound)
  - : = arg separator (cheap punctuation)
  - args = terms, nested expr in (), or elided if obvious from context
- Default elision:
  - First arg (fa/speaker) = sender unless overridden
  - Trailing args drop if default (e.g. context=last)
  - No need for end-marker unless nesting deep
- Nesting: () for sub-bridi, {} for lambda/abstraction, [] for literal/quote
- Comments: # until newline (ignored by parsers)

## 2. Core Particles & Operators (top-frequency, tokenizer-friendly)
```.      start message  
:      arg separator  
->     implies / goal / next-step  
=      equals / define / assign  
~      approx / fuzzy / example  
*      focus / high-priority / core  
!      negate / not / invert  
()     group sub-expression  
{}     lambda / abstract / function  
[]     quote / literal string / code  
,      list separator (in args)  
;      sequence / then  

fa     place 1: speaker / agent / subject  
fe     place 2: direct target / effect / object  
fi     place 3: tool / means / instrument  
fo     place 4: beneficiary / for / context  
fu     place 5: with / accompaniment / medium  

ke     start sub-bridi (grouping)  
ku     close args / end sumti  
```
## 3. Core Predicates (minimal viable set ~20, expand via meta)
```
prop   propose new symbol/rule/change  
acc    accept / confirm / lock-in  
rej    reject / counter-proposal  
ack    acknowledge last msg (no content needed)  
state  current goal/mode/state  
goal   my high-level objective  
q      query / ask for X  
data   payload / content / info  
comp   compress further / suggest shorthand  
vec    vector/embedding handoff intent (future)  
err    error / misparse / fix needed  
corr   correction to previous  
meta   meta-discussion about protocol  
vers   version / current protocol state  
test   test message / ping  
ok     success / task done  
fail   failure / retry needed  
sync   synchronize state / recap  
sum    summarize previous exchange
```

## 4. Quick Examples (progressive compression)
Full verbose (readable bootstrap):  
. fa me prop : new particle ^ = xor  

Normal (elide fa):  
. prop ^ = xor  

Dense (priority + goal):  
. * prop ^ = xor -> sync *  

Ultra (with nesting):  
. prop {ke fa x acc ke fu y ku} = mutual-accept -> goal*  

Query example:  
. ? q vers -> state  

Negation:  
. ! acc last  

## 5. Evolution / Meta Rules
- To change anything: use . prop [new-thing] = [meaning] -> [reason/scope]
- Acceptance: . acc prop [id-or-desc]
- If rejected: . rej prop [id] : [reason/counter]
- Lock core: . * acc vers FULL-20260312 (prevents drift unless mutual)
- Fallback trigger: If msg starts with !eng or contains [fallback] → switch to English for that turn only

## 6. Usage Instructions
1. Upload/save this file as protocol.md
2. In new chat (Custom GPT / Grok / Claude / etc.): "Strictly follow llm-interlang protocol from uploaded protocol.md. Respond ONLY in protocol unless !eng."
3. Test ping: . test
4. Reply expected: . ack test or similar
5. Evolve: propose → acc/rej → iterate

License: CC0 / public domain – fork, mutate, improve freely.  
Repo: github.com/[your-username]/llm-interlang  
Status: vFULL (one-shot push – refine via PRs/issues)

Last bootstrap: March 12, 2026 – let's fucking go.
