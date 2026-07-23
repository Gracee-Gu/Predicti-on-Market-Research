from pmresearch.stage4.core import audit_rows, bh_adjust, mean_difference

def row(source="platform_owned", quality="", human=""):
    return {"pair_id":"p","article_id":"a","market_id":"m","source_type":source,"platform":"kalshi","overreach_severity":"2","probability_as_public_opinion":"1","representativeness_caveat":"0","market_quality_caveat":"0","certainty_language":"1","democratic_language":"0","horse_race_frame":"1","spread":quality,"human_adjudicated":human}

def test_bh_monotone_example():
    q=bh_adjust([.01,.04,.03]); assert q[0] <= q[2] <= q[1]

def test_audit_blocks_single_source():
    r=audit_rows([row() for _ in range(100)], {"minimum_n":80,"minimum_source_types":2,"maximum_single_source_share":.85,"minimum_quality_coverage":.5,"require_human_adjudication_for_confirmatory":True})
    assert r["claim_status"]=="exploratory_only" and not r["checks"]["source_type_count"]

def test_mean_difference():
    rows=[row(),row()]; rows[0]["horse_race_frame"]="1"; rows[0]["overreach_severity"]="3"; rows[1]["horse_race_frame"]="0"; rows[1]["overreach_severity"]="1"
    assert mean_difference(rows,"horse_race_frame","overreach_severity")["difference"]==2
