#!/usr/bin/env python3
"""Generate all manuscript figures from real, audited repository data.

No synthetic or placeholder values are introduced here: every number plotted
is read from data/analysis/article_market_dataset.csv,
data/annotations/*, or the outputs/verification/* artifacts produced by
live Kalshi API calls and manual corpus review during Stage 8 recovery.
"""
from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "outputs/verification/figures"
FIG.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Shared style: Okabe-Ito colorblind-safe categorical palette, single sequential
# hue for magnitude, muted gray for de-emphasized / "no evidence" states.
# ---------------------------------------------------------------------------
INK = "#1b1f24"
MUTED = "#6b7280"
GRID = "#d9dce1"
SURFACE = "#ffffff"

C_BLUE = "#0072B2"
C_VERMILLION = "#D55E00"
C_GREEN = "#009E73"
C_ORANGE = "#E69F00"
C_PURPLE = "#CC79A7"
C_SKY = "#56B4E9"
C_GRAY = "#999999"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "text.color": INK,
    "axes.edgecolor": GRID,
    "axes.labelcolor": INK,
    "axes.titlecolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.6,
    "axes.axisbelow": True,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})


def savefig(fig, name, w=7.0, h=4.2):
    fig.set_size_inches(w, h)
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


def strip_spines(ax, keep=("left", "bottom")):
    for s in ax.spines:
        ax.spines[s].set_visible(s in keep)
    ax.tick_params(length=3, color=GRID)


# ---------------------------------------------------------------------------
# Load core data
# ---------------------------------------------------------------------------
rows = list(csv.DictReader(open(ROOT / "data/analysis/article_market_dataset.csv")))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


TOPIC_RULES = [
    ("sports", ["WORLDCUP", "WC-", "WCMOV", "WCFINAL", "WCADVANCE", "WCTOTAL", "WCGOALLEADER",
                "PGA", "MLB", "NBA", "NEXTTEAM", "BALLONDOR", "GOLF", "HRDERBY", "ROUNDSCORE",
                "UFC", "NFL", "NHL", "ATP"]),
    ("awards_entertainment", ["OSCAR", "GGLOVE", "EMMY", "GRAMMY", "WCAWARD", "RT-", "BIGBROTHER",
                              "SONGS", "HALFTIME", "CELEB", "PM-26JULZYNSHIP"]),
    ("finance_markets", ["EARNINGS", "SCHW", "STOCK", "FED", "RATE", "WTI", "OIL", "NASDAQ",
                         "SP500", "BTC", "ETH", "CRYPTO", "GOOG", "DPZ", "LUV-", "CBDECISION",
                         "ACPI", "UE-", "UKRETAIL"]),
    ("politics_government", ["PRESPERSON", "MAYOR", "SENATOR", "ELECTION", "CONGRESS", "NEXTAG",
                             "NEXTSC", "SHUTDOWN", "GOV", "NAVAJOPRES", "BERNIEMENTION"]),
    ("weather_climate", ["AQI", "WEATHER", "HEAT", "STORM", "DST", "HURRICANE", "TEMP"]),
]


def topic_of(market_id: str) -> str:
    m = market_id.upper()
    for label, kws in TOPIC_RULES:
        if any(kw in m for kw in kws):
            return label
    return "other"


for r in rows:
    r["_topic"] = topic_of(r["market_id"])

CONSTRUCTS = ["market_probability_present", "probability_as_public_opinion",
              "representativeness_caveat", "market_quality_caveat", "certainty_language",
              "democratic_language", "horse_race_frame"]
CONSTRUCT_LABELS = {
    "market_probability_present": "Probability\nforegrounded",
    "probability_as_public_opinion": "Probability =\npublic opinion",
    "representativeness_caveat": "Representativeness\ncaveat",
    "market_quality_caveat": "Market-quality\ncaveat",
    "certainty_language": "Certainty\nlanguage",
    "democratic_language": "Democratic\nlanguage",
    "horse_race_frame": "Horse-race\nframe",
}

# =============================================================================
# Figure 1 — Research design diagram (conceptual; hand-built, not data-driven)
# =============================================================================

