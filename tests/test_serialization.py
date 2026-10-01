from vepo.logging.schema import RunRecord,SCHEMA_VERSION

def test_result_schema_contains_required_fields():
    row=RunRecord("e","p","m","b",42,20,1,True,1,1,1.0,2.0,True,"algorithmic",1,0.3,None).to_dict()
    assert row["schema_version"]==SCHEMA_VERSION
    for key in ("experiment_id","problem_id","model","baseline","seed","budget","iteration","correct","runtime_ms","failure_type"):
        assert key in row
