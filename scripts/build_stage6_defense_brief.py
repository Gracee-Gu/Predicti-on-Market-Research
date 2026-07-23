from __future__ import annotations

import json
from pathlib import Path

from _stage6_common import ROOT, OUT, FINAL_PAPER, read_json, resolve_claim_status

def main() -> None:
    FINAL_PAPER.mkdir(parents=True, exist_ok=True)
    claim_status, claim_source = resolve_claim_status()
    stage4_report = ROOT / "outputs/stage4/stage4_report.md"
    stage5_audit = read_json(ROOT / "outputs/stage5/stage5_release_audit.json")

    limitations = {
        "confirmatory_ready": [
            "The design remains observational; associations are not automatically causal.",
            "External validity still depends on corpus construction and source coverage.",
        ],
        "exploratory_only": [
            "The current evidence supports exploratory within-corpus associations only.",
            "The current corpus is concentrated in platform-owned material.",
            "Publication-aligned market-quality evidence is insufficient for the intended moderation tests.",
            "Human adjudication evidence is absent or insufficient in the current audited dataset.",
        ],
        "blocked": [
            "Inferential claims are blocked by the current evidence gates.",
            "Only pipeline status and descriptive diagnostics should be defended.",
        ],
    }[claim_status]

    brief = f"""# Stage 6 Defense Brief

## One-sentence contribution

This project develops an auditable framework for identifying when prediction-market probabilities are framed as representations of public belief beyond what participation, market quality, and disclosed caveats can support.

## Research question

How do media framing choices transform prediction-market prices into manufactured public signals, and when does that transformation constitute representational overreach?

## Core conceptual distinction

A market probability is a price produced by a trading mechanism. It is not automatically a representative measure of public opinion. The research separates market output, market quality, media framing, and representational claims.

## Design

The project combines a governed media corpus, article–market matching, structured framing annotation, publication-aligned market evidence where available, reliability and provenance checks, and claim-gated statistical reporting.

## Current evidence classification

`{claim_status}`

Resolved from: `{claim_source or "unresolved"}`

## Defensible result language

{"The configured gates permit confirmatory association language, but not causal language." if claim_status == "confirmatory_ready" else "Results must be described as exploratory associations within the audited corpus." if claim_status == "exploratory_only" else "No inferential result language is currently authorized."}

## Principal limitations

""" + "\n".join(f"- {item}" for item in limitations) + """

## Likely defense questions

### Why are market probabilities not public opinion?

They aggregate the positions of eligible and active traders under a particular mechanism. Participant selection, wealth, incentives, liquidity, platform rules, and information conditions differ from representative public-opinion measurement.

### What is representational overreach?

It is the degree to which communication attributes broad collective meaning—such as what voters or the public believe—to a market signal without adequate representativeness or market-quality support and without appropriate caveats.

### Why is the project still useful with exploratory evidence?

The conceptual framework, operational definitions, corpus governance, matching protocol, and claim-gated reproducibility pipeline remain substantive contributions. The exploratory analysis demonstrates how the constructs can be measured while making the evidence limitations explicit.

### What would most strengthen the study?

Expand independent and critical media coverage, recover publication-aligned market-quality measures, conduct documented human double coding and adjudication, and rerun the preregistered claim gates before confirmatory analysis.

## Bottom line

The strongest defensible contribution is a theory and measurement framework for auditing the representational leap from traded probability to public belief, supported by a transparent exploratory implementation.
"""
    (FINAL_PAPER / "defense_brief.md").write_text(brief, encoding="utf-8")

    memo = f"""# Supervisor Handoff Memo

## Project

Prediction Markets as Manufactured Public Signals: Media Framing, Market Quality, and Representational Overreach

## Current stage

Stage 6 — final submission and reproducibility preparation.

## Current empirical status

`{claim_status}`

Stage 6 preserves rather than upgrades the Stage 4/5 claim classification.

## Completed assets

- literature and theory foundation;
- construct definitions and hypotheses;
- corpus and data-source governance;
- platform collection and article–market matching pipeline;
- coding and reliability workflow;
- claim-gated analysis;
- manuscript and claim–evidence ledger;
- clean and blinded manuscript copies;
- reproducibility capsule and final audit;
- defense brief.

## Decisions requiring human review

1. Whether the current exploratory corpus is sufficient for the awarded research credit.
2. Whether additional independent-media sampling is required.
3. Whether human recoding/adjudication must be completed before submission.
4. Whether the paper should be positioned as an empirical article, methods paper, or conceptual framework with an exploratory demonstration.
5. Which venue or institutional format should determine final length and citation style.

## Recommended positioning

Present the current work as a serious, auditable conceptual and methodological study with an exploratory empirical demonstration. Do not represent it as a population-generalizable or causal test.

## Review files

- `paper/final/manuscript_clean.md`
- `paper/final/defense_brief.md`
- `outputs/stage6/final_audit.json`
- `outputs/stage5/claim_evidence_ledger.csv`
- `release/stage6_reproducibility_capsule.zip`
"""
    (FINAL_PAPER / "supervisor_handoff.md").write_text(memo, encoding="utf-8")
    print(FINAL_PAPER / "defense_brief.md")
    print(FINAL_PAPER / "supervisor_handoff.md")

if __name__ == "__main__":
    main()
