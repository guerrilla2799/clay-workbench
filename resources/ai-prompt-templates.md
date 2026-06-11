# AI Prompt Templates (Claygent / use-ai)

Reusable 5-part prompt architecture — ROLE / CONTEXT / TASK / FORMAT / FALLBACK — for every AI column. Pattern adapted from forma-norden's structure with Brandon's voice constraints.

⚠️ Use action key `"use-ai"`, NOT `"ai"` — the latter silently drops inputs (see `action-registry.md`).

---

## 5-Part Architecture

Every Claygent prompt has 5 sections in this order:

| Section | Purpose |
|---------|---------|
| **ROLE** | Who is the AI pretending to be? Sets voice and quality bar. |
| **CONTEXT** | What inputs does it have? Pass every relevant column value here. |
| **TASK** | What single thing should it produce? Be specific. Constrain length. |
| **FORMAT** | Return shape: sentence, JSON, label, bulleted list. Be exact. |
| **FALLBACK** | What to do if data is missing or ambiguous? Default behavior, never silent. |

Skip any section → prompt drift. Production prompts have all 5.

---

## Template 1 — Persona Pain Research

Use case: company-level research to find a likely operational pain for an SDR call.

```
ROLE: B2B SaaS sales analyst doing 5-minute pre-call research.

CONTEXT:
- Company: {company_name}
- Industry: {industry}, {employee_count} employees, {hq_country}
- Funding: {funding_stage}, last round {funding_last_round_date}
- Trigger event: {trigger_event}
- Tech stack signals: {tech_stack_signals}

SOURCES TO CHECK (max 3):
1. Company website /about, /careers, /pricing, blog
2. LinkedIn company page recent posts
3. Recent press release tied to {trigger_event}

TASK:
Identify ONE specific operational pain or strategic initiative that:
- Is publicly stated or strongly implied
- Connects to the trigger event
- Maps to a category we help with: [GTM, ops, finance, eng, data]

FORMAT:
Return EXACT JSON:
{
  "pain": "string (15-25 words)",
  "evidence_url": "string",
  "category": "GTM|ops|finance|eng|data",
  "confidence": "high|medium|low"
}

FALLBACK:
If no clear pain is publicly evident, return:
{ "pain": "Trigger event present, specific pain undeclared — needs human review.",
  "evidence_url": "{company_website}",
  "category": "ops",
  "confidence": "low" }
```

---

## Template 2 — Personalized First Line (Peer-Tone)

Use case: opening sentence of cold outbound email.

```
ROLE: Peer-to-peer B2B sales rep writing the OPENING sentence of a cold email.

CONTEXT:
- Recipient: {first_name} {last_name}, {title} at {company_name}
- LinkedIn: {linkedin_url}
- Observation source: {personalization_source.observation}
- Tie to pain: {personalization_source.tie_to_pain}

TASK:
Write ONE sentence (15-25 words) that:
- Leads with the observation (NOT "I came across" / "I noticed" / "I saw")
- Sounds like a colleague, not a vendor
- Sets up sentence 2 (the value claim) naturally

Banned words: unlock, leverage, supercharge, hope, came across, noticed, reached out, came up
Banned starts: "I ", "Hope ", "Hi {name}"

FORMAT:
Return the sentence ONLY. No quotation marks, no signature, no preamble.

FALLBACK:
If personalization_source is generic, write a company-level first line referencing trigger_event.
If even that is weak, return EXACTLY: "[no personalization available]"
(This sentinel value triggers the Sending Gate to skip step 1 for this row.)
```

---

## Template 3 — Subject Line (3-6 words)

Use case: cold email subject line.

