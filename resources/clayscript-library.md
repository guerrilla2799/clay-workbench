# Clayscript Formula Library

Reusable Clayscript formulas — copy/paste into Clay's Formula columns. All formulas are 0-credit operations. Merge of forma-norden's clayscript-library + ColdIQ's copy-paste-formulas.

---

## String Manipulation

### Extract domain from email
```clayscript
SPLIT(email, "@")[1]
```

### Normalize domain (strip www., trailing slash, lowercase)
```clayscript
LOWER(REPLACE(REPLACE(REPLACE(domain, "https://", ""), "www.", ""), "/", ""))
```

### Initialize a name (Brandon Redlinger → B. Redlinger)
```clayscript
CONCAT(SUBSTRING(first_name, 0, 1), ". ", last_name)
```

### Clean & title-case a job title
```clayscript
TITLE_CASE(TRIM(title))
```

### Build a LinkedIn URL from slug
```clayscript
IF(linkedin_slug IS NOT NULL,
  CONCAT("https://linkedin.com/in/", linkedin_slug),
  NULL)
```

### Parse first/last from "Full Name"
```clayscript
// first_name
SPLIT(full_name, " ")[0]

// last_name
SPLIT(full_name, " ")[LENGTH(SPLIT(full_name, " ")) - 1]
```

---

## Coalesce / Fallback Patterns

### Email waterfall coalesce
```clayscript
COALESCE(email_apollo, email_findymail, email_datagma, email_hunter, email_dropcontact)
```

### Email source tracking
```clayscript
IF(email_apollo IS NOT NULL, "apollo",
IF(email_findymail IS NOT NULL, "findymail",
IF(email_datagma IS NOT NULL, "datagma",
IF(email_hunter IS NOT NULL, "hunter",
IF(email_dropcontact IS NOT NULL, "dropcontact",
NULL)))))
```

### Phone waterfall coalesce
```clayscript
COALESCE(phone_apollo, phone_datagma, phone_contactout, phone_cognism)
```

---

## Date Math

### Days since a timestamp
```clayscript
DAYS_BETWEEN(NOW(), event_date)
```

### Days until a timestamp
```clayscript
DAYS_BETWEEN(target_date, NOW())
```

### Is event within last N days?
```clayscript
DAYS_BETWEEN(NOW(), event_date) <= 90
```

### Days since last touch (or NULL if never touched)
```clayscript
IF(last_touch_date IS NOT NULL,
  DAYS_BETWEEN(NOW(), last_touch_date),
  NULL)
```

---

## Email Domain Logic

### Is personal email?
```clayscript
SPLIT(email, "@")[1] IN [
  "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
  "aol.com", "icloud.com", "me.com", "live.com",
  "proton.me", "protonmail.com", "yandex.com", "qq.com"
]
```

### Is government email?
```clayscript
ENDS_WITH(email, ".gov") OR ENDS_WITH(email, ".mil")
```

### Is education email?
```clayscript
ENDS_WITH(email, ".edu") OR ENDS_WITH(email, ".ac.uk") OR ENDS_WITH(email, ".edu.au")
```

---

## Seniority Detection

### Senior decision-maker?
```clayscript
title_lower = LOWER(title)
ANY([
  CONTAINS(title_lower, "vp "),
  CONTAINS(title_lower, "vice president"),
  CONTAINS(title_lower, "chief "),
  CONTAINS(title_lower, "ceo"),
  CONTAINS(title_lower, "cto"),
  CONTAINS(title_lower, "cmo"),
  CONTAINS(title_lower, "cro"),
  CONTAINS(title_lower, "head of "),
  CONTAINS(title_lower, "director")
])
```

### Department classification
```clayscript
title_lower = LOWER(title)
IF(ANY([CONTAINS(title_lower, "sales"), CONTAINS(title_lower, "revenue")]), "Sales",
IF(ANY([CONTAINS(title_lower, "marketing"), CONTAINS(title_lower, "growth"), CONTAINS(title_lower, "demand")]), "Marketing",
IF(CONTAINS(title_lower, "rev ops"), "RevOps",
IF(CONTAINS(title_lower, "product"), "Product",
IF(CONTAINS(title_lower, "engineering"), "Engineering",
IF(CONTAINS(title_lower, "finance"), "Finance",
IF(CONTAINS(title_lower, "founder"), "Founder",
"Other")))))))
```

---

## ICP Gate Patterns

### Industry whitelist
```clayscript
industry IN ["Software", "SaaS", "Fintech", "MarTech", "HealthTech", "EdTech"]
```

### Employee count band
```clayscript
AND(employee_count >= 50, employee_count <= 5000)
```

### Geo allowlist
```clayscript
hq_country IN ["United States", "Canada", "United Kingdom", "Ireland", "Australia", "New Zealand"]
```

### Multi-condition pass_1 gate
```clayscript
AND(
  industry IN ["Software", "SaaS", "Fintech"],
  employee_count >= 50,
  employee_count <= 5000,
  hq_country IN ["United States", "United Kingdom", "Canada"]
)
```

### Trigger required gate
```clayscript
AND(
  pass_1_qualified == TRUE,
  trigger_event IS NOT NULL,
  DAYS_BETWEEN(NOW(), trigger_event_date) <= 90
)
```

---

## Suppression Patterns

### Domain in customer list
```clayscript
EXISTS(LOOKUP("customers_table", "domain", company_domain))
```

