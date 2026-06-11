# Clay Action Registry

Catalog of Clay action keys, package IDs, input shapes, and known gotchas. Pattern adapted from TenSpy-ai/claycast.

⚠️ Action keys can change between Clay releases. When a known action doesn't behave as expected, check current registry first.

---

## Core Column Types

### text
- **Use**: Plain string column (manual entry or formula output)
- **Input keys**: `value`
- **Returns**: string

### formula
- **Use**: Clayscript formula column
- **Input keys**: `formula`
- **Returns**: any (formula result)
- **Gotcha**: Empty formula returns NULL silently — verify before save

### http
- **Use**: HTTP request to any URL
- **Input keys**: `url`, `method`, `headers`, `body`
- **Returns**: JSON response
- **Gotcha**: Rate limits enforced per workspace

### claygent (AI Research)
- **Action key**: `"use-ai"` ⚠️ (NOT `"ai"` — that key silently drops inputs)
- **Use**: AI research agent column
- **Input keys**: `prompt`, `max_sources`, `model`
- **Returns**: AI output (string or JSON depending on prompt format)
- **Gotcha**: Empty prompt is silently shipped — wrap in `verify()` (see claycast pattern)

### lookup
- **Use**: Cross-table lookup
- **Input keys**: `source_table`, `match_column`, `return_column`
- **Returns**: matched value

---

## Enrichment Actions

### find-company
- **Package**: `clay/find-company`
- **Input**: `domain` OR `company_name`
- **Output**: company object (industry, employees, revenue, HQ, social URLs)
- **Cost**: 1 credit
- **Gotcha**: Company name only (no domain) drops match rate ~25%. Always prefer domain.

### find-contacts-at-company
- **Package**: `clay/find-contacts`
- **Input**: `company_domain`, `titles[]`, `seniority`, `departments`
- **Output**: contact[] array
- **Cost**: 1 credit per returned contact
- **Gotcha**: `titles` is an EXACT match by default — use `title_keywords` for fuzzy.

### email-waterfall (Clay-managed prebuilt)
- **Package**: `clay/email-waterfall-prebuilt`
- **Input**: `first_name`, `last_name`, `company_domain`
- **Output**: `email`, `email_status`, `source_provider`
- **Cost**: Variable — 1 credit on first match, escalates per provider
- **Gotcha**: Graceful exit on first valid email — but if all providers fail, charges minimum credits per attempt.

### email-verify
- **Package**: `clay/email-verify`
- **Input**: `email`
- **Output**: `status` (valid / invalid / catch_all / unknown)
- **Cost**: 1 credit
- **Gotcha**: Catch-all domains score ~50% deliverable in real-world testing. Treat as risky.

### phone-waterfall
- **Package**: `clay/phone-waterfall`
- **Input**: `linkedin_url` OR (`first_name` + `last_name` + `company_domain`)
- **Output**: `phone`, `phone_type` (mobile / direct / hq), `source_provider`
- **Cost**: Variable — 1 to 4 credits per match
- **Gotcha**: Mobile match rate caps at ~40%. Set expectations.

---

## Source Actions

### webhook
- **Package**: `clay/webhook-source`
- **Input**: incoming JSON payload
- **Output**: row(s) appended to table
- **Cost**: 0 credits per row received (enrichments cost extra)
- **Gotcha**: Webhook URL is workspace-scoped — share carefully.

### csv-upload
- **Package**: `clay/csv-source`
- **Input**: file
- **Output**: rows appended
- **Cost**: 0 credits
- **Gotcha**: Auto-detected types can misclassify — verify column types after upload.

### hubspot-list
- **Package**: `clay/hubspot-source`
- **Input**: `list_id` OR `view_id`
- **Output**: synced contacts/companies
- **Cost**: 0 credits
- **Gotcha**: Sync cadence configurable (hourly default). Manual refresh available.

### salesforce-report
- **Package**: `clay/salesforce-source`
- **Input**: `report_id` OR SOQL query
- **Output**: synced records
- **Cost**: 0 credits
- **Gotcha**: Requires Salesforce API user with read scope.

