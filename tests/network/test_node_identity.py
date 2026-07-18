import pytest
from dataclasses import FrozenInstanceError
from network.node_identity import load_node, NodeIdentity

def test_loads_three_nodes():
    alpha = load_node("alpha")
    beta = load_node("beta")
    gamma = load_node("gamma")
    assert alpha.site_key == "penrose_co"
    assert beta.site_key == "albuquerque_nm"
    assert gamma.site_key == "hessdalen_style"

def test_unknown_node_rejected():
    with pytest.raises(ValueError, match="Unknown node_id"):
        load_node("delta")

def test_identity_immutable():
    alpha = load_node("alpha")
    with pytest.raises(FrozenInstanceError):
        alpha.node_id = "omega"
