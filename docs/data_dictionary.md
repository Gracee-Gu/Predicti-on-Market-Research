# Stage 2 Data Dictionary

## `market_raw`

| Field | Meaning |
|---|---|
| `platform` | `kalshi` or `polymarket` |
| `record_id` | Platform-native market identifier |
| `event_id` | Parent event identifier where available |
| `series_id` | Parent series identifier where available |
| `title` | Market question or title |
| `description` | Contract description |
| `rules` | Resolution rules or source |
| `category_raw` | Platform-native category |
| `status` | Active/open/closed/settled |
| `start_time` | Market opening or start time |
| `end_time` | Close/end time |
| `settlement_time` | Settlement timestamp |
| `outcome_token_ids` | Polymarket CLOB token IDs |
| `raw_payload` | Original API response, local-only |

## `media_source`

| Field | Meaning |
|---|---|
| `source_id` | Stable research identifier |
| `source_name` | Publisher or platform |
| `source_type` | Four-level Stage 1 source type |
| `formal_partnership` | 1, 0, or unknown |
| `partnership_evidence_url` | Primary dated evidence |
| `url` | Source URL |
| `published_at` | Seed publication time |
| `published_at_resolved` | Metadata-resolved time |
| `article_genre` | News, analysis, opinion, explainer, press release, help page, transcript |
| `market_category` | Harmonized category |
| `text_sha256` | Hash of extracted text |
| `text_length_chars` | Extraction length |
| `excerpt` | Short audit excerpt |
| `full_text` | Local-only; absent by default |

## `market_mention`

| Field | Meaning |
|---|---|
| `mention_id` | Stable document-market identifier |
| `source_id` | Linked media source |
| `platform` | Mentioned platform |
| `market_id` | Matched native ID |
| `match_method` | Identifier, title, fuzzy-reviewed |
| `match_confidence` | 0–1 audit score |
| `mention_start_char` | Character offset |
| `mention_end_char` | Character offset |
| `quoted_price` | Number represented in text |
| `quoted_price_unit` | cents, percent, odds, other |
| `publication_time` | Timestamp used for alignment |

## `market_snapshot`

| Field | Meaning |
|---|---|
| `snapshot_id` | Unique snapshot record |
| `platform` | Platform |
| `market_id` | Native market ID |
| `token_id` | Outcome token if needed |
| `observed_at` | Actual API observation time |
| `target_time` | Publication time being matched |
| `alignment_seconds` | Absolute timestamp difference |
| `snapshot_status` | Controlled status vocabulary |
| `price` | Matched price |
| `bid` / `ask` | Best quotes if actually observed |
| `relative_spread` | Quote spread normalized by midpoint |
| `depth_band` | Quantity within prespecified price band |
| `trailing_volume` | Activity over prespecified window |
| `trade_count` | Number of trades in window |
| `staleness_seconds` | Time since last trade |
| `realized_volatility` | Price variation over fixed window |
| `source_endpoint` | API endpoint used |

## Missingness rule

Empty values mean unavailable, not zero. No quality component may be zero-filled without an economic reason.