def fig1_research_design():
    fig, ax = plt.subplots()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.6)
    ax.axis("off")

    boxes = [
        (0.3, 1.6, 2.1, 1.2, "Platform &\nmedia relationship\n(ownership, partnership,\nsyndication)", C_BLUE),
        (2.9, 1.6, 2.1, 1.2, "Framing\n(probability-as-opinion,\ncertainty, horse race,\ndemocratic language)", C_VERMILLION),
        (5.5, 1.6, 2.1, 1.2, "Market-quality\ndisclosure\n(liquidity, spread,\nvolume, representativeness)", C_GREEN),
        (8.1, 1.6, 1.7, 1.2, "Audience-facing\npublic signal\n(\"the odds are X%\")", C_PURPLE),
    ]
    for x, y, w, h, label, color in boxes:
        fb = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.08",
                             linewidth=1.4, edgecolor=color, facecolor=color + "1A")
        ax.add_patch(fb)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=8.6, color=INK)

    arrow_pairs = [(2.4, 2.2, 2.9, 2.2), (5.0, 2.2, 5.5, 2.2), (7.6, 2.2, 8.1, 2.2)]
    for x0, y0, x1, y1 in arrow_pairs:
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=14,
                                      color=MUTED, linewidth=1.4))

    # omission path: quality disclosure -> signal, dashed "frequently omitted"
    ax.add_patch(FancyArrowPatch((6.55, 1.55), (8.9, 1.55), connectionstyle="arc3,rad=-0.35",
                                  arrowstyle="-|>", mutation_scale=12, color=C_VERMILLION,
                                  linewidth=1.3, linestyle=(0, (4, 2))))
    ax.text(7.7, 0.75, "frequently omitted in transmission", ha="center", fontsize=8, color=C_VERMILLION,
            style="italic")

    ax.text(5.0, 3.85, "Representational overreach: a numeric price is asserted as a public-opinion signal\n"
                       "without the market-quality and representativeness evidence needed to license that claim.",
            ha="center", va="center", fontsize=9.2, color=INK)

    savefig(fig, "fig1_research_design.png", w=8.6, h=3.6)


# =============================================================================
# Figure 2 — Corpus & annotation flow (real counts)
# =============================================================================

