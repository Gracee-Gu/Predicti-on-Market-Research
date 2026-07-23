import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from collect_kalshi_historical_batch import chunked, load_tickers
from export_kalshi_tickers import choose_tickers, export_tickers


def test_choose_tickers_prefers_match_fields():
    row = {
        "matched_market_id": "KXTEST-26",
        "market_id": "KXOTHER-26",
        "ticker": "KXIGNORED-26",
    }
    assert choose_tickers(row, ["matched_market_id", "market_id", "ticker"]) == ["KXTEST-26"]


def test_export_tickers_filters_platform_and_dedupes(tmp_path: Path):
    csv_path = tmp_path / "inventory.csv"
    csv_path.write_text(
        "\n".join(
            [
                "platform,matched_market_id,market_id,ticker",
                "kalshi,KXTEST-26,,",
                "polymarket,PM-1,,",
                "kalshi,KXTEST-26,,",
                "kalshi,,KXALT-26,",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    output = tmp_path / "tickers.txt"
    scanned, exported = export_tickers(
        inputs=[csv_path],
        output=output,
        ticker_fields=["matched_market_id", "market_id", "ticker"],
        platform_field="platform",
        platform_value="kalshi",
    )
    assert scanned == 4
    assert exported == 2
    assert output.read_text(encoding="utf-8").splitlines() == ["KXTEST-26", "KXALT-26"]


def test_load_tickers_dedupes_and_strips(tmp_path: Path):
    path = tmp_path / "tickers.txt"
    path.write_text("KXTEST-26\n\nKXTEST2-26\nKXTEST-26\n", encoding="utf-8")
    assert load_tickers(path) == ["KXTEST-26", "KXTEST2-26"]


def test_chunked_splits_values():
    assert list(chunked(["a", "b", "c", "d", "e"], 2)) == [["a", "b"], ["c", "d"], ["e"]]
