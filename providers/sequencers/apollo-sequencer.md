# Apollo Sequences

**Type**: Sales engagement built-into Apollo platform
**Best for**: When you're already paying for Apollo seats; mid-market SDR motions

---

## Push Patterns

- Action: `clay/apollo-push`
- Required: `sequence_id`, `contact_data`
- Uses Apollo's own contact records (creates or updates if exists)

## Mandatory: Sending Gate Filter

```
Action: push-apollo
Run Condition: sending_gate_eligible = TRUE
```

## Field Mapping

| Clay Column | Apollo Field |
|-------------|--------------|
| email | email |
| first_name | first_name |
| last_name | last_name |
| company_domain | organization (linked) |
| title | title |
| custom Claygent variables | Apollo custom fields |

## Cost Note

Apollo's email sending and sequencing is built-in (no extra credit cost). However, Apollo also has its own deliverability quirks — manage sending volume per mailbox.

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Contact created but not added to sequence | Sequence at capacity OR contact filter conflict | Check sequence settings |
| Custom variables blank | Field name mismatch between Clay push and Apollo template | Verify field name exactly |
| Deliverability issues | Apollo's shared IP pool | Use dedicated IP add-on for >5k/mo sending |

## When to Use

- ✅ You're already an Apollo customer (no marginal seat cost)
- ✅ Mid-market SDR motion
- ✅ Apollo's data + sending stack is one tool

## When Not to Use

- ❌ Enterprise / Fortune 500 motions (SalesLoft or Outreach preferred)
- ❌ Brand-new sender domain (Apollo's shared pool risk)
- ❌ Compliance-heavy industries (more control via dedicated tool)