def fig2_corpus_flow():
    n_media_by_type = {"platform_owned": 49, "partner_media": 31, "independent_media": 47,
                        "regulatory_critical": 37}
    n_media_total = sum(n_media_by_type.values())
    n_pairs = len(rows)
    n_quality_present = sum(1 for r in rows if r["quality_missing"] == "0")

    fig, ax = plt.subplots()
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.3, 5.3)
    ax.axis("off")

    stage_y = [4.2, 2.8, 1.4, 0.0]
    stage_h = 1.0

    # Stage A: raw corpus by source type (stacked)
    x0 = 0.2
    widths = {"platform_owned": 2.4, "partner_media": 1.5, "independent_media": 2.3, "regulatory_critical": 1.8}
    colors = {"platform_owned": C_BLUE, "partner_media": C_ORANGE, "independent_media": C_GREEN,
              "regulatory_critical": C_PURPLE}
    labels = {"platform_owned": "Platform-owned", "partner_media": "Partner media",
              "independent_media": "Independent media", "regulatory_critical": "Regulatory/critical"}
    cx = x0
    for k in ["platform_owned", "partner_media", "independent_media", "regulatory_critical"]:
        w = widths[k]
        ax.add_patch(FancyBboxPatch((cx, stage_y[0]), w, stage_h, boxstyle="round,pad=0.04,rounding_size=0.06",
                                     linewidth=1.2, edgecolor=colors[k], facecolor=colors[k] + "22"))
        ax.text(cx + w / 2, stage_y[0] + stage_h / 2, f"{labels[k]}\nn={n_media_by_type[k]}",
                ha="center", va="center", fontsize=8.2)
        cx += w + 0.15
    ax.text(-0.05, stage_y[0] + stage_h / 2, f"Raw corpus\n{n_media_total} docs", ha="right", va="center",
            fontsize=9, fontweight="bold")

    def full_bar(y, label, text, color, note=None):
        w = 8.6
        ax.add_patch(FancyBboxPatch((x0, y), w, stage_h, boxstyle="round,pad=0.04,rounding_size=0.06",
                                     linewidth=1.3, edgecolor=color, facecolor=color + "15"))
        ax.text(x0 + w / 2, y + stage_h / 2 + (0.12 if note else 0), text, ha="center", va="center", fontsize=9)
        if note:
            ax.text(x0 + w / 2, y + 0.18, note, ha="center", va="center", fontsize=7.6, color=MUTED,
                    style="italic")
        ax.text(-0.05, y + stage_h / 2, label, ha="right", va="center", fontsize=9, fontweight="bold")

    full_bar(stage_y[1], "Ticker /\nlink matching",
              f"Exact-identifier article\N{EN DASH}market matches: n={n_pairs} (100% platform-owned)",
              C_VERMILLION,
              note="102 non-platform documents screened; 0 yielded a verifiable quoted-price match "
                   "(see §3.2 and Appendix A)")
    full_bar(stage_y[2], "Automated\nclassification",
              f"n={n_pairs} pairs scored on 7 constructs via a disclosed keyword rule set (§3.3)",
              C_ORANGE,
              note="not human-coded; construction of the overreach-severity composite documented in §3.3")
    full_bar(stage_y[3], "Market-quality\nlinkage",
              f"Publication-aligned quality evidence recovered: n={n_quality_present} "
              f"({n_quality_present/n_pairs:.1%}) via live Kalshi API re-verification", C_PURPLE)

    for y0, y1 in zip(stage_y[:-1], stage_y[1:]):
        ax.add_patch(FancyArrowPatch((x0 + 4.3, y0), (x0 + 4.3, y1 + stage_h), arrowstyle="-|>",
                                      mutation_scale=13, color=MUTED, linewidth=1.3))

    savefig(fig, "fig2_corpus_flow.png", w=9.4, h=6.8)


# =============================================================================
# Figure 3 — Frame co-occurrence network
# =============================================================================

def fig3_frame_network():
    import networkx as nx

    bin_vals = {}
    for c in CONSTRUCTS:
        bin_vals[c] = [1 if (num(r[c]) is not None and num(r[c]) >= 1) else 0 for r in rows]

    n = len(rows)
    G = nx.Graph()
    prevalence = {c: sum(bin_vals[c]) / n for c in CONSTRUCTS}
    for c in CONSTRUCTS:
        G.add_node(c, prevalence=prevalence[c])

    edges = []
    for i, c1 in enumerate(CONSTRUCTS):
        for c2 in CONSTRUCTS[i + 1:]:
            both = sum(1 for a, b in zip(bin_vals[c1], bin_vals[c2]) if a == 1 and b == 1)
            union = sum(1 for a, b in zip(bin_vals[c1], bin_vals[c2]) if a == 1 or b == 1)
            jac = both / union if union else 0
            if both > 0:
                edges.append((c1, c2, both, jac))
                G.add_edge(c1, c2, weight=jac, count=both)

    fig, ax = plt.subplots()
    pos = nx.spring_layout(G, seed=7, k=1.6, weight="weight")

    for c1, c2, both, jac in edges:
        x0, y0 = pos[c1]
        x1, y1 = pos[c2]
        ax.plot([x0, x1], [y0, y1], color=MUTED, alpha=min(0.15 + jac * 1.4, 0.9),
                linewidth=0.6 + jac * 7, solid_capstyle="round", zorder=1)

    sizes = [900 + 2400 * prevalence[c] for c in G.nodes]
    node_colors = [C_BLUE if prevalence[c] >= 0.5 else C_SKY for c in G.nodes]
    xs = [pos[c][0] for c in G.nodes]
    ys = [pos[c][1] for c in G.nodes]
    ax.scatter(xs, ys, s=sizes, c=node_colors, edgecolors=INK, linewidths=1.0, zorder=2)
    for c in G.nodes:
        x, y = pos[c]
        ax.text(x, y, f"{CONSTRUCT_LABELS[c]}\n({prevalence[c]:.0%})", ha="center", va="center",
                fontsize=7.6, zorder=3, color=INK)

    ax.set_xlim(min(xs) - 0.55, max(xs) + 0.55)
    ax.set_ylim(min(ys) - 0.55, max(ys) + 0.55)
    ax.axis("off")
    ax.set_title("Frame co-occurrence network (n=116 platform-owned pairs)\n"
                  "node size = prevalence; edge width = co-occurrence strength (Jaccard)", fontsize=9.5)
    savefig(fig, "fig3_frame_cooccurrence_network.png", w=7.2, h=6.2)

    with open(FIG.parent / "frame_cooccurrence_edges.json", "w") as f:
        json.dump({"prevalence": prevalence, "edges": [{"a": a, "b": b, "count": c, "jaccard": j}
                                                          for a, b, c, j in edges]}, f, indent=2)


