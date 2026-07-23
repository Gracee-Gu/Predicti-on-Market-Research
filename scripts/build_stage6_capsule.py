from __future__ import annotations

import json
import zipfile
from pathlib import Path

from _stage6_common import ROOT, OUT, EXCLUDED_PARTS, secret_hits, sha256_file, write_json

MAX_BYTES = 5_000_000
INCLUDE_ROOTS = ["config", "docs", "scripts", "src", "tests", "paper", "outputs"]
ROOT_FILES = [
    "README_STAGE2.md", "README_STAGE3.md", "README_STAGE4.md",
    "README_STAGE5.md", "README_STAGE6.md", "pyproject.toml",
    "requirements.txt", "stage4_requirements.txt"
]
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".key", ".pem"}
EXCLUDE_NAMES = {".env", ".env.local", "credentials", "credentials.json"}

def eligible(path: Path) -> tuple[bool, str | None]:
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDED_PARTS for part in rel.parts):
        return False, "excluded_directory"
    if path.name in EXCLUDE_NAMES or path.suffix.lower() in EXCLUDE_SUFFIXES:
        return False, "sensitive_extension_or_name"
    if path.stat().st_size > MAX_BYTES:
        return False, "oversized"
    if "raw" in {part.lower() for part in rel.parts} and path.suffix.lower() in {".html", ".txt", ".jsonl"}:
        return False, "possible_raw_copyrighted_content"
    hits = secret_hits(path)
    if hits:
        return False, "secret_pattern:" + ",".join(hits)
    return True, None

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    release = ROOT / "release"
    release.mkdir(parents=True, exist_ok=True)
    capsule = release / "stage6_reproducibility_capsule.zip"

    candidates: list[Path] = []
    for folder in INCLUDE_ROOTS:
        root = ROOT / folder
        if root.exists():
            candidates.extend(p for p in root.rglob("*") if p.is_file())
    for name in ROOT_FILES:
        path = ROOT / name
        if path.exists():
            candidates.append(path)

    records = []
    excluded = []
    unique = sorted(set(candidates), key=lambda p: str(p.relative_to(ROOT)))
    included = []
    for path in unique:
        ok, reason = eligible(path)
        rel = str(path.relative_to(ROOT))
        if ok:
            record = {"path": rel, "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
            records.append(record)
            included.append(path)
        else:
            excluded.append({"path": rel, "reason": reason})

    with zipfile.ZipFile(capsule, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in included:
            archive.write(path, arcname=str(path.relative_to(ROOT)))

    payload = {
        "stage": 6,
        "capsule": str(capsule.relative_to(ROOT)),
        "capsule_sha256": sha256_file(capsule),
        "included_file_count": len(records),
        "excluded_file_count": len(excluded),
        "files": records,
        "excluded": excluded,
    }
    write_json(OUT / "reproducibility_capsule_manifest.json", payload)
    print(json.dumps({k: payload[k] for k in payload if k not in {"files", "excluded"}}, indent=2))

if __name__ == "__main__":
    main()
