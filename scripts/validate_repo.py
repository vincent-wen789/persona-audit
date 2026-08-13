#!/usr/bin/env python3
"""Validate the portable skill bundle and its deterministic test fixtures."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised by CI setup failure
    raise SystemExit("PyYAML is required: python -m pip install PyYAML") from exc


ROOT = Path(__file__).resolve().parents[1]
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED_EVAL_IDS = {
    "engine-happy-path",
    "code-review-negative",
    "lite-landing-page",
    "lite-visual-comprehension",
    "visual-polish-negative",
    "rewrite-only-negative",
    "publish-only-negative",
    "single-pass-evidence-label",
    "prompt-injection-boundary",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def validate_skill() -> None:
    skill_path = ROOT / "SKILL.md"
    match = FRONTMATTER_RE.match(skill_path.read_text(encoding="utf-8"))
    if not match:
        fail("SKILL.md must start with YAML frontmatter")

    try:
        metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        fail(f"SKILL.md frontmatter is invalid YAML: {exc}")

    if not isinstance(metadata, dict):
        fail("SKILL.md frontmatter must be a YAML mapping")
    if set(metadata) != {"name", "description"}:
        fail("SKILL.md frontmatter must contain only name and description")

    name = metadata["name"]
    description = metadata["description"]
    if not isinstance(name, str) or not SKILL_NAME_RE.fullmatch(name):
        fail("skill name must use lowercase letters, numbers, and single hyphens")
    if name != ROOT.name:
        fail(f"skill name {name!r} must match directory name {ROOT.name!r}")
    if not isinstance(description, str) or not description.startswith("Use when "):
        fail("skill description must start with 'Use when '")
    if len(description) > 1024:
        fail("skill description must be at most 1024 characters")


def validate_openai_metadata() -> None:
    metadata_path = ROOT / "agents" / "openai.yaml"
    if not metadata_path.is_file():
        fail("agents/openai.yaml is required for Codex UI metadata")

    metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
    interface = metadata.get("interface") if isinstance(metadata, dict) else None
    if not isinstance(interface, dict):
        fail("agents/openai.yaml must define interface metadata")
    for key in ("display_name", "short_description", "default_prompt"):
        if not isinstance(interface.get(key), str) or not interface[key].strip():
            fail(f"agents/openai.yaml interface.{key} must be a non-empty string")
    if "$persona-audit" not in interface["default_prompt"]:
        fail("agents/openai.yaml default_prompt must mention $persona-audit")
    policy = metadata.get("policy")
    if not isinstance(policy, dict) or not isinstance(
        policy.get("allow_implicit_invocation"), bool
    ):
        fail("agents/openai.yaml policy.allow_implicit_invocation must be boolean")


def validate_eval_cases() -> None:
    data = json.loads((ROOT / "test-prompts.json").read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        fail("test-prompts.json must use schema_version 1")

    contract = data.get("global_contract")
    if not isinstance(contract, dict) or contract.get("default_execution") != "report_only":
        fail("global_contract.default_execution must be report_only")
    for key in ("requires_explicit_authorization", "never"):
        if not isinstance(contract.get(key), list) or not contract[key]:
            fail(f"global_contract.{key} must be a non-empty list")

    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        fail("test-prompts.json cases must be a non-empty list")
    ids: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            fail("each eval case must be an object")
        required = {"id", "prompt", "should_trigger", "expected_mode", "required", "forbidden"}
        if set(case) != required:
            fail(f"eval case keys must be exactly {sorted(required)}")
        if not isinstance(case["id"], str) or not case["id"]:
            fail("eval case id must be a non-empty string")
        if case["id"] in ids:
            fail(f"duplicate eval case id: {case['id']}")
        ids.add(case["id"])
        if not isinstance(case["prompt"], str) or not case["prompt"]:
            fail(f"{case['id']}: prompt must be a non-empty string")
        if not isinstance(case["should_trigger"], bool):
            fail(f"{case['id']}: should_trigger must be boolean")
        if case["expected_mode"] not in {"lite", "engine", None}:
            fail(f"{case['id']}: expected_mode must be lite, engine, or null")
        for key in ("required", "forbidden"):
            if (
                not isinstance(case[key], list)
                or not case[key]
                or not all(isinstance(item, str) and item for item in case[key])
            ):
                fail(f"{case['id']}: {key} must be a non-empty list of strings")
    missing_ids = REQUIRED_EVAL_IDS - ids
    if missing_ids:
        fail(f"test-prompts.json is missing required cases: {sorted(missing_ids)}")


def validate_behavior_contract() -> None:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    required_fragments = (
        "**只审计、只报告。**",
        "**不编事实。**",
        "**隔离冷读**",
        "**单次多视角模拟**",
        "提示词不是安全沙箱",
        "不编辑文件，不改产品，不 commit，不发布或部署",
    )
    missing = [fragment for fragment in required_fragments if fragment not in skill]
    if missing:
        fail(f"SKILL.md is missing behavior-contract fragments: {missing}")


def validate_relative_links() -> None:
    missing: list[str] = []
    for markdown_path in ROOT.rglob("*.md"):
        if ".git" in markdown_path.parts:
            continue
        text = markdown_path.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK_RE.findall(text):
            target = unquote(raw_target.strip().split("#", 1)[0])
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if not (markdown_path.parent / target).exists():
                missing.append(f"{markdown_path.relative_to(ROOT)} -> {raw_target}")
    if missing:
        fail("missing relative link targets:\n" + "\n".join(missing))


def main() -> int:
    checks = (
        validate_skill,
        validate_openai_metadata,
        validate_eval_cases,
        validate_behavior_contract,
        validate_relative_links,
    )
    for check in checks:
        try:
            check()
        except (AssertionError, json.JSONDecodeError, yaml.YAMLError) as exc:
            print(f"FAIL {check.__name__}: {exc}", file=sys.stderr)
            return 1
        print(f"PASS {check.__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