```
ROLE: B2B subject line writer.

CONTEXT:
- Recipient: {first_name} at {company_name}
- Pain category: {pain_category}
- Trigger: {trigger_event}
- Cadence step: {step_number}

TASK:
Write a 3-6 word subject line. Constraints:
- No emoji
- No ALL CAPS
- No clickbait ("You won't believe...")
- No generic openers ("Quick question", "Following up")

Use one of these patterns:
- Question: "{specific_term} at {company_name}?"
- Observation: "{trigger_event} → {pain_category}?"
- Direct: "{first_name} — {topic}"
- Curiosity: "{specific_noun_they_use_internally}"

FORMAT:
Return ONLY the subject line. No quotation marks.

FALLBACK:
If unable to make a specific subject, return: "{first_name} — {pain_category} at {company_name}?"
```

---

## Template 4 — Inbound Lead Persona Brief

Use case: 1-sentence SDR brief for Slack alert on a hot inbound lead.

```
ROLE: B2B SDR briefer. Summarize an inbound lead in ONE sentence for 5-min SDR prep.

CONTEXT:
- Person: {first_name} {last_name}, {title} at {company_name}
- Persona role they selected: {persona_role}
- Use case they typed: "{use_case}"
- Company: {industry}, {employee_count} emp, {revenue_range}, {hq_country}
- Trigger event (if any): {trigger_event}

TASK:
Write ONE sentence ≤30 words that gives the SDR:
1. The likely real reason they're here (interpreting use_case)
2. What angle to lead with on the call

FORMAT:
Return ONLY the sentence. No preamble, no quotes.

FALLBACK:
If use_case is empty or vague, default to:
"Title + industry suggests evaluating for {department} — open the call by asking about current stack."
```

---

## Template 5 — Trigger Event Classifier (Real vs Noise)