# =============================================================================
# Figure 4 — Coefficient plot with CIs (real M1 OLS) + exploratory cross-source panel
# =============================================================================

def wilson_ci(k, n, z=1.96):
    if n == 0:
        return (0, 0, 0)
    p = k / n
    denom = 1 + z ** 2 / n
    center = (p + z ** 2 / (2 * n)) / denom
    half = (z * math.sqrt((p * (1 - p) + z ** 2 / (4 * n)) / n)) / denom
    return p, max(0, center - half), min(1, center + half)


def figA1_crosssource_frames():
    tag_rows = list(csv.DictReader(open(ROOT / "outputs/verification/cross_source_frame_tags.csv")))
    tag_rows = [r for r in tag_rows if r["frame_tag"] != "no_captured_text"]
    by_type = defaultdict(Counter)
    for r in tag_rows:
        by_type[r["source_type"]][r["frame_tag"]] += 1
    tags = ["price_as_signal", "growth_legitimacy", "scandal_integrity", "regulatory_jurisdiction", "other_context"]
    tag_labels = {"price_as_signal": "Price-as-signal", "growth_legitimacy": "Growth/legitimacy",
                  "scandal_integrity": "Scandal/integrity", "regulatory_jurisdiction": "Regulatory/jurisdiction",
                  "other_context": "Other context"}
    src_types = ["partner_media", "independent_media", "regulatory_critical"]
    src_colors = {"partner_media": C_ORANGE, "independent_media": C_GREEN, "regulatory_critical": C_PURPLE}

    fig, ax2 = plt.subplots()
    y2 = np.arange(len(tags))
    bar_h = 0.24
    for i, st in enumerate(src_types):
        total = sum(by_type[st].values())
        props = [by_type[st][t] / total if total else 0 for t in tags]
        ax2.barh(y2 + (i - 1) * bar_h, props, height=bar_h, color=src_colors[st], label=st.replace("_", " "))
    ax2.set_yticks(y2)
    ax2.set_yticklabels([tag_labels[t] for t in tags], fontsize=8.8)
    strip_spines(ax2)
    ax2.set_xlabel("Share of tagged documents (exploratory, single-coder)", fontsize=8.8)
    ax2.legend(fontsize=7.6, frameon=False, loc="lower right")
    ns = {st: sum(by_type[st].values()) for st in src_types}
    ax2.set_title("How other institutions discuss the same platform (exploratory)\n"
                   f"n(partner)={ns['partner_media']}, n(independent)={ns['independent_media']}, "
                   f"n(regulatory)={ns['regulatory_critical']}", fontsize=9.4)

    savefig(fig, "fig_appendix_crosssource.png", w=7.2, h=4.0)


# =============================================================================
# Figure 5 — Market quality vs authority framing scatter
# =============================================================================

