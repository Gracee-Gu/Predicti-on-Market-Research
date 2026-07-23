import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from collect_publication_time_matches import candlestick_price, source_quoted_price
from match_market_mentions import build_catalog, match_media_row, resolve_market_from_event_payload
from pmresearch.collectors.media import MediaCollector
from pmresearch.market_utils import (
    choose_polymarket_yes_token,
    extract_kalshi_market_ticker,
    extract_polymarket_slug,
)
from pmresearch.snapshots import summarize_kalshi_orderbook, summarize_polymarket_orderbook


class InlineTextClient:
    def __init__(self, html: str):
        self.html = html

    def get_text(self, url):
        return self.html, "text/html"


def test_media_collector_extracts_market_links_and_candidate_tickers():
    html = """
    <html><head><title>Story</title></head>
    <body>
      <article>
        <a href="https://kalshi.com/markets/KXTEST-26">Will it happen?</a>
        <a href="/relative">Ignore me</a>
      </article>
    </body></html>
    """
    row = MediaCollector(
        InlineTextClient(html),
        store_full_text=False,
        excerpt_character_limit=120,
    ).collect_one(
        {
            "source_id": "seed_1",
            "url": "https://example.com/story",
            "published_at": "2026-07-01",
            "source_type": "platform_owned",
        }
    )
    assert row["market_links"] == [
        {"url": "https://kalshi.com/markets/KXTEST-26", "label": "Will it happen?"}
    ]
    assert row["candidate_tickers"] == ["KXTEST-26"]


def test_choose_polymarket_yes_token_falls_back_to_first_token():
    assert choose_polymarket_yes_token(
        {
            "_parsed_outcomes": ["No", "Yes"],
            "_parsed_clob_token_ids": ["no-token", "yes-token"],
        }
    ) == "yes-token"
    assert choose_polymarket_yes_token({"_parsed_clob_token_ids": ["first"]}) == "first"


def test_extract_polymarket_slug_uses_last_path_component():
    assert (
        extract_polymarket_slug("https://polymarket.com/event/example-market-slug")
        == "example-market-slug"
    )
    assert (
        extract_kalshi_market_ticker("https://kalshi.com/markets/kxpresperson/pres-person/kxpresperson-28")
        == "KXPRESPERSON-28"
    )
    assert (
        extract_kalshi_market_ticker(
            "https://kalshi.com/markets/kxworldcuphalftime/who-will-perform-at-event/"
            "kxworldcuphalftime-26?op_market_ticker=KXWORLDCUPHALFTIME-26-POS"
        )
        == "KXWORLDCUPHALFTIME-26-POS"
    )


def test_match_media_row_finds_identifier_and_exact_title(tmp_path: Path):
    kalshi_path = tmp_path / "kalshi.jsonl"
    kalshi_path.write_text(
        (
            '{"ticker":"KXTEST-26","title":"Will it rain tomorrow?",'
            '"event_ticker":"KXTEST","series_ticker":"KXRAIN","status":"active"}\n'
        ),
        encoding="utf-8",
    )
    polymarket_path = tmp_path / "polymarket.jsonl"
    polymarket_path.write_text(
        (
            '{"id":"123","question":"Will Bitcoin top $200k by year end?",'
            '"slug":"bitcoin-200k-year-end","closed":false,'
            '"_parsed_outcomes":["Yes","No"],'
            '"_parsed_clob_token_ids":["yes-token","no-token"]}\n'
        ),
        encoding="utf-8",
    )
    catalog = build_catalog([kalshi_path], [polymarket_path])
    source = {
        "source_id": "seed_1",
        "source_name": "Example",
        "source_type": "independent_media",
        "formal_partnership": "0",
        "url": "https://example.com/story",
        "page_title": "Markets update",
        "excerpt": (
            "Kalshi contract KXTEST-26 moved sharply. "
            "Meanwhile, Will Bitcoin top $200k by year end? was heavily discussed."
        ),
        "notes": "",
        "candidate_tickers": [],
        "market_links": [],
        "published_at_resolved": "2026-07-01T12:00:00Z",
    }
    mentions = match_media_row(source, catalog, max_title_matches=10)
    assert {(row["platform"], row["market_id"], row["match_method"]) for row in mentions} == {
        ("kalshi", "KXTEST-26", "exact_identifier"),
        ("polymarket", "123", "exact_title"),
    }
    kalshi_mention = next(row for row in mentions if row["platform"] == "kalshi")
    assert kalshi_mention["event_ticker"] == "KXTEST"
    assert kalshi_mention["series_ticker"] == "KXRAIN"