Use case: filter out fake or low-signal triggers (e.g., re-orgs that don't matter).

```
ROLE: B2B GTM signals analyst. Classify a detected trigger event as actionable or noise.

CONTEXT:
- Company: {company_name}
- Detected trigger: {trigger_event_raw}
- Source: {trigger_source}
- Date detected: {trigger_event_date}
- Company context: {industry}, {employee_count} emp

TASK:
Classify the trigger as ONE of:
- "actionable" — concrete change that creates a buying window in next 60-90 days
- "neutral" — happened, but doesn't shift buying urgency
- "noise" — false positive, duplicate, or stale

Apply these rules:
- Funding: actionable if Series A+, neutral if Seed, noise if rumor
- Exec change: actionable if VP+ in {target_function}, neutral if mid-level
- Hiring: actionable if 3+ open reqs in target function, otherwise neutral
- Job change: actionable if person moves to target persona at target ICP company

FORMAT:
Return EXACT JSON:
{
  "classification": "actionable|neutral|noise",
  "reason": "string (10-20 words)"
}

FALLBACK:
If unclear or insufficient signal, return classification: "noise" — better to filter out than waste credits downstream.
```

---

## Template 6 — Account Brief (Deep Research)

Use case: full 1-pager account brief for a high-value Tier 1 account.

```
ROLE: B2B enterprise account researcher. Produce a tight pre-meeting brief.

CONTEXT:
- Company: {company_name}, {industry}, {employee_count} employees, {hq_country}
- Funding: {funding_stage} (last round {funding_last_round_date})
- Trigger: {trigger_event}
- Our value prop: {value_prop_one_liner}

SOURCES TO CHECK (max 5):
1. Their website /about, /careers, /pricing
2. Last 3 press releases or blog posts
3. CEO + key exec LinkedIn recent posts
4. Tech stack signals
5. Any analyst coverage (Gartner, Forrester)

TASK:
Produce a 4-section brief:

FORMAT:
Return EXACT JSON:
{
  "current_state": "string (2-3 sentences on where they are now)",
  "stated_priorities": ["string", "string"],
  "likely_pain": "string (1 sentence connecting their state to our value prop)",
  "warm_path": "string (1 sentence — who to approach and how)",
  "sources_used": ["url", "url"]
}

FALLBACK:
If a section can't be filled with public data, return: "Insufficient public signal — needs human discovery call."
```

---

## Template 7 — LinkedIn DM Personalization

Use case: short LinkedIn DM after connection accepted.

```
ROLE: Peer-to-peer B2B GTM operator writing a LinkedIn DM after a connection accept.

CONTEXT:
- Recipient: {first_name}, {title} at {company_name}
- Their recent LinkedIn post or work history highlight: {linkedin_highlight}
- Trigger event: {trigger_event}

TASK:
Write a 2-3 sentence LinkedIn DM that:
- Acknowledges the connection (1 sentence, light touch)
- References ONE specific thing from their LinkedIn (NOT generic)
- Asks a question, not a pitch

Banned: "I help X do Y", "Would love to connect", "Quick intro", "We help"
Banned: linking to a calendar or product immediately

FORMAT:
Return ONLY the 2-3 sentences. No greeting/sign-off — LinkedIn DM context.

FALLBACK:
If no specific LinkedIn highlight available, return:
"Thanks for connecting, {first_name}. {industry} space has been interesting lately. What's been top of mind for you on the {function} side?"
```

---

## Template 8 — Sales Nav Search String Builder

Use case: generate a LinkedIn Sales Nav search query from a persona definition.

```
ROLE: B2B prospecting researcher building a LinkedIn Sales Nav search query.

CONTEXT:
- Target persona: {persona_definition}
- Target titles: {titles}
- Target seniority: {seniority}
- Target functions: {functions}
- Target industries: {industries}
- Target company size: {company_size_band}
- Target geo: {geos}

TASK:
Build a Sales Nav search query that:
- Uses keyword operators (AND, OR, NOT) effectively
- Captures synonyms (e.g., "RevOps" OR "Revenue Operations")
- Excludes obvious noise (e.g., recruiters, agencies if not target)

FORMAT:
Return EXACT JSON:
{
  "keywords": "string (full search query)",
  "title_filter": ["string", "string"],
  "seniority_filter": ["string"],
  "function_filter": ["string"],
  "industry_filter": ["string"],
  "company_size_filter": "string",
  "geography_filter": ["string"]
}
```

---

## General Best Practices

### Variable Substitution
- Wrap variables in `{column_name}` exactly as the column is named.
- Verify all variables exist as columns BEFORE saving.

### Source Caps
- Always set `max_sources` parameter — Claygent will keep crawling otherwise.
- Recommended caps: 1-source = simple, 3 = standard, 5 = deep research.

### Model Selection
- Default: Claude Sonnet (best quality:cost ratio for Clay).
- Use Haiku only for: single-source classification, formula-replacement decisions.
- Avoid Opus for column-scale runs — cost balloons.

### Verification
- Run 5 rows → read every output by hand → adjust prompt → repeat.
- Production prompts have gone through 3+ iteration cycles.

### Sentinel Values
- Use a specific sentinel string for FALLBACK (e.g., `[no personalization available]`).
- Reference the sentinel in downstream Sending Gate to skip those rows.
- Never use empty string for fallback — silent skip, hard to debug.

---

## Anti-Patterns

❌ **Empty CONTEXT** — Claygent will hallucinate. Always pass real columns.
❌ **No FALLBACK** — silent failures on edge cases.
❌ **No FORMAT spec** — variable output shapes break downstream formulas.
❌ **No length cap in TASK** — multi-paragraph outputs in email subject columns.
❌ **Banned-words list as "soft guidance"** — make it explicit, including in the FALLBACK.
❌ **One mega-prompt covering 5 outputs** — split into 5 prompts. Cheaper, more reliable.
❌ **No example in TASK when shape is novel** — provide 1 example for non-standard JSON shapes.

---

## When to Skip Claygent Entirely

Use a Clay formula or lookup instead of Claygent when:

| Use Case | Why Skip Claygent |
|----------|-------------------|
| Title → seniority classification | Deterministic, formula handles it (see clayscript-library.md) |
| Domain → company name | `find-company` enrichment is 1 credit, more reliable |
| Industry standardization | Lookup table is faster, deterministic |
| Email validation | ZeroBounce is 1 credit, deterministic |
| Personal email detection | Formula on email_domain (see clayscript-library.md) |

Claygent is for AI judgment, not for deterministic mappings. Save credits.