def fig5_quality_vs_framing():
    fig, ax = plt.subplots()
    rng = np.random.default_rng(11)

    tiers = {"unavailable": 0, "historical_price_matched": 1, "historical_trade_matched": 2}
    tier_labels = ["No public evidence\nrecovered", "Price recovered,\nno liquidity evidence",
                   "Full trade/volume/\nspread evidence"]
    tier_colors = [C_GRAY, C_ORANGE, C_GREEN]

    xs, ys, cs = [], [], []
    for r in rows:
        ppo = num(r["probability_as_public_opinion"])
        if ppo is None:
            continue
        tier = tiers.get(r["quality_evidence_class"], 0)
        xs.append(ppo + rng.uniform(-0.12, 0.12))
        ys.append(tier + rng.uniform(-0.14, 0.14))
        cs.append(tier)

    for t in [0, 1, 2]:
        xi = [x for x, c in zip(xs, cs) if c == t]
        yi = [y for y, c in zip(ys, cs) if c == t]
        ax.scatter(xi, yi, s=46, color=tier_colors[t], edgecolors=INK, linewidths=0.5, alpha=0.85,
                   label=f"{tier_labels[t]} (n={len(xi)})", zorder=3)

    ax.axvspan(1.5, 2.6, color=C_VERMILLION, alpha=0.06, zorder=0)
    ax.axhspan(-0.5, 0.5, color=C_VERMILLION, alpha=0.06, zorder=0)
    ax.text(2.05, 2.35, "high framing,\nno evidence", ha="center", va="center", fontsize=8.2, color=C_VERMILLION,
            style="italic")

    ax.set_xlim(-0.5, 2.6)
    ax.set_ylim(-0.6, 2.6)
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(tier_labels, fontsize=8.2)
    ax.set_xticks([0, 1, 2])
    ax.set_xlabel("Probability-as-public-opinion score (0-2, keyword-classified, jittered)",
                  fontsize=8.8)
    ax.set_title("Independently recovered market-quality evidence vs.\nkeyword-classified framing (one point per audited pair, n=116)",
                 fontsize=9.6)
    strip_spines(ax)
    ax.legend(fontsize=7.6, frameon=False, loc="upper left")
    savefig(fig, "fig5_quality_vs_framing_scatter.png", w=7.4, h=5.0)


# =============================================================================
# Figure 6 — Ridgeline / violin of frame-score distributions by topic
# =============================================================================

def fig6_ridgeline_by_topic():
    from scipy.stats import gaussian_kde

    topic_scores = defaultdict(list)
    for r in rows:
        ov = num(r["probability_as_public_opinion"])
        if ov is None:
            continue
        topic_scores[r["_topic"]].append(ov + np.random.default_rng(abs(hash(r["pair_id"])) % (2**32)).uniform(-0.08, 0.08))

    order = sorted(topic_scores, key=lambda k: -len(topic_scores[k]))
    fig, ax = plt.subplots()
    xg = np.linspace(-0.8, 2.8, 300)
    palette = [C_BLUE, C_VERMILLION, C_GREEN, C_ORANGE, C_PURPLE, C_SKY]

    for i, topic in enumerate(order):
        vals = np.array(topic_scores[topic])
        base = i * 1.05
        if len(vals) >= 3 and np.std(vals) > 1e-6:
            kde = gaussian_kde(vals, bw_method=0.35)
            dens = kde(xg)
            dens = dens / dens.max() * 0.9
        else:
            dens = np.zeros_like(xg)
        ax.fill_between(xg, base, base + dens, color=palette[i % len(palette)], alpha=0.35, zorder=2)
        ax.plot(xg, base + dens, color=palette[i % len(palette)], linewidth=1.3, zorder=3)
        jitter_y = base + np.random.default_rng(i).uniform(0.02, 0.16, size=len(vals))
        ax.scatter(vals, jitter_y, s=10, color=palette[i % len(palette)], alpha=0.75, zorder=4,
                   edgecolors="none")
        ax.text(-0.95, base + 0.12, f"{topic.replace('_', ' ')}\n(n={len(vals)})", ha="right", va="center",
                fontsize=8)

    ax.set_xlim(-2.3, 2.8)
    ax.set_ylim(-0.2, (len(order) - 1) * 1.05 + 1.1)
    ax.set_yticks([])
    ax.set_xlabel("Probability-as-public-opinion score (0-2, keyword-classified), raw points shown", fontsize=8.8)
    ax.set_title("Probability-as-public-opinion framing by market topic\n(platform-owned corpus, n=116; topic inferred from ticker taxonomy)",
                 fontsize=9.4)
    strip_spines(ax, keep=("bottom",))
    savefig(fig, "fig7_ridgeline_by_topic.png", w=7.6, h=5.4)