---

## Action / Destination Actions

### push-hubspot
- **Package**: `clay/hubspot-push`
- **Input**: object type (contact / company / deal), field mappings
- **Output**: HubSpot object ID
- **Cost**: 0 credits
- **Gotcha**: Set up dedup by HubSpot ID OR email — never both, causes conflicts.

### push-salesforce
- **Package**: `clay/salesforce-push`
- **Input**: object type, field mappings, upsert key
- **Output**: SFDC record ID
- **Cost**: 0 credits
- **Gotcha**: Custom fields require API name (not label).

### push-salesloft
- **Package**: `clay/salesloft-push`
- **Input**: `cadence_id`, `person_data`, optional `account_data`
- **Output**: SalesLoft person ID
- **Cost**: 0 credits
- **Gotcha**: Set Sending Gate filter on this action — see Global Rule #2.

### push-outreach
- **Package**: `clay/outreach-push`
- **Input**: `sequence_id`, `prospect_data`
- **Output**: Outreach prospect ID
- **Cost**: 0 credits

### push-apollo
- **Package**: `clay/apollo-push`
- **Input**: `sequence_id`, `contact_data`
- **Output**: Apollo contact ID
- **Cost**: 0 credits

### push-11x
- **Package**: `clay/11x-push`
- **Input**: `agent_id`, `lead_data`
- **Output**: 11x lead ID
- **Cost**: 0 credits
- **Gotcha**: 11x agents have their own ICP filter — coordinate with Clay-side gate to avoid double filtering.

### push-smartlead / push-instantly
- **Package**: `clay/smartlead-push` / `clay/instantly-push`
- **Input**: `campaign_id`, `lead_data`
- **Output**: lead ID
- **Cost**: 0 credits
- **Gotcha**: Both impose daily send limits — coordinate batch size with limits.

### slack-notify
- **Package**: `clay/slack-message`
- **Input**: `channel`, `message_template`
- **Output**: Slack message ID
- **Cost**: 0 credits
- **Gotcha**: Channel must be in connected Slack workspace. Use for high-value match alerts.

### webhook-out
- **Package**: `clay/webhook-action`
- **Input**: `url`, `method`, `headers`, `body_template`
- **Output**: response (logged)
- **Cost**: 0 credits

---

## Verification Pattern (claycast)

Before triggering any action with a Clay-managed run, verify these silent-failure cases:

```python
# Pseudocode — adapt for actual builder library
def verify(workbook):
    for action in workbook.actions:
        # 1. AI columns: empty prompt is silently shipped
        if action.kind == "use-ai" and not action.inputs.get("prompt"):
            raise BuilderError(f"AI column '{action.name}' has empty prompt")

        # 2. Required inputs unwired
        for req in action.required_inputs:
            if req not in action.inputs or action.inputs[req] is None:
                raise BuilderError(f"Action '{action.name}' missing required input '{req}'")

        # 3. Action key typo guard
        if action.kind == "ai":
            raise BuilderError(f"Use 'use-ai', not 'ai' — action '{action.name}' will silently drop inputs")

        # 4. Sending Gate guard
        if action.kind.startswith("push-") and action.is_sequencer:
            if not workbook.has_column("sending_gate_eligible"):
                raise BuilderError("Sequencer action requires a Sending Gate column (Rule #2)")
```

---

## Known Pitfalls

| Symptom | Likely Cause |
|---------|--------------|
| AI column returns blank for every row | `actionKey: "ai"` instead of `"use-ai"` |
| Email waterfall burning credits with 0 matches | Domain column not wired to waterfall input |
| HubSpot push creates duplicates | Dedup key not set OR set to both ID and email |
| Sequencer push runs on unqualified rows | Sending Gate filter not configured on push action |
| Auto-run firing during build | `auto_run` not set to `false` during construction |
| Webhook source not appending rows | Webhook URL changed after recipe save — regenerate |
| Formula column returns NULL silently | Empty formula or syntax error — check formula editor |
