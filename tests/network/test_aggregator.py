from network.aggregator import CentralAggregator
from network.node_identity import load_node

def test_three_node_ingest():
    nodes = [load_node("alpha"), load_node("beta"), load_node("gamma")]
    agg = CentralAggregator(nodes)
    agg.ingest("alpha", {"timestamp_utc": "123"})
    rep = agg.report()
    assert "alpha" in rep["node_status"]
    assert "beta" in rep["node_status"]
    assert "gamma" in rep["node_status"]

def test_schema_alignment():
    nodes = [load_node("alpha")]
    agg = CentralAggregator(nodes)
    rep = agg.report()
    assert "meta" in rep["node_status"]["alpha"]
    assert "node_type" in rep["node_status"]["alpha"]["meta"]
    assert "sensors" in rep["node_status"]["alpha"]

def test_consensus_ledger_in_report():
    nodes = [load_node("alpha")]
    agg = CentralAggregator(nodes)
    rep = agg.report()
    assert "consensus_ledger" in rep
    assert "correlations" in rep
