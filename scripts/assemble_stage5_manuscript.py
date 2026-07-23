from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'outputs/stage5'; PAPER=ROOT/'paper/manuscript_stage5.md'

def read_first(paths):
    for p in paths:
        if p.exists(): return p.read_text(encoding='utf-8'), str(p.relative_to(ROOT))
    return '', None

def main():
    OUT.mkdir(parents=True,exist_ok=True); PAPER.parent.mkdir(parents=True,exist_ok=True)
    audit=json.loads((OUT/'stage5_input_audit.json').read_text()) if (OUT/'stage5_input_audit.json').exists() else {}
    status=audit.get('stage4_claim_status','blocked')
    results,result_src=read_first([ROOT/'outputs/stage4/stage4_report.md',ROOT/'paper/stage4/results_scaffold.md'])
    abstract=(ROOT/'paper/stage5/abstract_template.md').read_text(encoding='utf-8').replace('# Abstract Template','').strip()
    discussion=(ROOT/'paper/stage5/discussion_template.md').read_text(encoding='utf-8').replace('# Discussion Template','').strip()
    boundary={
      'confirmatory_ready':'The corpus passed the configured Stage 4 claim gates. Results are still interpreted as associations rather than causal effects.',
      'exploratory_only':'The corpus did not pass all confirmatory gates. All empirical statements below are restricted to exploratory within-corpus associations.',
      'blocked':'The empirical evidence is blocked for inferential claims. The Results section is limited to available diagnostics and pipeline status.'
    }.get(status,'The empirical status is unknown; no inferential claim is authorized.')
    text=f"""# Prediction Markets as Manufactured Public Signals: Media Framing, Market Quality, and Representational Overreach

## Abstract

{abstract}

**Empirical status:** `{status}`.

## Introduction

Prediction-market probabilities are numerical outputs of trading systems, but they increasingly circulate as statements about what “the public,” “voters,” or “people” believe. This paper investigates the representational work required to turn a market price into a public signal and the conditions under which media framing exceeds what participation and market quality can support.

## Theory and Hypotheses

The project distinguishes a market probability from a claim about collective representation. Framing becomes representationally consequential when it suppresses information about who may trade, how liquid the market is, how prices are formed, and whether the observed market can plausibly stand in for a broader public. The hypotheses and construct definitions remain those established in Stage 1 and operationalized in Stage 3.

## Data and Methods

The study uses a governed corpus of prediction-market media mentions linked to market records. Corpus construction, platform and source-type classification, article–market matching, coding rules, reliability procedures, and publication-aligned market-quality joins are documented in the Stage 2–4 protocols. Historical price evidence is distinguished from prospective order-book evidence, and current snapshots are not treated as historical market quality.

## Results

**Interpretation boundary:** {boundary}

{results or 'Stage 4 results were not found. Run the Stage 4 workflow before finalizing this section.'}

## Discussion

{discussion}

## Limitations

The design is observational and cannot establish causal effects of framing. Generalizability depends on source-type diversity and corpus construction. Article–market matching may be uncertain; publication-aligned quality measures may be missing; platform-owned coverage may differ systematically from independent journalism; and coding provenance constrains the strongest available claims. Failed Stage 4 gates must remain visible in any publication.

## Conclusion

Prediction markets can function as manufactured public signals when market probabilities are circulated with representational meanings that the underlying market cannot independently warrant. The framework developed here separates numerical prediction, market quality, media framing, and claims about collective belief, providing an auditable basis for evaluating representational overreach.

## Reproducibility Statement

The repository contains collection protocols, matching rules, codebooks, analysis scripts, claim gates, tests, and generated audit artifacts. Raw copyrighted article text is excluded by default. Stage 5 records file hashes and a claim–evidence ledger so that manuscript statements can be traced to design records or empirical outputs.
"""
    PAPER.write_text(text,encoding='utf-8')
    (OUT/'manuscript_build.json').write_text(json.dumps({'manuscript':str(PAPER.relative_to(ROOT)),'claim_status':status,'results_source':result_src},indent=2)+'\n',encoding='utf-8')
    print(PAPER)
if __name__=='__main__': main()
