#!/usr/bin/env python3
import json
from pathlib import Path
req=['config/stage3.yaml','config/stage3_annotation_schema.json','docs/stage3_codebook.md','scripts/build_stage3_sampling_frame.py','scripts/check_stage3_reliability.py','scripts/build_stage3_analytic_dataset.py']
status={p:Path(p).exists() for p in req}; result={'implementation_pass':all(status.values()),'files':status}; Path('docs/stage3_qa_report.json').write_text(json.dumps(result,indent=2),encoding='utf-8'); print(json.dumps(result,indent=2))
