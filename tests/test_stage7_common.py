import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts" / "_stage7_common.py"
spec = importlib.util.spec_from_file_location("stage7_common", PATH)
m = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(m)

def test_normalize_source():
    assert m.normalize_source("platform-owned") == "platform_owned"
    assert m.normalize_source("Independent Media") == "independent_media"
    assert m.normalize_source("regulatory/critical") == "regulatory_critical"

def test_nonempty():
    assert m.nonempty("x")
    assert not m.nonempty("")
    assert not m.nonempty("nan")

def test_media_record_key_prefers_url():
    row = {"url": "https://example.com/a", "source_id": "abc", "text_sha256": "hash"}
    assert m.media_record_key(row) == ("url", "https://example.com/a")

def test_dedupe_media_records_keeps_richer_row():
    rows = [
        {"url": "https://example.com/a", "source_type": "platform_owned"},
        {
            "url": "https://example.com/a",
            "source_type": "platform_owned",
            "published_at": "2026-07-23T00:00:00Z",
            "text_sha256": "abc",
        },
    ]
    deduped = m.dedupe_media_records(rows)
    assert len(deduped) == 1
    assert deduped[0]["text_sha256"] == "abc"
