<!-- See CONTRIBUTING.md for the full workflow. -->

## Type of change

- [ ] New template (`templates/library/<slug>/`)
- [ ] Sub-skill improvement
- [ ] Bug fix
- [ ] Documentation

## Description

<!-- One paragraph: what does this PR do and why. Link related issue if any. -->

Related issue: #

## For template contributions — self-attestation

- [ ] No client / company names in `template.json` or `README.md`
- [ ] No hardcoded email domains (used `{{PLACEHOLDERS}}` or `example.com`)
- [ ] No Slack channel names (used `{{SLACK_CHANNEL}}`)
- [ ] No CRM object / list / record IDs (used `{{CRM_OBJECT_ID}}` etc.)
- [ ] No sender names in outbound copy (used `{{SENDER_NAME}}`)
- [ ] No specific competitor names in Claygent prompts (used `{{COMPETITORS}}`)
- [ ] No proprietary scoring weights or suppression lists
- [ ] Ran `python3 scripts/validate-template.py` — zero errors
- [ ] Updated `templates/library/INDEX.md` (main table + stage section)
- [ ] `README.md` placeholder map filled in with realistic examples

If the validator surfaced warnings, list them here and explain why each is safe to merge:

<!-- e.g. WARNING: `#example-channel` is inside the placeholder table as an Example value, not a hardcoded channel. -->

## Testing

<!-- How did you verify this works? For templates: did you instantiate it into a fresh workbook? For sub-skill changes: which scenarios did you walk through? -->

## Breaking change?

- [ ] Yes — explain below
- [ ] No

<!-- If yes, describe what breaks and the migration path. Changes to the template.json schema, Global Rules, or routing semantics are breaking. -->
