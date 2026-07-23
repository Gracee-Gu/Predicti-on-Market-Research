from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "stage6"
FINAL_PAPER = ROOT / "paper" / "final"

EXCLUDED_PARTS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
    ".ruff_cache", ".mypy_cache", "stage6_overlay"
}

SECRET_PATTERNS = {
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "generic_secret_assignment": re.compile(
        r"(?i)\b(?:api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]"
    ),
}

def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}

def first_existing(paths: Iterable[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None

def resolve_claim_status() -> tuple[str, str | None]:
    candidates = [
        ROOT / "outputs/stage5/stage5_release_audit.json",
        ROOT / "outputs/stage5/stage5_input_audit.json",
        ROOT / "outputs/stage4/stage4_audit.json",
        ROOT / "outputs/stage4/input_audit.json",
    ]
    allowed = {"confirmatory_ready", "exploratory_only", "blocked"}
    for path in candidates:
        if not path.exists():
            continue
        payload = read_json(path)
        for key in ("claim_status", "stage4_claim_status", "empirical_status"):
            value = payload.get(key)
            if value in allowed:
                return str(value), str(path.relative_to(ROOT))
    manuscript = ROOT / "paper/manuscript_stage5.md"
    if manuscript.exists():
        match = re.search(
            r"(?:Empirical status|Claim status):\s*`?(confirmatory_ready|exploratory_only|blocked)`?",
            manuscript.read_text(encoding="utf-8"),
            flags=re.I,
        )
        if match:
            return match.group(1).lower(), str(manuscript.relative_to(ROOT))
    return "blocked", None

def section_missing(text: str, sections: list[str]) -> list[str]:
    missing = []
    for section in sections:
        pattern = re.compile(rf"(?mi)^##\s+{re.escape(section)}\s*$")
        if not pattern.search(text):
            missing.append(section)
    return missing

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def secret_hits(path: Path) -> list[str]:
    try:
        if path.stat().st_size > 5_000_000:
            return []
        text = path.read_text(encoding="utf-8")
    except Exception:
        return []
    return [name for name, pattern in SECRET_PATTERNS.items() if pattern.search(text)]

def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
