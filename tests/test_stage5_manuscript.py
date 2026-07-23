from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_required_section_names_are_documented():
    text=(ROOT/'config/stage5.yaml').read_text()
    for s in ['Abstract','Introduction','Data and Methods','Results','Limitations','Reproducibility Statement']:
        assert s in text
