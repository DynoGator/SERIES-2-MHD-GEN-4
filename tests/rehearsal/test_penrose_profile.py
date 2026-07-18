from rehearsal.penrose_profile import PenroseSignalModel

def test_baseline_realistic():
    model = PenroseSignalModel("penrose_co")
    # Simulate 1 hour at 1 Hz
    vals = [model.geomagnetic_nt(float(i)) for i in range(3600)]
    mean = sum(vals) / len(vals)
    # config/sites.py penrose_co has baseline_nt 50000
    assert 47500 < mean < 52500

def test_spike_injection():
    model = PenroseSignalModel("penrose_co")
    base_val = model.geomagnetic_nt(0.0)
    model.inject_spike(5.0, 500.0, 1.0)
    
    spike_val = model.geomagnetic_nt(5.5)
    assert spike_val > base_val + 200.0 # Measurable above noise

def test_deterministic_seed():
    model1 = PenroseSignalModel("penrose_co", seed=42)
    model2 = PenroseSignalModel("penrose_co", seed=42)
    
    vals1 = [model1.geomagnetic_nt(float(i)) for i in range(100)]
    vals2 = [model2.geomagnetic_nt(float(i)) for i in range(100)]
    
    assert vals1 == vals2
