import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "scripts" / "audit_stage5_release.py"
    spec = importlib.util.spec_from_file_location("audit_stage5_release", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_find_secret_hits_skips_virtualenv(tmp_path):
    mod = load_module()
    token = "AKIA" + ("A" * 16)
    project_file = tmp_path / "notes.txt"
    project_file.write_text(f"token {token}\n", encoding="utf-8")
    venv_file = tmp_path / ".venv" / "lib" / "pkg.py"
    venv_file.parent.mkdir(parents=True)
    venv_file.write_text(f"token {token}\n", encoding="utf-8")

    hits = mod.find_secret_hits(tmp_path)

    assert hits == ["notes.txt"]
