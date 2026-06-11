# Clay Workbench — Global Rules

These 8 rules are NON-NEGOTIABLE. Apply them in every sub-skill. Lifted and updated from the mariosworkflows/clay-engineer pattern.

---

## 1. Gates Before Credits

Never run paid enrichments on unqualified rows. Every workbook must have an **ICP qualification gate** (formula column returning TRUE/FALSE) **before** any column that costs credits. Set every paid column's "Run condition" to `gate_qualified = TRUE`.

If no gate column exists yet, build it first. If the user pushes back, repeat: "We'll burn credits on rows that will never close. The gate is the cheapest insurance."

**Enforced by:** `/clay-list-clean` (pre-Clay disqualification before any column runs) · `/clay-icp-score` (builds the gate column itself) · `/clay-account-research` + `/clay-prospect-research` (research runs only on gated rows) · `/clay-buying-signals` (intent enrichment runs only on gated rows) · `/clay-claygent-iterator` (Claygent counts as paid — gate first) · `/clay-credits` (forecasts assume gate compliance) · `/clay-cost-audit` (Check 1 of 12 is gate enforcement)

## 2. Sending Gate Before Export

Every workbook that exports to a sequencer (SalesLoft / Outreach / Apollo / 11x / Smartlead / Instantly) requires a **Sending Gate** formula column as the final qualification before export. Required components:

- Email present AND email status ∈ {valid, accept_all_high}
- Phone present OR phone optional (per ICP)
- LinkedIn URL present (if persona requires)
- Suppression check (no opt-out, no bounced-in-last-90, no current customer)
- Persona / seniority match
- Trigger event present (when ABM motion)

The Sending Gate column is named `sending_gate_eligible` and returns TRUE/FALSE. Export action filters on `sending_gate_eligible = TRUE`.

**Enforced by:** `/clay-outbound` (final pre-export check) · `/clay-enrich-waterfall` (feeds email validity into the gate) · `/clay-prospect-research` (feeds persona/seniority + warm-path into the gate) · `/clay-buying-signals` (intent score can flip suppression on inactive accounts) · `/clay-data-hygiene` (keeps suppression list fresh) · `/clay-cost-audit` (Check 2 — flags exports missing the gate)

## 3. Data Unification

Always unify firmographic + persona + signal data into a single coherent row before scoring or exporting. Do not score in fragments. The row should answer in one read: "Who is this, why now, where does it go?"

**Enforced by:** `/clay-account-research` (multi-source firmographic + news + hiring unified per account) · `/clay-prospect-research` (multi-source person dossier unified per contact) · `/clay-buying-signals` (composite intent fuses 8+ sources into one time-decayed score) · `/clay-icp-score` (scores on unified row, not fragments) · `/clay-data-hygiene` (`crm_record_health` table keeps the unified view intact over time)

## 4. ICP Qualification First

The first qualification step is the ICP fit check — not enrichment. Use the cheapest possible signal (domain pattern, public website scrape, free Apollo company match) to disqualify before spending credits on enrichment.

Disqualify aggressively. The default move is "drop the row," not "enrich more."

**Enforced by:** `/clay-list-clean` (domain/email/title/geo disqualification at zero credits — the cheapest possible signal) · `/clay-icp-score` (10-point fit score before any paid column) · `/clay-data-hygiene` (rolling ICP-fit re-check on aging CRM records) · `/clay-abm-list` (firmographic + trigger gate before research/enrichment) · `/clay-cost-audit` (Check 4 — flags workbooks running paid columns before ICP disqualification)

## 5. Free Before Paid

For every data point you want to capture, check the **free** source first:
- Domain → free company match (Clay native, 0 credits)
- LinkedIn URL → free if found via search
- Public website scrape → free via Claygent or HTTP request
- Apollo company data → free at small volumes

Only escalate to paid providers when the free source has missed. This is rule #2 in the waterfall design.

**Enforced by:** `/clay-enrich-waterfall` (free-tier providers ordered first in every waterfall) · `/clay-account-research` + `/clay-prospect-research` (Claygent free-web scrape attempted before paid intent providers) · `/clay-credits` (provider mix forecast explicitly compares free vs paid tiers) · `/clay-cost-audit` (Check 5 — flags waterfalls running paid first) · `/clay-list-clean` (free domain/MX checks before any paid validation)

## 6. Never Assume — Always Ask

