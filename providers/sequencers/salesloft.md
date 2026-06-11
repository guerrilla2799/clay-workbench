# SalesLoft Integration

**Type**: Sales engagement / sequencer destination
**Best for**: SDR-driven cadences; multi-step outbound; warm follow-up

---

## Push Patterns

### Add to cadence
- Action: `clay/salesloft-push`
- Required: `cadence_id`, `person_data`
- Optional: `account_data` for company-level fields

### Cadence selection logic
Determine which cadence to use based on:
- ICP band (Hot → "T1 SDR cadence", Warm → "Nurture cadence")
- Persona (VP cadence vs Director cadence vs IC cadence)
- Step number (some workflows split early-step from late-step cadences)

## Mandatory: Sending Gate Filter

```
Action: push-salesloft
Run Condition: sending_gate_eligible = TRUE
```

Without this, you'll push unqualified rows. Domain reputation damage results.

## Per-Step Eligibility

```
Action 1: push-salesloft (step 1 cadence)
  Run Condition: step_1_eligible = TRUE
  
Action 2: push-salesloft (step 2 cadence)
  Run Condition: step_2_eligible = TRUE
  
Action 3: push-salesloft (LinkedIn-only cadence)
  Run Condition: linkedin_step_eligible = TRUE
```

This pattern lets you fan out different channels at different speeds.

## Field Mapping

| Clay Column | SalesLoft Field | Notes |
|-------------|-----------------|-------|
| email | email_address | Required |
| first_name | first_name | Required |
| last_name | last_name | Required |
| company_name | company_name | Required for account-level cadences |
| title | title | Personalization |
| linkedin_url | linkedin_url | For LinkedIn steps |
| first_line | custom_field_first_line | Custom variable, must be added to template |
| subject_line | custom_field_subject_line | Custom variable, must be added to template |
| assigned_owner | owner_id | Required for owner routing |

## SalesLoft Template Variables

To use Claygent-generated copy in templates, set up custom variables in SalesLoft:
- Person field → Custom field → name it `first_line`
- Template: use `{{first_line}}` in subject or body
- Clay pushes `first_line` content into that custom field

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Person added to cadence but no email sent | Cadence inactive OR person in another cadence | Check cadence status; SalesLoft prevents dup person-in-cadence |
| Custom field empty in sent email | Variable not added to template OR field mapping mismatch | Verify variable defined in SL; map exact field name |
| Owner not assigned | Owner ID wrong format | Use SL numeric user ID, not email |
| Person.email rejected | Already exists with different status | Update existing person, don't try to create dup |

## Cadence Strategy

| Cadence Type | When to Use |
|--------------|-------------|
| T1 SDR (4-step manual) | Hot Tier 1 ABM accounts |
| Nurture (8-step automated) | Warm leads, lower-touch |
| Account-based | Multiple personas at same company |
| Re-engagement | Closed-lost or stale opps |
| Inbound demo | Quick response to demo request |

## Best Practices

- One Clay workbook can push to multiple cadences via different actions with different run conditions.
- Always test push on 5 rows before full push — verify cadence assignment is correct.
- Set SalesLoft cadence delays to match sending limits to avoid throttling.
