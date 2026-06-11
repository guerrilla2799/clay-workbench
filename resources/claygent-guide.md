# Claygent Guide — AI Research Agent Columns

Claygent is Clay's AI research agent — it crawls public sources and returns structured outputs. Used as a column in any Clay table.

This guide covers the production-ready patterns for using Claygent without burning credits or producing hallucinated outputs.

⚠️ Action key is `"use-ai"`, NOT `"ai"`. The `"ai"` key silently drops inputs.

---

## Anatomy of a Good Claygent Column

| Setting | Recommendation |
|---------|----------------|
| Action key | `use-ai` (always) |
| Model | Claude Sonnet (default), Haiku for cheap classification, Opus avoid for scale |
| max_sources | 1 = simple, 3 = standard, 5 = deep research, 10 = avoid |
| Prompt | 5-part architecture (ROLE / CONTEXT / TASK / FORMAT / FALLBACK) |
| Run Condition | Always gated by ICP / Sending Gate (Rule #1) |
| Output column type | Match the FORMAT (text for sentence, JSON for structured) |
| Variable substitution | Use exact column names in `{curly_braces}` |

---

## When to Use Claygent (vs Other Tools)

✅ **Good fit**:
- Researching pain points or strategic priorities from a website
- Classifying trigger events as actionable vs noise
- Generating personalized first lines or subject lines
- Interpreting unstructured use-case text from form fills
- Summarizing recent news / press releases tied to an account

❌ **Bad fit**:
- Email/phone discovery (use waterfalls — deterministic and cheaper)
- Industry / firmographic standardization (use Clay native enrichment)
- Title → seniority classification (use Clayscript formula)
- Domain → company name (use `find-company` enrichment)

Rule: if the answer is deterministic, don't use Claygent. Save for AI judgment.

---

## Cost Profile

| Use Case | max_sources | Typical Credits per Run |
|----------|-------------|-------------------------|
| Single-source classification | 1 | 2 |
| Standard 1-paragraph research | 3 | 5 |
| Multi-source summarization | 5 | 8 |
| Deep account brief | 5 | 12 |
| First-line generation (no crawl, just composition) | 0–1 | 2–3 |

Cost scales with sources crawled. Cap aggressively.

---

## Production Recipes

### Recipe 1 — Pain Point Research

**Goal**: 1 sentence operational pain mapped to your value categories.

**Settings**:
- max_sources: 3
- Run Condition: `icp_gate_qualified = TRUE`
- Output: JSON

**Prompt**: See `ai-prompt-templates.md` Template 1.

**Sample Output Shape**:
```json
{
  "pain": "Scaling AI infra costs without observability into per-tenant burn rates.",
  "evidence_url": "https://company.com/blog/2026/scaling-ai",
  "category": "finance",
  "confidence": "high"
}
```

### Recipe 2 — Personalized First Line

**Goal**: One peer-tone email opener.

**Settings**:
- max_sources: 2 (LinkedIn + company website)
- Run Condition: `sending_gate_eligible = TRUE`
- Output: text

**Prompt**: See `ai-prompt-templates.md` Template 2.

**Common Failure Mode**: Generic openers ("I came across {company_name}...").

**Fix**: Add explicit banned-words list inside the prompt. Iterate until 5/5 read-aloud pass.

### Recipe 3 — Trigger Event Classifier

**Goal**: Filter raw trigger feed to only actionable triggers.

**Settings**:
- max_sources: 1 (the trigger source URL)
- Run Condition: `trigger_event_raw IS NOT NULL`
- Output: JSON {classification, reason}

**Prompt**: See Template 5.

**Why valuable**: Predictleads + Champify return noisy triggers. Filtering with Claygent cuts SDR alert noise 40-60%.

### Recipe 4 — Inbound Use-Case Interpretation

**Goal**: Turn a free-text use case into an SDR-ready brief.

**Settings**:
- max_sources: 0 (no crawl — pure interpretation)
- Run Condition: `route_to = "SDR_QUEUE"`
- Output: text (single sentence)

**Prompt**: See Template 4.

**Note**: `max_sources: 0` means Claygent doesn't crawl — it just composes from CONTEXT. Cheapest mode.

### Recipe 5 — Sales Nav Search Builder

**Goal**: Generate Sales Nav search queries from a persona definition.

**Settings**:
- max_sources: 0
- Run Condition: persona definition required
- Output: JSON (keywords, filters)

**Prompt**: See Template 8.

**Why**: SDRs spend 10+ min per ICP refining Sales Nav. This compresses to seconds.

---

## Source Crawling Best Practices

### Be Specific About Sources

❌ Bad: "Check the company's online presence."
✅ Good: "Check (max 3): /about, /careers, recent press release at {url}."

### Cap max_sources Strictly

| max_sources | Use Case | Risk if Higher |
|-------------|----------|----------------|
| 0 | Pure composition | None |
| 1-2 | Classification, single-source research | Acceptable |
| 3 | Standard research | Cost creep |
| 5 | Deep brief | Cost balloon (10+ credits/row) |
| 10+ | Avoid | Drains credits, low ROI marginal sources |

### Prefer Specific URLs

When you have URLs from upstream columns (LinkedIn URL, company URL, trigger source URL), pass them explicitly:

```
SOURCES TO CHECK:
1. {linkedin_url}
2. {company_url}/about
3. {trigger_event_url}
```

Better than: "Crawl the web for this company."

---

## Variable Substitution Rules

### Use Exact Column Names

✅ `{first_name}` (matches column "first_name")
❌ `{firstName}` if column is named "first_name"

### Handle Missing Values in FALLBACK

```
FALLBACK:
If {trigger_event} is empty, use {industry} as alternative angle.
If both empty, return "[no signal available]" — this triggers downstream gate.
```

### Nested JSON References

If a previous Claygent column returned JSON, reference fields with dot notation:

```
TASK: Use {personalization_source.observation} as the lead.
```

---

## Common Pitfalls

### Pitfall 1: Empty Prompt Silently Ships
**Symptom**: All AI columns return blank.
**Cause**: Action key is `"ai"` not `"use-ai"`, OR prompt template variable substitution failed and produced empty prompt.
**Fix**: Verify action key. Add a `verify()` step that checks prompt length > 0.

### Pitfall 2: Claygent Hallucinates When Sources Are Missing
**Symptom**: AI returns plausible-but-false output.
**Cause**: max_sources crawled returned nothing, AI composes from priors.
**Fix**: FALLBACK section that returns sentinel value when no sources found.

### Pitfall 3: JSON Output Parsing Fails Downstream
**Symptom**: Downstream formula returns null.
**Cause**: AI returned valid JSON but with different field names than expected.
**Fix**: Specify EXACT JSON structure in FORMAT. Show shape with quotes around field names. Add 1-shot example for novel structures.

### Pitfall 4: Cost Explosion
**Symptom**: 1000-row run costs 15,000+ credits in Claygent alone.
**Cause**: max_sources too high, prompt encourages over-crawl.
**Fix**: Cap max_sources, simplify TASK, use formulas where deterministic.

### Pitfall 5: Vendor-Tone Output
**Symptom**: Generated copy sounds like marketing brochure.
**Cause**: ROLE doesn't specify peer-tone, no banned-words list.
**Fix**: Explicit ROLE ("peer-to-peer GTM operator"), explicit banned words.

---

## Iteration Protocol

For any new Claygent column, follow this iteration:

```
Pass 1 — 5 sample rows
  - Inspect every output by hand
  - Adjust prompt for any failure mode
Pass 2 — 25 rows
  - Spot-check 10 rows
  - Look for systematic issues (vendor tone, off-format, hallucination)
  - Iterate prompt again
Pass 3 — 100 rows
  - Final calibration
  - Lock prompt
Pass 4 — Full run
```

Production-quality Claygent columns have gone through 3+ iteration cycles. New columns that haven't been iterated are a Reliability Risk — don't push to sequencer until iterated.

---

## When Claygent ISN'T the Right Tool

| Symptom | Replace Claygent With |
|---------|----------------------|
| Need deterministic mapping | Formula or lookup column |
| Need verified data (email, phone, firmographic) | Native enrichment / waterfall |
| Need standardized industry/department | Lookup table |
| Need rule-based classification (rules well-defined) | Formula with nested IFs |
| Need real-time data feed | Webhook + native sync |
| Need 100% consistent output | Templated formula with slot-fills |

Claygent is for: judgment, summarization, generation. Not for: lookups, validation, classification with deterministic rules.

---

## Model Selection Cheat Sheet

| Model | Use Case | Cost Multiplier vs Sonnet |
|-------|----------|---------------------------|
| Haiku | Single-input classification, simple labels | 0.3x |
| Sonnet | Standard research, copy generation | 1x (default) |
| Opus | Avoid for column-scale runs | 3-5x |

Default to Sonnet. Switch to Haiku only for high-volume classification with clear rules. Switch to Opus only for one-off ultra-high-stakes runs (rare).
