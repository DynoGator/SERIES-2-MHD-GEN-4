from network.consensus import ConsensusEngine
from network.events import make_event

def test_single_node_never_confirms():
    engine = ConsensusEngine()
    e1 = make_event("alpha", "TYPE1", 100.0, 1.0)
    assert engine.report(e1) == "SUSPECT"
    e2 = make_event("alpha", "TYPE1", 101.0, 1.0)
    assert engine.report(e2) == "SUSPECT"
    assert engine.state("TYPE1") == "SUSPECT"

def test_two_nodes_confirm():
    engine = ConsensusEngine()
    e1 = make_event("alpha", "TYPE1", 100.0, 1.0)
    e2 = make_event("beta", "TYPE1", 101.0, 1.0)
    assert engine.report(e1) == "SUSPECT"
    assert engine.report(e2) == "CONFIRMED"
    assert engine.state("TYPE1") == "CONFIRMED"

def test_window_expiry_rejects():
    engine = ConsensusEngine(window_s=60.0)
    e1 = make_event("alpha", "TYPE1", 100.0, 1.0)
    engine.report(e1)
    assert engine.state("TYPE1") == "SUSPECT"
    engine.expire(161.0)
    assert engine.state("TYPE1") == "REJECTED_UNCORROBORATED"

def test_distinct_nodes_only():
    engine = ConsensusEngine()
    e1 = make_event("alpha", "TYPE1", 100.0, 1.0)
    e2 = make_event("alpha", "TYPE1", 101.0, 2.0)
    engine.report(e1)
    assert engine.report(e2) == "SUSPECT"

def test_event_dedup():
    engine = ConsensusEngine()
    e1 = make_event("alpha", "TYPE1", 100.0, 1.0)
    engine.report(e1)
    assert len(engine.active_events["TYPE1"]) == 1
    engine.report(e1)
    assert len(engine.active_events["TYPE1"]) == 1
