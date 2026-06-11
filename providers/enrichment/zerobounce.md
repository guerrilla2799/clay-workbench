# ZeroBounce

**Type**: Email verification (deliverability check)
**Available via**: Clay-managed
**Best for**: Post-waterfall email verification before sequencer push

---

## What It Returns

| Status | Meaning | Deliverability |
|--------|---------|----------------|
| `valid` | Confirmed deliverable | 99% |
| `accept_all_high` | Catch-all but high confidence | ~70-80% |
| `accept_all_low` | Catch-all, low confidence | ~30-40% |
| `invalid` | Hard bounce | 0% — DROP |
| `unknown` | Can't verify (timeout, weird domain) | ~50% — DROP unless desperate |
| `spamtrap` | Spam trap | 0% — DROP, DOMAIN REPUTATION DAMAGE |
| `do_not_mail` | Role-based (info@, sales@) | DROP or use carefully |

## Cost

| Operation | Credits |
|-----------|---------|
| Verify email | 1 |

## When to Use

- ✅ After every email waterfall (mandatory)
- ✅ Before any sequencer push (mandatory)
- ✅ As a periodic re-verify on stale CRM contacts

## When NOT to Use

- ❌ On Apollo "verified" emails (Apollo's own verification is sufficient; wasted credit)
- ❌ Without a sequencer downstream — verification value comes from preventing bounce, which only matters if you send

## Configuration

```
Column: email_verified
Provider: ZeroBounce
Input: {email}
Run Condition: email IS NOT NULL AND email_source != "apollo_verified"
```

## Sending Gate Implication

```clayscript
sending_gate_eligible includes:
  email_verified IN ["valid", "accept_all_high"]
```

Reject:
- `accept_all_low` — too risky
- `unknown` — unverifiable
- `spamtrap` — DOMAIN DEATH if you send
- `invalid` — guaranteed bounce
- `do_not_mail` — unless intentional (rare)

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Many "unknown" results | Domain MX records refusing SMTP checks | Use Bouncer or Kickbox for catch-all scoring |
| 1 credit per row even on Apollo-verified | Run condition not skipping Apollo-verified | Add `email_source != "apollo_verified"` to run condition |
| Spam-trap matches | Source list polluted with bought data | Drop the source; audit input quality |

## Alternatives (Functionally Equivalent)

| Verifier | When Better |
|----------|-------------|
| NeverBounce | Comparable; switch only if ZeroBounce coverage issues |
| MillionVerifier | Cheaper bulk; ~5% lower confidence |
| Bouncer | Better catch-all scoring (EU-friendly) |
| Kickbox | Best catch-all scoring; more expensive |

Default to ZeroBounce. Switch only if catch-all rate is unusually high in your list.
