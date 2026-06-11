---
name: clay-outbound
description: Generate personalized outbound copy in Clay workbooks — first lines, subject lines, value claims, CTAs — using Claygent and ICP context. Composes Sending Gate, multi-step sequencing, and push to SalesLoft / Outreach / Apollo / 11x / Smartlead / Instantly. Auto-detects client voice (Obin, Vantage, Dodge, etc.) to keep copy on-brand. Triggers — "outbound message", "first line", "personalized email", "Sending Gate", "push to SalesLoft Outreach 11x Smartlead Instantly", "Clay outbound", "ai-sdr", "/clay-outbound".
---

# clay-outbound — Personalized Outbound + Sequencer Push

Composes the AI copy columns, the Sending Gate, and the sequencer push action for outbound motions. Detects client context and routes to client messaging skills for voice.

Inherits master workflow. Specializes step 3 (copy column composition) and step 5 (Sending Gate + sequencer push).

---

## Inputs Expected

From intake:
- **Destination sequencer**: SalesLoft / Outreach / Apollo / 11x / Smartlead / Instantly
- **Sequence/cadence ID**: which sequence in the destination
- **Cadence shape**: # of steps, channels per step (email / LinkedIn / call), days between
- **Copy elements needed**: first line / subject line / value claim / specific objection handler / CTA
- **Voice / client context**: Obin / Vantage / Dodge / generic? (drives messaging skill routing)
- **Personalization depth**: pattern (industry-level) / mid (company-level) / deep (person-level Claygent research)

---

## Step 3 — Composition (Specialized)

### Pre-Composition: Client Voice Routing

Before generating any copy, detect client context per `resources/client-context-detection.md`.

```
1. Scan prompt for client tokens.
2. If matched: load the matching messaging skill (obin-messaging / vantage-messaging / etc.)
3. Pull:
   - ICP value proposition
   - Top 3 differentiators
   - Universal positioning statement
   - Voice / tone parameters (e.g., Obin = direct, FSI-formal; Vantage = engineering-tone, no-fluff)
4. Feed these into the Claygent prompts below as {voice_block}.
5. If no client context: state "Using generic voice — specify a client for on-brand copy."
```

### Copy Column Spec

| # | Column | Type | Cost | Depends On |
|---|--------|------|------|-----------|
| 1 | `personalization_source` | Claygent | 3–5 | LinkedIn URL OR company website OR trigger event |
| 2 | `first_line` | Claygent | 3 | personalization_source, voice_block |
| 3 | `subject_line` | Claygent | 2 | first_name, company_name, trigger_event |
| 4 | `value_claim` | formula or Claygent | 0–3 | ICP value prop, persona |
| 5 | `cta` | formula | 0 | step_number, persona |
| 6 | `email_body_step_1` | formula | 0 | first_line + value_claim + cta |
| 7 | `email_body_step_2` | formula or Claygent | 0–3 | step_1 reference + new angle |
| 8 | `email_body_step_3` | formula | 0 | breakup framing |
| 9 | `linkedin_message` | Claygent | 2 | persona, trigger_event |
| 10 | `sending_gate_eligible` | formula | 0 | email_verified + suppression + persona |
| 11 | `step_1_eligible` | formula | 0 | sending_gate_eligible |
| 12 | `step_2_eligible` | formula | 0 | sending_gate_eligible AND step_1 sent |
| 13 | `linkedin_step_eligible` | formula | 0 | sending_gate_eligible AND linkedin_url present |

### Claygent Prompt Template — First Line

```
ROLE: You are a senior B2B sales rep writing the opening line of a cold outbound email.

CONTEXT:
- Recipient: {first_name} {last_name}, {title} at {company_name}
- Industry: {industry}
- Trigger event (if any): {trigger_event}
- Their LinkedIn highlight: {personalization_source}
- Our voice: {voice_block}
- Our positioning: {positioning_one_liner}

TASK:
Write ONE sentence (15–25 words) that:
- References a specific observation about them OR their company, NOT a generic compliment
- Connects naturally to the value we'll claim in the next sentence
- Sounds like a peer, not a vendor
- Uses zero clichés ("Hope you're well", "I came across", "I noticed", "Quick question")

FORMAT:
Return ONLY the sentence. No preamble, no signature, no quotation marks.

FALLBACK:
If LinkedIn highlight is empty or generic, use the trigger_event instead.
If both are empty, return: "{first_name}, quick context on why I'm reaching out:"
```

### Subject Line Template

```
ROLE: B2B email subject line writer.

CONTEXT:
- Recipient: {first_name} at {company_name}
- Trigger: {trigger_event}
- Cadence step: {step_number}

TASK: Write a 3–6 word subject line. No emojis. No ALL CAPS. No clickbait.

Use one of these patterns:
- Question: "{topic} at {company_name}?"
- Observation: "{trigger} at {company_name}"
- Direct: "{first_name} — {topic}"
- Curiosity: "{specific term they'd recognize}"

FORMAT: One subject line only.
```

