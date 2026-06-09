# Candidate Topic Score — Methodology

## Overview

Each candidate receives a score (0–100) for every topic (e.g., Y01, D03).
The score is computed from AI-assessed statements, weighted by their centrality to the topic.

---

## Building Blocks

### 1. Statement–Topic Mapping (fixed, candidate-independent)

Each topic is defined by a set of statements. Every statement carries a `statement_weight` that expresses how central it is to the topic:

| Role | Weight |
|---|---|
| core | 1.0 |
| supporting | 0.75 |
| contextual | 0.5 |

This is a fixed property of the **topic model** — it does not change per candidate.

### 2. Candidate–Statement Assessment (from AI)

For each candidate × statement, the AI provides:
- `value` — the candidate's relationship to the statement:
  - **deot axis**: `supports` / `mixed` / `unknown` / `opposes`
  - **yecholot & tadmit axes**: `supports` / `mixed` / `unknown` (no opposes — capabilities and image are not actively contradicted)
- `confidence` — AI certainty in its assessment (0–100)

Value is converted to a numeric score:

| Value | Raw score |
|---|---|
| supports | 100 |
| mixed | 50 |
| opposes (deot only) | 0 |
| unknown | see below |

---

## Scoring Formula

### Statement score
```
statement_score = raw_score × (confidence / 100)
```

Confidence scales the **value** only — not the statement weight.
Rationale: `statement_weight` is a property of the topic model and should not be distorted by the AI's certainty about a specific candidate.

### Candidate score for a topic
```
topic_score = Σ(statement_score × statement_weight)
              ──────────────────────────────────────
                       Σ(statement_weight)
```

A weighted average, normalized to 0–100.

---

## Handling Unknown Values

Unknown statements must be resolved before the topic score is finalized — otherwise candidates with less AI coverage would be scored on a smaller sample, creating an unfair and inconsistent comparison.

**Three options (voter's choice):**

| Option | Unknown treated as | Rationale |
|---|---|---|
| Neutral | 50 (midpoint) | No judgment — treat missing as average |
| Benefit of the doubt | Candidate's own average on known statements in this topic | Missing ≠ absent |
| Class average (default) | Average score of all candidates on this specific statement | Missing coverage is meaningful signal; calibrates against the field |

**Default: Class average (Option 3)**
If all other candidates score 70 on `cap_003`, a candidate with no data on that statement receives 70 — or slightly below, if penalization is desired. This treats missing information as a relative signal, not a neutral one.

---

## Summary Pipeline

```
statement_weight  (topic model, fixed)
       ×
statement_score   (value × confidence/100, per candidate)
       ↓
topic_score       (weighted average, 0–100)
```

---

## Voter Preferences — Aggregation to Final Score

Topic scores are computed independently of the voter. Voter preferences enter only at the aggregation stage, as star ratings (1–5).

### Rules
- A topic with **0 stars** is excluded entirely from the calculation.
- Both aggregation steps use the same formula: a normalized weighted average.

### Step 1 — Topic → Axis score
```
axis_score(candidate, axis) = Σ(topic_score × voter_stars(topic))
                               ────────────────────────────────────
                                      Σ(voter_stars(topic))
```
Summed over all topics within the axis that have stars > 0.

### Step 2 — Axis → Final score
```
final_score(candidate) = Σ(axis_score × voter_stars(axis))
                          ──────────────────────────────────
                                 Σ(voter_stars(axis))
```
Summed over all axes that have stars > 0.

### Full pipeline
```
statement_score   (value × confidence/100)
      × statement_weight                      [topic model layer]
      ↓
topic_score       (0–100)
      × voter_stars(topic)                    [voter preference layer 1]
      ↓
axis_score        (0–100)
      × voter_stars(axis)                     [voter preference layer 2]
      ↓
final_score       (0–100)
```
