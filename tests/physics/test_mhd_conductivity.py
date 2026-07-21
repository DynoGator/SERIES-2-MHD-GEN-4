import pytest
import os
from physics.mhd.conductivity import PlasmaConductivity

def load_anchors():
    anchors = []
    filepath = os.path.join(os.path.dirname(__file__), '../../data/reference/conductivity_anchors.md')
    with open(filepath, 'r') as f:
        in_table = False
        for line in f:
            if "|-" in line:
                in_table = True
                continue
            if in_table and line.startswith("|"):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 6:
                    T = float(parts[1])
                    x_seed = float(parts[2])
                    p = float(parts[3])
                    sigma_ref = float(parts[4])
                    tol = float(parts[5]) / 100.0
                    anchors.append((T, x_seed, p, sigma_ref, tol))
    return anchors

@pytest.mark.xfail(strict=True, reason="Saha equation lacks collision cross-sections for accurate conductivity")
@pytest.mark.parametrize("T, x_seed, p, sigma_ref, tol", load_anchors())
def test_sigma_against_reference(T, x_seed, p, sigma_ref, tol):
    cond = PlasmaConductivity('K', {})
    
    # Test provisional physics
    sigma_provisional = cond.sigma_from_saha(T, p, x_seed)
    
    # We assert that the saha implementation matches the literature reference.
    # This WILL fail since it's a placeholder without cross-sections. 
    # Green is only meaningful once gates can go red.
    err = abs(sigma_provisional - sigma_ref) / sigma_ref
    assert err <= tol, f"SAHA sigma={sigma_provisional} failed to match anchor {sigma_ref} within {tol*100}%"
