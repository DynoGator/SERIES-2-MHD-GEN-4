import pytest
from validation.kill_chain import (
    generation_gate,
    second_law_gate,
    energy_closure_gate,
    conductivity_ceiling_gate,
    dissipation_sign_gate,
    fidelity_gate,
    evaluate_state_or_indeterminate
)
from validation.gates import Verdict

def test_verified_kill_chain_verdicts():
    # generation_gate(0,0)=FAIL
    res1 = generation_gate(0, 0)
    assert res1.verdict == Verdict.FAIL
    assert res1.reason == "no conductivity"
    
    # second_law_gate(150e3,100e3)=FAIL, imbalance=50000, eta_II=1.5
    res2 = second_law_gate(150e3, 100e3)
    assert res2.verdict == Verdict.FAIL
    assert res2.measured_values["imbalance"] == 50000
    assert res2.measured_values["eta_II"] == 1.5
    
    # second_law_gate(80e3,100e3)=PASS
    res3 = second_law_gate(80e3, 100e3)
    assert res3.verdict == Verdict.PASS
    
    # conductivity_ceiling_gate(2e20,1e20,50)=FAIL
    res4 = conductivity_ceiling_gate(2e20, 1e20, 50)
    assert res4.verdict == Verdict.FAIL
    
    # dissipation_sign_gate({'ohmic':-5})=FAIL
    res5 = dissipation_sign_gate({'ohmic': -5})
    assert res5.verdict == Verdict.FAIL
    
    # fidelity_gate([1,2,4,8,16,64])=INDETERMINATE
    res6 = fidelity_gate([1, 2, 4, 8, 16, 64])
    assert res6.verdict == Verdict.INDETERMINATE
    
    # energy_closure_gate(None,0,0)=INDETERMINATE
    res7 = energy_closure_gate(None, 0, 0)
    assert res7.verdict == Verdict.INDETERMINATE
