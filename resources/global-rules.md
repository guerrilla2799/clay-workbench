# Clay Workbench — Global Rules

These 8 rules are NON-NEGOTIABLE. Apply them in every sub-skill. Lifted and updated from the mariosworkflows/clay-engineer pattern.

---

## 1. Gates Before Credits

Never run paid enrichments on unqualified rows. Every workbook must have an **ICP qualification gate** (formula column returning TRUE/FALSE) **before** any column that costs credits. Set every paid column's "Run condition" to `gate_qualified = TRUE`.

If no gate column exists yet, build it first. If the user pushes back, repeat: "We'll burn credits on rows that will never close. The gate is the cheapest insurance."

## 2. Sending Gate Before Export

Every workbook that exports to a sequencer (SalesLoft / Outreach / Apollo / 11x / Smartlead / Instantly) requires a **Sending Gate** formula column as the final qualification before export. Required components:

- Email present AND email status ∈ {valid, accept_all_high}
- Phone present OR phone optional (per ICP)
- LinkedIn URL present (if persona requires)
- Suppression check (no opt-out, no bounced-in-last-90, no current customer)
- Persona / seniority match
- Trigger event present (when ABM motion)

The Sending Gate column is named `sending_gate_eligible` and returns TRUE/FALSE. Export action filters on `sending_gate_eligible = TRUE`.

## 3. Data Unification

Always unify firmographic + persona + signal data into a single coherent row before scoring or exporting. Do not score in fragments. The row should answer in one read: "Who is this, why now, where does it go?"

## 4. ICP Qualification First

The first qualification step is the ICP fit check — not enrichment. Use the cheapest possible signal (domain pattern, public website scrape, free Apollo company match) to disqualify before spending credits on enrichment.

Disqualify aggressively. The default move is "drop the row," not "enrich more."

## 5. Free Before Paid

For every data point you want to capture, check the **free** source first:
- Domain → free company match (Clay native, 0 credits)
- LinkedIn URL → free if found via search
- Public website scrape → free via Claygent or HTTP request
- Apollo company data → free at small volumes

Only escalate to paid providers when the free source has missed. This is rule #2 in the waterfall design.

## 6. Never Assume — Always Ask

Run the 8-question intake (see `intake-questions.md`) before composing any workbook. If the user says "you decide," ask which DIMENSION they want a recommendation on, then offer 2–3 options.

Forbidden phrases when fabricating: "I'll use a reasonable default," "let's assume," "typically users want X." Replace with: "Two options here. Which fits — A or B?"

## 7. Clay-Managed vs Own API Key

Always confirm whether the enrichment uses a **Clay-managed** integration (credits debit Clay account) or the user's **own API key** (credits debit user's vendor account). These have different cost profiles, rate limits, and fallback behavior. Default to Clay-managed unless the user already has the vendor relationship.

For every column added: state which side the credits hit.

## 8. Multiple Sending Steps Are Supported

When designing outbound: assume the buyer journey has 2–4 sending steps (email 1 → LinkedIn connect → email 2 → call). Build separate "step eligible" columns per step rather than one mega-Sending-Gate. This lets the sequencer fan out steps independently and respect per-channel suppression.

---

## Enforcement

- Every sub-skill's pre-flight check must verify these 8 rules before allowing build.
- The `clay-troubleshoot` skill uses these as its diagnostic checklist.
- If a rule is intentionally skipped (e.g., user explicitly wants to enrich without a gate for a one-time spike), log it as `gate-override: <reason>` in the workbook description column.

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
