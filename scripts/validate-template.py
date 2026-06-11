#!/usr/bin/env python3
"""
validate-template.py — schema + anonymization checks for clay-workbench templates.

Stdlib only. No pip dependencies.

Usage:
    python3 scripts/validate-template.py                    # check all templates
    python3 scripts/validate-template.py path/to/<slug>/    # check one template

Schema reference: skills/clay-template-library/SKILL.md → "template.json Schema"

Exit codes:
    0  = no errors (warnings allowed)
    1  = one or more schema/structural errors
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable

# ---------------------------------------------------------------------------
# Schema definition (mirrors skills/clay-template-library/SKILL.md)
# ---------------------------------------------------------------------------

REQUIRED_TOP_LEVEL_KEYS = [
    "schema_version",
    "template",
    "intake_defaults",
    "columns",
    "actions",
    "verification_checklist",
]

REQUIRED_TEMPLATE_KEYS = [
    "slug",
    "name",
    "version",
    "description",
    "use_case",
    "motion",
]

REQUIRED_COLUMN_KEYS = [
    "name",
    "type",
    "source",
    "cost_credits",
    "depends_on",
    "run_condition",
    "config",
    "formula_text",
    "claygent_prompt",
    "notes",
]

# ---------------------------------------------------------------------------
# Anonymization denylist + patterns
# ---------------------------------------------------------------------------

# Known client / brand names that should never appear in a community template.
# Case-insensitive whole-word match. Add to this list as the library grows.
CLIENT_DENYLIST = [
    "Obin",
    "Vantage",
    "Dodge",
    "CurveDental",
    "Curve Dental",
    "Avarra",
    "Narvar",
    "KiwiData",
    "Coefficient",
    "Apoorv",
    "Lak Lakshmanan",
    "Brandon Redlinger",
    "Stack and Scale",
    "Stack & Scale",
]

# Email-domain patterns that are safe to ignore.
SAFE_EMAIL_DOMAINS = {
    "example.com",
    "example.org",
    "example.net",
    "test.com",
    "acme.com",
    "company.com",
    "yourcompany.com",
}

# Regex: hardcoded email (we'll filter placeholders + safe domains afterwards).
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")

# Regex: hardcoded Slack channel reference like #channel-name (not in a {{...}} placeholder).
SLACK_CHANNEL_RE = re.compile(r"(?<!\w)#([a-z0-9][a-z0-9_\-]{2,})\b")

# Regex: UUID-looking IDs (Hubspot/SF/Slack IDs frequently look like this).
UUID_RE = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)

# Regex: Salesforce-style 15/18-char object IDs (start with 3 letters then alphanum).
SF_ID_RE = re.compile(r"\b00[0-9A-Za-z]{13}(?:[0-9A-Za-z]{3})?\b")

# Regex: Hubspot numeric list IDs that look real (long runs of digits NOT in a placeholder).
LONG_NUM_RE = re.compile(r"(?<!\d)(\d{9,})(?!\d)")

# Regex: a {{PLACEHOLDER}} token — used to skip false positives.
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")

# ---------------------------------------------------------------------------
# Result aggregation
# ---------------------------------------------------------------------------

class Result:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def merge(self, other: "Result") -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)

# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

def validate_schema(slug: str, data: dict[str, Any], result: Result) -> None:
    """Validate top-level + nested schema. Errors = exit 1."""
    # Top-level keys
    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in data:
            result.error(f"[{slug}] missing required top-level key: '{key}'")

    # template block
    template = data.get("template")
    if not isinstance(template, dict):
        result.error(f"[{slug}] 'template' must be an object")
    else:
        for key in REQUIRED_TEMPLATE_KEYS:
            if key not in template:
                result.error(f"[{slug}] template.{key} is required")
        # slug must match dir name
        if template.get("slug") and template["slug"] != slug:
            result.error(
                f"[{slug}] template.slug='{template['slug']}' does not match "
                f"directory name '{slug}'"
            )

    # columns: required list, each item has all required keys
    columns = data.get("columns")
    if not isinstance(columns, list):
        result.error(f"[{slug}] 'columns' must be a list")
    else:
        if len(columns) == 0:
            result.error(f"[{slug}] 'columns' is empty — every template needs at least 1 column")
        for i, col in enumerate(columns):
            if not isinstance(col, dict):
                result.error(f"[{slug}] columns[{i}] must be an object")
                continue
            for key in REQUIRED_COLUMN_KEYS:
                if key not in col:
                    name = col.get("name", f"index {i}")
                    result.error(f"[{slug}] column '{name}' missing required key: '{key}'")

    # actions: must be a list (can be empty for read-only / enrichment-only templates)
    actions = data.get("actions")
    if not isinstance(actions, list):
        result.error(f"[{slug}] 'actions' must be a list (can be empty)")

    # intake_defaults: must be an object
    intake = data.get("intake_defaults")
    if not isinstance(intake, dict):
        result.error(f"[{slug}] 'intake_defaults' must be an object")

    # verification_checklist: must be a list
    checklist = data.get("verification_checklist")
    if not isinstance(checklist, list):
        result.error(f"[{slug}] 'verification_checklist' must be a list")

# ---------------------------------------------------------------------------
# Anonymization scanning
# ---------------------------------------------------------------------------

def scan_text_lines(file_label: str, text: str, result: Result) -> None:
    """Scan a file's text for likely anonymization leaks. All findings are warnings."""
    for lineno, line in enumerate(text.splitlines(), start=1):
        # Strip placeholders so they don't trigger sub-pattern matches.
        scrubbed = PLACEHOLDER_RE.sub("", line)

        # 1. Client / brand denylist (case-insensitive whole word)
        for name in CLIENT_DENYLIST:
            pattern = re.compile(r"\b" + re.escape(name) + r"\b", re.IGNORECASE)
            if pattern.search(scrubbed):
                result.warn(
                    f"{file_label}:{lineno} potential client name leak: "
                    f"'{name}' → '{line.strip()[:160]}'"
                )

        # 2. Hardcoded email domains
        for match in EMAIL_RE.finditer(scrubbed):
            domain = match.group(1).lower()
            if domain in SAFE_EMAIL_DOMAINS:
                continue
            if domain.endswith(".test") or domain.endswith(".example"):
                continue
            result.warn(
                f"{file_label}:{lineno} hardcoded email domain: "
                f"'{match.group(0)}' (use {{{{PLACEHOLDER}}}} or example.com)"
            )

        # 3. Slack channel names (skip if it's actually a hex color or anchor)
        for match in SLACK_CHANNEL_RE.finditer(scrubbed):
            channel = match.group(0)
            # Skip if it looks like a hex color (#abc123 with all hex chars + 6 length).
            inner = match.group(1)
            if len(inner) in (3, 6, 8) and re.fullmatch(r"[0-9a-fA-F]+", inner):
                continue
            # Skip common markdown anchor/heading words.
            if inner in {"general", "random", "channel"}:
                continue
            result.warn(
                f"{file_label}:{lineno} hardcoded Slack channel: "
                f"'{channel}' (use {{{{SLACK_CHANNEL}}}})"
            )

        # 4. UUIDs
        for match in UUID_RE.finditer(scrubbed):
            result.warn(
                f"{file_label}:{lineno} UUID-like ID: '{match.group(0)}' "
                f"(use {{{{CRM_OBJECT_ID}}}})"
            )

        # 5. Salesforce-style IDs
        for match in SF_ID_RE.finditer(scrubbed):
            result.warn(
                f"{file_label}:{lineno} Salesforce-style ID: '{match.group(0)}' "
                f"(use {{{{CRM_OBJECT_ID}}}})"
            )

        # 6. Long numeric IDs (likely Hubspot list IDs etc.)
        for match in LONG_NUM_RE.finditer(scrubbed):
            num = match.group(0)
            # Skip obvious version / year / cost numbers; only flag 9+ digit runs.
            if len(num) >= 9:
                result.warn(
                    f"{file_label}:{lineno} long numeric ID: '{num}' "
                    f"(if this is a CRM list/object ID, use {{{{CRM_OBJECT_ID}}}})"
                )

