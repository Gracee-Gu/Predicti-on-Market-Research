import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "_stage6_common.py"

spec = importlib.util.spec_from_file_location("stage6_common", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(module)

def test_sha256_file_is_stable(tmp_path):
    path = tmp_path / "x.txt"
    path.write_text("abc", encoding="utf-8")
    assert module.sha256_file(path) == module.sha256_file(path)
    assert len(module.sha256_file(path)) == 64

def test_section_missing():
    text = "# Title\n\n## Abstract\nx\n\n## Introduction\ny\n"
    assert module.section_missing(text, ["Abstract", "Introduction"]) == []
    assert module.section_missing(text, ["Results"]) == ["Results"]

def test_secret_detection(tmp_path):
    path = tmp_path / "secret.txt"
    path.write_text("-----BEGIN PRIVATE KEY-----", encoding="utf-8")
    assert "private_key" in module.secret_hits(path)