Run the 8-question intake (see `intake-questions.md`) before composing any workbook. If the user says "you decide," ask which DIMENSION they want a recommendation on, then offer 2–3 options.

Forbidden phrases when fabricating: "I'll use a reasonable default," "let's assume," "typically users want X." Replace with: "Two options here. Which fits — A or B?"

**Enforced by:** Every sub-skill runs intake before build. Particularly load-bearing in `/clay-buying-signals` (signal source selection), `/clay-account-research` + `/clay-prospect-research` (depth/breadth tradeoff), `/clay-data-hygiene` (which CRM is source of truth), `/clay-signal-monitor` (severity thresholds + routing destinations), `/clay-template-library` (anonymization rules per template).

## 7. Clay-Managed vs Own API Key

Always confirm whether the enrichment uses a **Clay-managed** integration (credits debit Clay account) or the user's **own API key** (credits debit user's vendor account). These have different cost profiles, rate limits, and fallback behavior. Default to Clay-managed unless the user already has the vendor relationship.

For every column added: state which side the credits hit.

**Enforced by:** `/clay-credits` (provider mix forecast splits Clay-managed vs own-key explicitly; required input before any forecast) · `/clay-cost-audit` (Check 7 — flags columns where ownership side is unlabeled or inconsistent across the portfolio) · `/clay-enrich-waterfall` (waterfall steps label managed vs own-key per tier) · `/clay-troubleshoot` (uses ownership-side as a primary diagnostic axis when credits don't reconcile)

## 8. Multiple Sending Steps Are Supported

When designing outbound: assume the buyer journey has 2–4 sending steps (email 1 → LinkedIn connect → email 2 → call). Build separate "step eligible" columns per step rather than one mega-Sending-Gate. This lets the sequencer fan out steps independently and respect per-channel suppression.

**Enforced by:** `/clay-outbound` (generates per-step copy + per-step eligibility columns) · `/clay-prospect-research` (warm-path + personalized entry line are per-step inputs — first email vs LinkedIn connect ask different things) · `/clay-signal-monitor` (severity tier maps to which step gets triggered, not whether the whole cadence runs)

---

## Enforcement

- Every sub-skill's pre-flight check must verify these 8 rules before allowing build.
- `/clay-troubleshoot` uses these as its single-workbook diagnostic checklist.
- `/clay-cost-audit` uses these as its **portfolio-wide** 12-check audit — every workbook in the workspace is scored against all 8 rules plus 4 additional waste/ROI checks.
- If a rule is intentionally skipped (e.g., user explicitly wants to enrich without a gate for a one-time spike), log it as `gate-override: <reason>` in the workbook description column.

---

## Sub-skill mandatory pre-checks (not yet promoted to Global Rules)

These two operational gates were introduced in v2.0.0 sub-skills. They behave like Global Rules in spirit — violating them produces the exact failure modes the existing 8 rules were built to prevent — but they are scoped to specific sub-skills rather than every workbook. Treat as mandatory inside those sub-skills; treat as candidate Global Rules pending review:

- **Claygent scorecard before scaling.** No Claygent column ships at production volume without first running the structured 5 → 25 → 100 row iteration loop and passing the scorecard (PASS %, FABRICATED %, credits/row). Enforced by `/clay-claygent-iterator`. Prevents the "looked great on 5 rows, hallucinated on 500" failure that wastes credits AND ships bad data into outbound.
- **Backfill discrimination ≥3x lift before `auto_run`.** No composite intent score auto-runs against pipeline until the backfill test shows ≥3x lift on closed-won vs closed-lost over the trailing 12 months. Enforced by `/clay-buying-signals`. Prevents scoring on "signals" that don't actually discriminate buyers from non-buyers.

---

## Why These Specific Rules

Each rule traces back to a recurring failure mode in Clay workbooks:

| Rule | Failure It Prevents |
|------|---------------------|
| 1 — Gates Before Credits | $500+ burn rates on unqualified rows |
| 2 — Sending Gate | Exporting bad emails → domain reputation damage |
| 3 — Data Unification | Scoring on stale or fragmented data |
| 4 — ICP First | Enriching companies that were never ICP |
| 5 — Free Before Paid | 2–10x cost inflation when paid runs first |
| 6 — Never Assume | Building the wrong workbook entirely |
| 7 — Clay-Managed vs Own Key | Credit accounting surprises |
| 8 — Multi-Step | One-shot sequences that collapse after step 1 |