# ---------------------------------------------------------------------------
# Per-template orchestration
# ---------------------------------------------------------------------------

def validate_template_dir(dir_path: Path) -> Result:
    result = Result()
    slug = dir_path.name

    template_json = dir_path / "template.json"
    readme_md = dir_path / "README.md"

    if not template_json.exists():
        result.error(f"[{slug}] missing template.json")
    if not readme_md.exists():
        result.error(f"[{slug}] missing README.md")

    if template_json.exists():
        try:
            raw = template_json.read_text(encoding="utf-8")
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            result.error(f"[{slug}] template.json is not valid JSON: {exc}")
        else:
            validate_schema(slug, data, result)
            scan_text_lines(f"{slug}/template.json", raw, result)

    if readme_md.exists():
        readme_text = readme_md.read_text(encoding="utf-8")
        scan_text_lines(f"{slug}/README.md", readme_text, result)

    return result

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def find_repo_root(start: Path) -> Path:
    """Walk up to find the repo root (contains templates/library/INDEX.md)."""
    cur = start.resolve()
    for parent in [cur, *cur.parents]:
        if (parent / "templates" / "library" / "INDEX.md").exists():
            return parent
    # Fall back to script's parent's parent.
    return Path(__file__).resolve().parent.parent

def discover_templates(library: Path) -> list[Path]:
    return sorted(
        d for d in library.iterdir()
        if d.is_dir() and (d / "template.json").exists()
    )

def main(argv: list[str]) -> int:
    repo_root = find_repo_root(Path.cwd())
    library = repo_root / "templates" / "library"

    if len(argv) > 1:
        target = Path(argv[1]).resolve()
        if not target.exists() or not target.is_dir():
            print(f"ERROR: '{target}' is not a directory")
            return 1
        targets = [target]
    else:
        if not library.exists():
            print(f"ERROR: templates/library/ not found at {library}")
            return 1
        targets = discover_templates(library)

    if not targets:
        print("No templates found.")
        return 0

    overall = Result()
    for d in targets:
        per = validate_template_dir(d)
        overall.merge(per)

    # Print warnings first, errors second so errors are last thing on screen.
    for w in overall.warnings:
        print(f"WARNING: {w}")
    for e in overall.errors:
        print(f"ERROR: {e}")

    print()
    print(
        f"{len(targets)} templates checked, "
        f"{len(overall.errors)} errors, "
        f"{len(overall.warnings)} warnings"
    )

    return 1 if overall.errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
