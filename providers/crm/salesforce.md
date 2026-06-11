# Salesforce Integration

**Type**: CRM (source + destination)
**Best for**: Enterprise CRM destination; SOQL-driven source lists

---

## Source Patterns

### SOQL query → Clay
- Source: `clay/salesforce-source`
- Input: SOQL query OR report_id
- Use case: pull existing Accounts / Contacts / Leads matching a query

### Report-based sync
- Salesforce report → Clay
- Cadence: configurable

## Destination Patterns

### Lead upsert
- Action: `clay/salesforce-push`, object: Lead
- Dedup key: email OR external_id custom field
- Note: Lead is for net-new prospects; for existing Accounts, use Contact

### Contact + Account upsert
- Two-step: ensure Account exists (upsert on Account domain), then Contact (upsert on email + link to Account ID)
- Account dedup: Account.Website OR custom Website_Normalized__c field
- Contact dedup: Email

### Custom field mapping
- Use API names (e.g., `Custom_Field__c`), NOT labels
- Custom fields ending in `__c`

## Configuration Notes

### Salesforce User Permissions
Clay's connection user needs:
- Read/Write on Lead, Contact, Account, Opportunity (as relevant)
- Edit Standard Fields permission
- API Enabled on profile

### Object Strategy
- **Inbound demo / contact-us** → Lead first, convert to Contact + Account + Opportunity on qualification
- **ABM target accounts** → Account directly (skip Lead)
- **Existing contact data refresh** → Contact upsert

### Owner Assignment
- `OwnerId` requires Salesforce User ID (15 or 18 char)
- Round-robin formula → owner_id_pool[index]

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| API limit hit | Daily API limit reached | Throttle Clay run cadence OR upgrade SFDC API tier |
| Duplicate Leads | Dedup key wrong OR Standard dedup OFF | Use email as dedup; verify SFDC duplicate rules enabled |
| Field write fails | Field is calculated OR field-level security | Check field accessibility for Clay's API user |
| Lookup field "stuck" | Trying to set a relationship by name, not ID | Always use record IDs (15/18 char) for lookup fields |

## Lead vs Contact Decision

| Scenario | Object |
|----------|--------|
| Brand-new prospect from inbound form | Lead |
| Person already known but new buying role | Contact (don't create dup Lead) |
| Mass enrichment of existing contacts | Contact |
| Net-new ABM accounts with no prior touch | Account (then Contacts under it) |

## Sample Push Action Spec

```
Action: push-salesforce
Object type: Lead
Dedup key: Email
Mappings:
  - email → Email
  - first_name → FirstName
  - last_name → LastName
  - company_name → Company
  - title → Title
  - icp_score → ICP_Score__c (custom field)
  - icp_band → ICP_Band__c (custom field)
  - assigned_owner → OwnerId
LeadSource: "Clay Inbound Router"
Status: "Open - Not Contacted"
Run Condition: route_to = "SDR_QUEUE" AND suppression_check = FALSE
```