### Sending Gate Formula

```clayscript
IF(
  AND(
    email IS NOT NULL,
    email_verified IN ["valid", "accept_all_high"],
    icp_band IN ["Hot", "Warm"],
    suppression_check == FALSE,
    seniority IN [{TARGET_SENIORITIES}],
    NOT(EXISTS(prior_contact_in_last_30_days)),
    first_line != NULL,
    LENGTH(first_line) > 30
  ),
  TRUE,
  FALSE
)
```

**Per-step eligibility** (Global Rule #8):

```clayscript
// step_1_eligible
sending_gate_eligible == TRUE

// step_2_eligible
sending_gate_eligible == TRUE AND step_1_sent == TRUE AND step_1_replied == FALSE

// linkedin_step_eligible
sending_gate_eligible == TRUE AND linkedin_url IS NOT NULL
```

---

## Step 5 — Execution (Specialized)

### Pre-Push Validation (Mandatory)

```
1. Generate 5 sample rows worth of copy.
2. Read every first_line and subject_line out loud.
3. Test against three filters:
   - Does it sound like a peer or a vendor?
   - Could this sentence apply to 100 other companies? If yes → reject.
   - Does the trigger event make the subject feel relevant? If forced → reject.
4. Reject AND iterate the Claygent prompt until 5/5 pass.
5. Only then move to the 25-row run.
```

### Sequencer Push

```
1. mcp__claude_ai_Clay__list_subroutines
   → Look for "Push to {sequencer}" subroutine
2. If exists:
   mcp__claude_ai_Clay__get_subroutine_input_options
   → Map columns to expected fields
   → mcp__claude_ai_Clay__run_subroutine with sending_gate_eligible filter
3. If not exists — manual:
   In Clay UI:
   a. + Add Action → push-{sequencer}
   b. Map fields (email, first_name, last_name, company_name, custom fields)
   c. CRITICAL: Set Run Condition on action to `sending_gate_eligible = TRUE`
   d. Optional per-step conditions: step_1_eligible, step_2_eligible
   e. Save action
4. Test on 5-row sample.
5. Verify in destination sequencer that 5 contacts appear correctly.
6. Full push only after sample verifies.
```

### 11x AI SDR Push (Coordination Note)

11x agents have their own ICP filter. Coordinate:
- Set Clay's `sending_gate_eligible` to your stricter filter.
- Set 11x's ICP filter to looser (or off).
- This avoids double filtering that drops eligible rows silently.

---

## Anti-Patterns

❌ Generic first lines ("I came across {company_name}…") — reject and re-prompt.
❌ Pushing without `sending_gate_eligible = TRUE` filter — domain reputation damage.
❌ Skipping the Read-Out-Loud test — Claygent will happily produce sounds-fine-looks-bad copy.
❌ Single-step cadence — buyers don't reply on cold email 1. Always build 2–4 step.
❌ One mega Sending Gate without per-step eligibility — sequencer can't independently fan out steps.
❌ Burning Claygent credits on un-qualified rows — gate before generating copy.
❌ Generating copy without client voice when client is identifiable — produces generic, off-brand outbound.

---

## Cost Notes

For 1,000-contact outbound build (deep personalization):

| Column | Per-Row Cost | 1k Rows |
|--------|--------------|---------|
| personalization_source (Claygent) | 3 | 3,000 |
| first_line (Claygent) | 3 | 3,000 |
| subject_line (Claygent) | 2 | 2,000 |
| value_claim (Claygent, conditional) | 3 | 3,000 |
| linkedin_message (Claygent) | 2 | 2,000 |
| **Total** | **13 credits/row** | **13,000 credits ≈ $130** |

Drops to ~$30 if you skip Claygent for value_claim + linkedin_message and use formula-based personalization (industry/persona slot-fills).

---

## Voice Conditionals (When Client Detected)

When client is detected, the Claygent prompts include client-specific guardrails. Examples:

**Obin AI (FSI-formal):**
> "Voice: direct, FSI-formal, no startup-speak. Avoid: 'unlock', 'leverage', 'supercharge'. Reference: AI agent risk, governance, model serving. Differentiator: enterprise GenAI infrastructure that meets FSI compliance bar out of the box."

**Vantage (engineering-tone):**
> "Voice: engineer-to-engineer. No marketing fluff. Speak in metrics (tokens, latency, $/M tokens, model cost). Differentiator: real-time AI cost observability across all models in a tenant's stack."

**Dodge (mid-market expert):**
> "Voice: peer-to-peer GTM operator. Reference: ABM cadences, pipeline math, SDR efficiency. Differentiator: trigger-driven outbound that books meetings without an SDR army."

If no client matched: omit voice constraints, default to "B2B SaaS, direct, peer-tone."

---

## Related

- Source contacts → `/clay-enrich-waterfall` (email + phone) + `/clay-icp-score` (Hot band)
- For inbound demo-form copy/routing → `/clay-inbound-routing`
- For low reply rate diagnosis → `/clay-troubleshoot`