### Recent contact (last 30 days)
```clayscript
IF(last_contact_date IS NOT NULL,
  DAYS_BETWEEN(NOW(), last_contact_date) <= 30,
  FALSE)
```

### Combined suppression check
```clayscript
OR(
  is_customer == TRUE,
  is_opt_out == TRUE,
  recent_contact_30d == TRUE,
  bounce_in_90d == TRUE
)
```

---

## Routing Formulas

### Tier-based routing
```clayscript
IF(suppression_check == TRUE, "SUPPRESSED",
IF(account_tier == "T1", "SDR_QUEUE_T1",
IF(account_tier == "T2", "MARKETING_NURTURE",
IF(account_tier == "T3", "PROGRAMMATIC",
"DISQUALIFIED"))))
```

### Round-robin assignment
```clayscript
sdr_pool = ["alice_id", "bob_id", "carla_id", "dan_id"]
sdr_pool[MOD(ROW_INDEX, LENGTH(sdr_pool))]
```

### Territory-based assignment
```clayscript
IF(hq_country IN ["United Kingdom", "Germany", "France", "Spain", "Italy"],
  ["sdr_emea_1", "sdr_emea_2"][MOD(ROW_INDEX, 2)],
IF(hq_country IN ["United States", "Canada"],
  ["sdr_na_1", "sdr_na_2", "sdr_na_3"][MOD(ROW_INDEX, 3)],
  "sdr_intl_default")
)
```

### Weighted round-robin (Alice gets 50% more)
```clayscript
weighted_pool = ["alice", "alice", "alice", "bob", "bob", "carla", "carla"]
weighted_pool[MOD(ROW_INDEX, LENGTH(weighted_pool))]
```

---

## Scoring Formulas

### 10-point ICP score components
```clayscript
// fit_score (out of 5)
(IF(industry IN [{ICP_INDUSTRIES}], 2, 0))
+ (IF(AND(employee_count >= {MIN}, employee_count <= {MAX}), 1, 0))
+ (IF(hq_country IN [{GEOS}], 1, 0))
+ (IF(ANY(tech_stack_signals IN [{ICP_STACK}]), 1, 0))

// intent_score (out of 5)
(IF(trigger_event IS NOT NULL, 2, 0))
+ (IF(AND(trigger_event IS NOT NULL, trigger_recency_days <= 90), 1, 0))
+ (IF(OR(visited_pricing == TRUE, downloaded_asset == TRUE), 1, 0))
+ (IF(seniority IN ["VP", "C-level", "Director"], 1, 0))

// total
fit_score + intent_score
```

### Score band classification
```clayscript
IF(icp_score >= 8, "Hot",
IF(icp_score >= 5, "Warm",
"Cold"))
```

---

## Sending Gate Formulas

### Strict Sending Gate
```clayscript
AND(
  email IS NOT NULL,
  email_verified IN ["valid", "accept_all_high"],
  icp_band IN ["Hot", "Warm"],
  suppression_check == FALSE,
  seniority IN ["VP", "C-level", "Director", "Senior Manager"],
  NOT(EXISTS(prior_contact_in_last_30_days))
)
```

### Per-step Sending Gate
```clayscript
// step_1
sending_gate_eligible == TRUE
  AND LENGTH(first_line) >= 30
  AND first_line NOT CONTAINS "[no personalization available]"

// step_2 (only after step_1 has been sent)
step_1_eligible == TRUE
  AND step_1_sent_at IS NOT NULL
  AND step_1_replied != TRUE
  AND DAYS_SINCE(step_1_sent_at) >= 3

// linkedin_step
sending_gate_eligible == TRUE
  AND linkedin_url IS NOT NULL
```

---

## URL Construction

### HubSpot deep link
```clayscript
CONCAT("https://app.hubspot.com/contacts/", hubspot_portal_id, "/contact/", hubspot_contact_id)
```

### Salesforce deep link
```clayscript
CONCAT("https://", sfdc_subdomain, ".lightning.force.com/lightning/r/Contact/", sfdc_id, "/view")
```

### LinkedIn search by name + company
```clayscript
CONCAT("https://linkedin.com/search/results/people/?keywords=",
       ENCODE_URL(CONCAT(first_name, " ", last_name, " ", company_name)))
```

### Slack channel deep link
```clayscript
CONCAT("https://", slack_workspace, ".slack.com/archives/", channel_id)
```

---

## Sanity Checks

### Email looks valid (basic regex)
```clayscript
MATCHES_REGEX(email, "^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")
```

### Domain looks valid
```clayscript
AND(
  LENGTH(domain) >= 4,
  CONTAINS(domain, "."),
  NOT(CONTAINS(domain, " "))
)
```

### Phone normalization (US format)
```clayscript
// strip non-numeric, ensure 10 digits
clean = REGEX_REPLACE(phone, "[^0-9]", "")
IF(LENGTH(clean) == 10, CONCAT("+1", clean),
IF(AND(LENGTH(clean) == 11, STARTS_WITH(clean, "1")), CONCAT("+", clean),
NULL))
```

---

## Anti-Patterns to Avoid

❌ `IF(IF(IF(...)))` — nested IFs over 3 levels are unreadable; refactor to multiple columns.
❌ Formulas longer than 10 lines — split into intermediate columns.
❌ Hardcoded IDs in formulas — use lookup tables.
❌ Formula columns burning credits (they shouldn't — if yours does, check it's not actually calling an enrichment).
❌ Same formula in 3 columns — extract to a shared column and reference.
