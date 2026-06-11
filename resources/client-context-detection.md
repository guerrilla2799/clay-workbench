# Client Context Detection

When the user mentions a client by name in a Clay workbook request, route to the matching messaging / context skill to pull ICP, voice, and positioning before composing.

This keeps `clay-workbench` client-agnostic at its core while still producing on-brand outbound copy when context is available.

---

## Detection Rules

Scan the user's prompt for these tokens (case-insensitive):

| If prompt mentions... | Then load before composing |
|----------------------|---------------------------|
| "obin", "Obin AI", "Apoorv", "Lak", "Foreman Bank" | `obin-messaging` skill — pull positioning, ICP, voice |
| "vantage", "Amy", "Brooke McKim", "Decagon" | `vantage-messaging` + `vantage-outbound-program` skills |
| "dodge", "Dodge ENT", "ABM cadence" | `dodge-abm-cadence` skill |
| "curve", "CurveDental", "Flex", "Dental HP" | Reference `~/Obsidian/01-Clients/CurveDental/` context |
| "kiwi", "KiwiData" | Reference `~/Obsidian/01-Clients/KiwiData/` |
| "narvar" | Reference `~/Obsidian/01-Clients/Narvar/` |
| "stack and scale", "Stack & Scale", "newsletter" | Brandon's voice — load `~/Obsidian/03-Voice-and-Style/brandon-voice-style-guide.md` |
| No client mentioned | Stay generic — use universal frameworks |

---

## Routing Logic (apply in sub-skills that generate copy)

```
1. Scan prompt for client tokens above.
2. If matched:
   a. State: "Detected client context: {ClientName}. Loading {skill_name} for ICP + voice."
   b. Load the matching skill (read its SKILL.md or invoke it).
   c. Use that skill's ICP definition for gates, persona, positioning hooks.
   d. Use that skill's voice for AI prompts that generate copy.
3. If no client matched:
   a. Use universal positioning framework (April Dunford 5-step lite).
   b. Use universal outbound voice (direct, problem-focused, ICP-tailored).
4. If ambiguous (multiple clients in same prompt):
   a. Ask: "I see both X and Y mentioned — which is this workbook for?"
```

---

## What to Pull from Each Client Skill

When loading a client skill, extract these specific elements:

| Element | Used For |
|---------|----------|
| ICP definition | Gate column logic, qualification filter |
| Persona / titles | Contact-finding filter |
| Trigger events | Signal-based row qualification |
| Value propositions | Personalized first line, subject line |
| Differentiators | "Why us" line in outbound |
| Disqualifiers | Negative gate logic |
| Voice / tone | All AI-generated copy |
| Suppression rules | Customer list, prospect list, opt-outs |

---

## Universal Defaults (when no client matched)

If the prompt has no client context, use these defaults:

### Universal Persona Default
Senior decision-maker in the named function:
- VP / Director / Head of [function]
- Min 50 employees (filters out solopreneurs)
- US/CA/UK/AU geos
- Trigger-event optional but preferred

### Universal Voice
- Direct, no fluff
- 1-sentence first line referencing the trigger or observation
- 1-sentence value claim with specificity
- Concrete next step ("worth a 15-min look?")

### Universal Disqualifiers
- Current customers (suppression list)
- Prospects in last 30 days (cadence cooldown)
- Bounced emails in last 90 days
- Opt-out / unsubscribe flagged

---

## Why This Matters

Generic outbound copy from a generic Clay workbook is worse than not doing outbound at all — it damages domain reputation and trains the audience to ignore brand names. By detecting client context and routing to a voice-aware skill, every output stays on-brand.

This is the "Layer on top — Clay skill is the engine" architecture from the design decisions.