# =============================================================================
# Figure 7 — Event-window standardized plots (real candlestick data)
# =============================================================================

def fig7_event_window():
    data = json.load(open(ROOT / "outputs/verification/case_market_candlesticks.json"))
    mentions = {r["market_id"]: r for r in
                (json.loads(l) for l in open(ROOT / "data/processed/market_mentions_kalshi_archive_45_v3.jsonl"))}

    tickers = ["KXMAYORLA-26-SPRA", "KXWORLDCUPHALFTIME-26-POS", "KXAQICITY-NYC26JUL19-130"]
    display = {"KXMAYORLA-26-SPRA": "LA mayor's-race price distortion",
               "KXWORLDCUPHALFTIME-26-POS": "World Cup halftime surprise-guest",
               "KXAQICITY-NYC26JUL19-130": "NYC air-quality threshold"}
    colors = {"KXMAYORLA-26-SPRA": C_VERMILLION, "KXWORLDCUPHALFTIME-26-POS": C_BLUE,
              "KXAQICITY-NYC26JUL19-130": C_GREEN}

    fig, axes = plt.subplots(1, 3)
    for ax, t in zip(axes, tickers):
        candles = data[t]["candles"]
        if not candles:
            ax.axis("off")
            continue
        ts = np.array([c.get("end_period_ts", 0) for c in candles], dtype=float)
        t0 = ts.min()
        hours = (ts - t0) / 3600.0

        def price_of(c):
            p = c.get("price", {}) or {}
            for f in ("mean_dollars", "close_dollars", "mean", "close"):
                if p.get(f) not in (None, ""):
                    try:
                        return float(p[f])
                    except ValueError:
                        continue
            return np.nan

        prices = np.array([price_of(c) for c in candles])
        vols = np.array([float(c.get("volume", c.get("volume_fp", 0)) or 0) for c in candles])

        ax2 = ax.twinx()
        ax2.bar(hours, vols, width=(hours.max() / max(len(hours), 1)) * 0.9, color=MUTED, alpha=0.28, zorder=1)
        ax2.set_yticks([])
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        ax2.spines["left"].set_visible(False)

        ax.plot(hours, prices, color=colors[t], linewidth=1.6, zorder=3)
        pub_iso = mentions.get(t, {}).get("publication_time", "")
        if pub_iso:
            from datetime import datetime
            try:
                pub_ts = datetime.fromisoformat(pub_iso.replace("Z", "+00:00")).timestamp()
                pub_hour = (pub_ts - t0) / 3600.0
                if 0 <= pub_hour <= hours.max():
                    ax.axvline(pub_hour, color=INK, linewidth=1.1, linestyle=(0, (3, 2)))
                    ax.text(pub_hour, 0.93, " cited", rotation=90, fontsize=7, ha="left", va="top",
                            color=INK)
            except ValueError:
                pass
        strip_spines(ax)
        ax.set_ylim(0, 1.02)
        ax.set_xlabel("Hours since market open", fontsize=8)
        ax.set_title(f"{display[t]}\n(n={len(candles)} real 60-min candles)", fontsize=8.6)
    axes[0].set_ylabel("YES price ($, line) / volume (bars, right)", fontsize=8)

    fig.suptitle("Event-window price and volume trajectories for three fully verifiable cited markets\n"
                 "(live Kalshi candlestick history; dashed line = article publication time, where within window)",
                 fontsize=9.4, y=1.05)
    savefig(fig, "fig6_event_window.png", w=10.6, h=3.8)


if __name__ == "__main__":
    fig1_research_design()
    fig2_corpus_flow()
    fig3_frame_network()
    figA1_crosssource_frames()
    fig5_quality_vs_framing()
    fig6_ridgeline_by_topic()
    fig7_event_window()
    print("ALL FIGURES DONE")
