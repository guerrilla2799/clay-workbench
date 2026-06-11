# HubSpot Integration

**Type**: CRM (source + destination)
**Best for**: Source for inbound enrichment; destination for ABM list upserts

---

## Source Patterns

### Inbound webhook
- Form submission → webhook URL in Clay → row appended
- Setup: HubSpot form → Workflows → Webhook → paste Clay webhook URL

### List sync (HubSpot view → Clay)
- Source: `clay/hubspot-source` (action package)
- Input: `list_id` OR `view_id`
- Sync cadence: hourly default, configurable
- Use case: re-enrich existing HubSpot accounts/contacts

## Destination Patterns

### Contact upsert
- Action: `clay/hubspot-push`
- Dedup key: HubSpot ID (if known) OR email (preferred for new contacts)
- ⚠️ Use ONE dedup key — combining ID + email causes conflicts

### Company upsert
- Action: `clay/hubspot-push` (object_type: company)
- Dedup key: domain (most reliable)

### Property mapping
- Map Clay columns → HubSpot custom property names (NOT labels)
- Custom properties: use the API name (`property_name`), not the UI label

## Configuration Best Practices

### Set Up Custom Property for Clay Source
Add a HubSpot custom property: `clay_source_workbook` (text)
Populate with workbook ID — lets you trace any HubSpot record back to its Clay source.

### Lifecycle Stage on Push
Set `lifecyclestage` explicitly on push:
- Hot inbound → MQL or SAL
- Warm inbound → MQL (lower-priority)
- Enriched ABM account → marketingqualifiedlead OR salesqualifiedlead

### Owner Assignment
If using round-robin, set `hubspot_owner_id` from formula column. HubSpot owner IDs (not emails) are required.

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Duplicate contacts created | Dedup key not set or set wrong | Single dedup key — email for contacts, domain for companies |
| Properties not updating | Read-only property OR custom field disabled | Verify property is editable via API; check field permissions |
| List sync slow | List has 10k+ records | Use view filter instead of list, or paginate |
| Owner not assigning | Owner ID format wrong (using email) | Use HubSpot numeric owner_id |

## Sample Push Action Spec

```
Action: push-hubspot
Object type: contact
Dedup key: email
Mappings:
  - email → email
  - first_name → firstname
  - last_name → lastname
  - company_name → company
  - title → jobtitle
  - icp_band → custom_clay_icp_band (custom property)
  - icp_score → custom_clay_icp_score (custom property)
  - assigned_owner → hubspot_owner_id
Lifecycle Stage: marketingqualifiedlead (if icp_band = "Hot")
Run Condition: route_to NOT IN ["SUPPRESSED", "DISQUALIFIED"]
```
