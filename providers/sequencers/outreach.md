# Outreach Integration

**Type**: Sales engagement / sequencer destination
**Best for**: Enterprise SDR teams; complex multi-step sequences with conditional logic

---

## Push Patterns

- Action: `clay/outreach-push`
- Required: `sequence_id`, `prospect_data`
- Field mapping similar to SalesLoft

## Mandatory: Sending Gate Filter

```
Action: push-outreach
Run Condition: sending_gate_eligible = TRUE
```

## Per-Step Eligibility

```
Action 1: push-outreach (email step 1)
  Run Condition: step_1_eligible = TRUE
  
Action 2: push-outreach (email step 2)
  Run Condition: step_2_eligible = TRUE
```

## Field Mapping

| Clay Column | Outreach Field |
|-------------|----------------|
| email | emails |
| first_name | firstName |
| last_name | lastName |
| company_name | accountName |
| title | title |
| linkedin_url | linkedInUrl |
| first_line | customField1 (or named custom variable) |
| subject_line | customField2 |
| assigned_owner | ownerId |

## Custom Variables (Snippets)

In Outreach, custom Snippets pull from prospect custom fields. Map Claygent-generated columns to Outreach custom fields, then reference in Snippets via `{{custom_field_name}}`.

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Prospect in sequence but emails not firing | Sequence paused OR mailbox throttling | Check sequence + mailbox limits |
| Duplicate prospects | Outreach dedup off | Enable dedup by email at workflow level |
| Custom field empty | Mapping not configured OR snippet variable wrong | Verify field-to-snippet binding |
| Sequence rejection on push | Prospect in another active sequence | Resolve sequence conflict before push |

## Notes

- Outreach prefers single-active-sequence per prospect. Configure your Clay logic to respect that.
- Tags in Outreach are useful for downstream reporting — push a `clay_source: workbook_name` tag for traceability.
