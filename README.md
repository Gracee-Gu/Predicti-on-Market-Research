# Framing Without Disclosure: Representational Overreach in a Prediction-Market Platform's Own Public Communications

Independent research project by Yingzi Gu (Cornell University), advised by Professor Tommaso Bondi.

**The paper is [`paper/final/manuscript.pdf`](paper/final/manuscript.pdf).** Source is
[`paper/final/manuscript.html`](paper/final/manuscript.html) (plain HTML/CSS, no LaTeX
dependency); figures are in `paper/final/figures/`.

## What this project studies

Prediction-market prices are increasingly presented to the public as if they were direct readings
of collective belief. This project asks how one platform, Kalshi, frames its own contracts in its
own public writing, and whether that framing is calibrated to the liquidity and stability of the
specific market being described. It combines a corpus of platform-published articles linked to
specific contracts, scored on seven framing constructs by a disclosed, deterministic keyword
classifier (not human coders — see the paper's §3.3, which states this limitation directly), with
independent re-verification of market-quality evidence pulled directly from Kalshi's own trade,
market, and candlestick API endpoints (rather than trusting cached values or platform summaries).
A smaller, clearly-labeled exploratory comparison with how partner, independent, and regulatory
sources describe the same platform is reported in the paper's Appendix A.

## Repository layout

```
paper/final/        the manuscript (HTML source, rendered PDF, figures) and references.bib
docs/                methodology: corpus protocol, codebook, research design, reproduction steps
data/analysis/       the final article-market dataset used in every reported result
data/annotations/    annotation sheets (see paper §3.3 for how these were actually produced —
                     the coder_id/double_code fields do not reflect independent human coding)
outputs/verification/ independent Kalshi API re-verification artifacts (ticker audit, candlestick
                     pulls, cross-source tagging) underlying §5-7 of the paper
src/pmresearch/      collector and analysis library code
scripts/             collection, matching, coding-support, analysis, and figure-generation scripts
tests/               unit tests for the collectors and analysis pipeline
config/              collection and analysis configuration
```

Raw article text and prospective order-book snapshots are excluded from version control by
design (`.gitignore`; see `docs/corpus_protocol.md`) because much of the source material is
copyrighted. Only URLs, hashes, short excerpts, and derived labels are retained.

## Reproducing the results

See `docs/REPRODUCE.md` for the full pipeline, from raw collection through to rendering the PDF.
In short:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r stage4_requirements.txt
uv run pytest                      # unit tests
python scripts/make_figures.py     # regenerate figures from the audited data
```

## Key methodology documents

- `docs/research_design.md` — theory, constructs, and hypotheses
- `docs/codebook.md` — the seven-construct coding instrument and decision rule
- `docs/corpus_protocol.md` — collection scope, inclusion/exclusion criteria, copyright-safe storage
- `docs/data_dictionary.md` — field-level documentation of the analytic dataset
- `docs/literature_map.md` — the literature review underlying the paper's framing
- `paper/references.bib` — full bibliography
