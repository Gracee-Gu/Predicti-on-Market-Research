import json
from pathlib import Path
def test_schema_has_core_fields():
 s=json.loads(Path('config/stage3_annotation_schema.json').read_text())
 assert 'overreach_severity' in s['required_fields']
 assert s['enums']['overreach_severity']==[0,1,2,3]
