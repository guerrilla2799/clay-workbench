# Email Waterfall — EU

**Slug**: `email-waterfall-eu` · **Version**: `1.0` · **Use case**: `enrichment` · **Motion**: `slg`

Contact-keyed email waterfall optimized for **EU ICPs**. Dropcontact → Datagma → Findymail, with ZeroBounce verification. Dropcontact leads because of better GDPR-compliance + higher EU match rate than Apollo.

## When to use this
- ICP is concentrated in UK / DACH / France / Benelux / Nordics
- You've seen Apollo-led waterfalls return <50% match rate on EU lists
- GDPR-compliant outbound is a hard requirement (Dropcontact documents opt-in source)

## What it produces
- 70–80% email match rate on EU ICPs
- `email_source` column for diagnostic
- All emails verified via ZeroBounce (no provider ships EU emails pre-verified at usable confidence)

## Required inputs (placeholders to fill)
| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{ICP_GATE_FORMULA}}` | Clayscript formula that returns TRUE for in-ICP rows | `AND(account_tier IN ["T1", "T2"], hq_country IN ["United Kingdom", "Germany", "France"])` |

## Required integrations
- Clay providers (in order): Dropcontact, Datagma, Findymail, ZeroBounce
- Dropcontact: Clay-managed or own-key (own-key has better rate limits for high-volume EU lists)

## Cost
- Estimated credits/row: 5–7
- 1k contacts: ~$60–80 at $0.01/credit
- Match rate: 70–80% (EU)

## Known good for
- Anonymized from production patterns; EU-variant of golden ref 03 waterfall

## Notes / Gotchas
- **Verify everything**: unlike the US waterfall, no Apollo-verified shortcut. Skip-verification logic would over-trust EU provider output.
- **DACH catch-all domains** (`@kanzlei-*.de`, many corporate firewalls) flag as `accept_all_high` in ZeroBounce — treat as deliverable but track bounce rate separately.
- LinkedIn URL input is **strongly recommended** — Dropcontact match rate jumps 15–20% when LinkedIn URL is present.
- For mixed US+EU lists, run rows through both this and `email-waterfall-us-smb` with country-based routing — don't try to make one waterfall serve both.
- GDPR: document the opt-in source for any Dropcontact-returned email if used for cold outbound.

## Changelog
- v1.0 — 2026-06-10 — initial bootstrap, EU variant
