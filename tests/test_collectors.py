from pathlib import Path

from pmresearch.collectors.kalshi import KalshiCollector
from pmresearch.collectors.polymarket import PolymarketCollector, parse_jsonish_list
from pmresearch.collectors.media import MediaCollector


FIXTURES = Path(__file__).parent / "fixtures"


class FakeJsonClient:
    def __init__(self, payloads):
        self.payloads = list(payloads)
        self.calls = []

    def get_json(self, url, params=None):
        self.calls.append((url, dict(params or {})))
        return self.payloads.pop(0)


class FakeTextClient:
    def get_text(self, url):
        return (FIXTURES / "media.html").read_text(encoding="utf-8"), "text/html"


class FailingTextClient:
    def get_text(self, url):
        raise RuntimeError("boom")


def test_kalshi_pagination():
    import json
    p1 = json.loads((FIXTURES / "kalshi_markets_page1.json").read_text())
    p2 = json.loads((FIXTURES / "kalshi_markets_page2.json").read_text())
    fake = FakeJsonClient([p1, p2])
    rows = list(KalshiCollector(fake, page_limit=100).markets(status="open"))
    assert [row["ticker"] for row in rows] == ["KXTEST-26", "KXTEST2-26"]
    assert fake.calls[1][1]["cursor"] == "next"


def test_kalshi_historical_market_filters():
    fake = FakeJsonClient([{"markets": [{"ticker": "KXTEST-26"}], "cursor": ""}])
    rows = list(KalshiCollector(fake).markets(historical=True, tickers=["KXTEST-26", "KXTEST2-26"]))
    assert [row["ticker"] for row in rows] == ["KXTEST-26"]
    assert fake.calls[0][1]["tickers"] == "KXTEST-26,KXTEST2-26"


def test_kalshi_historical_filters_are_mutually_exclusive():
    fake = FakeJsonClient([])
    try:
        list(
            KalshiCollector(fake).markets(
                historical=True,
                tickers=["KXTEST-26"],
                event_ticker="KXEVENT-26",
            )
        )
    except ValueError as exc:
        assert "mutually exclusive" in str(exc)
    else:
        raise AssertionError("Expected mutually exclusive historical filters to raise")


def test_kalshi_max_pages_stops_pagination():
    fake = FakeJsonClient(
        [
            {"markets": [{"ticker": "KXTEST-26"}], "cursor": "next"},
            {"markets": [{"ticker": "KXTEST2-26"}], "cursor": ""},
        ]
    )
    rows = list(KalshiCollector(fake).markets(status="open", max_pages=1))
    assert [row["ticker"] for row in rows] == ["KXTEST-26"]
    assert len(fake.calls) == 1


def test_polymarket_jsonish_fields():
    assert parse_jsonish_list('["a", "b"]') == ["a", "b"]
    fake = FakeJsonClient([[{
        "id": "1", "clobTokenIds": '["yes","no"]',
        "outcomes": '["Yes","No"]', "outcomePrices": '["0.7","0.3"]'
    }]])
    row = list(PolymarketCollector(fake).markets())[0]
    assert row["_parsed_clob_token_ids"] == ["yes", "no"]


def test_media_copyright_safe_default():
    collector = MediaCollector(FakeTextClient(), store_full_text=False, excerpt_character_limit=30)
    row = collector.collect_one({
        "source_id": "x", "url": "https://example.com/a",
        "published_at": "", "source_type": "independent_media"
    })
    assert row["page_title"] == "Prediction market article"
    assert row["published_at_resolved"] == "2026-07-01T12:00:00Z"
    assert "full_text" not in row
    assert len(row["excerpt"]) <= 30
    assert row["text_sha256"]


def test_media_collect_one_safe_captures_fetch_errors():
    collector = MediaCollector(FailingTextClient(), store_full_text=False, excerpt_character_limit=30)
    row = collector.collect_one_safe(
        {
            "source_id": "x",
            "url": "https://example.com/a",
            "published_at": "2026-07-01",
            "source_type": "independent_media",
        }
    )
    assert row["fetch_ok"] is False
    assert row["fetch_error"] == "boom"
    assert row["published_at_resolved"] == "2026-07-01"
