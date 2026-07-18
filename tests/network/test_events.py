from network.events import make_event

def test_deterministic_event_id():
    e1 = make_event("alpha", "GEOMAGNETIC_SPIKE", 12345.0, 50.0)
    e2 = make_event("alpha", "GEOMAGNETIC_SPIKE", 12345.0, 50.0)
    assert e1.event_id == e2.event_id

def test_distinct_ids_for_distinct_nodes():
    e1 = make_event("alpha", "GEOMAGNETIC_SPIKE", 12345.0, 50.0)
    e2 = make_event("beta", "GEOMAGNETIC_SPIKE", 12345.0, 50.0)
    assert e1.event_id != e2.event_id