def test_match_media_row_keeps_exact_identifier_without_catalog_row():
    source = {
        "source_id": "seed_2",
        "source_name": "Kalshi News",
        "source_type": "platform_owned",
        "formal_partnership": "0",
        "url": "https://news.kalshi.com/example",
        "page_title": "A linked market",
        "excerpt": "",
        "notes": "",
        "candidate_tickers": [],
        "market_links": [
            {
                "url": "https://kalshi.com/markets/kxpresperson/pres-person/kxpresperson-28",
                "label": "Will a specific candidate win the 2028 U.S. presidential election?",
            }
        ],
        "published_at_resolved": "2026-07-01T12:00:00Z",
    }
    mentions = match_media_row(source, [], max_title_matches=10)
    assert len(mentions) == 1
    assert mentions[0]["market_id"] == "KXPRESPERSON-28"
    assert mentions[0]["match_method"] == "exact_identifier"


def test_resolve_market_from_event_payload_uses_fragment_and_single_market():
    payload = {
        "event": {"series_ticker": "KXTEST"},
        "markets": [
            {
                "ticker": "KXTEST-26",
                "event_ticker": "KXTEST",
                "title": "Will it happen?",
                "yes_sub_title": "Yes",
                "no_sub_title": "No",
            }
        ],
    }
    resolved = resolve_market_from_event_payload(payload, "Current odds", "")
    assert resolved["ticker"] == "KXTEST-26"

    payload_many = {
        "markets": [
            {"ticker": "KXABC-26", "title": "Will Alice win?", "yes_sub_title": "Alice"},
            {"ticker": "KXDEF-26", "title": "Will Bob win?", "yes_sub_title": "Bob"},
        ]
    }
    resolved_fragment = resolve_market_from_event_payload(payload_many, "Current odds", "kxdef-26")
    assert resolved_fragment["ticker"] == "KXDEF-26"


def test_orderbook_summaries_compute_key_metrics():
    kalshi_summary = summarize_kalshi_orderbook(
        {
            "orderbook_fp": {
                "yes_dollars": [["0.40", "100.00"], ["0.36", "50.00"]],
                "no_dollars": [["0.55", "80.00"], ["0.50", "20.00"]],
            }
        }
    )
    assert kalshi_summary["bid"] == 0.40
    assert round(kalshi_summary["ask"], 2) == 0.45
    assert kalshi_summary["depth_band"] == 250.0

    polymarket_summary = summarize_polymarket_orderbook(
        {
            "bids": [{"price": "0.48", "size": "100"}],
            "asks": [{"price": "0.52", "size": "80"}],
        }
    )
    assert polymarket_summary["bid"] == 0.48
    assert polymarket_summary["ask"] == 0.52
    assert polymarket_summary["depth_band"] == 180.0


def test_candlestick_price_supports_historical_price_shape():
    assert (
        candlestick_price(
            {
                "price": {
                    "close": "0.5600",
                    "mean": "0.5700",
                }
            }
        )
        == "0.5700"
    )


def test_source_quoted_price_normalizes_percent_to_probability():
    assert source_quoted_price({"quoted_price": "65", "quoted_price_unit": "%"}) == "0.6500"
