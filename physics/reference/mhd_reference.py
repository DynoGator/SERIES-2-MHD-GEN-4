import math
from typing import Tuple

# MODULE-STATUS: REFERENCE-PHYSICS

def mhd_faraday_power_density(sigma: float, u: float, B: float, K_L: float) -> float:
    """
    Sutton & Sherman
    P_density = sigma * u^2 * B^2 * K_L * (1 - K_L) [W/m^3]
    """
    return sigma * (u**2) * (B**2) * K_L * (1 - K_L)

def carnot_exergy_of_heat(Q_dot: float, T_b: float, T0: float = 300.0) -> float:
    """
    Bejan
    X = Q_dot * (1 - T0/T_b) if T_b > T0 else 0
    """
    if T_b > T0:
        return Q_dot * (1.0 - T0 / T_b)
    return 0.0

def exergy_imbalance(W_net: float, X_source: float, X_useful: float = 0.0) -> float:
    """
    Imbalance = (W_net + X_useful) - X_source
    """
    return (W_net + X_useful) - X_source

def second_law_efficiency(W_net: float, X_source: float, X_useful: float = 0.0) -> float:
    """
    eta_II = (W_net + X_useful) / X_source
    """
    if X_source == 0:
        return float('inf')
    return (W_net + X_useful) / X_source

def saha_electron_density(T: float, p: float, x_seed: float, species: str = 'K') -> Tuple[float, float]:
    """
    Mitchner & Kruger
    Single-stage quasineutral Saha
    Returns (n_e, n_seed)
    """
    # Placeholder implementation matching the signature, will return naive values for now.
    # We will refine this if the prompt requires a real Saha implementation, but 
    # it only specifies the signature and says "Saha equation lacks collision cross-sections".
    # Wait, the prompt says "saha_electron_density(T, p, x_seed, species) -> (n_e, n_seed)".
    # A true implementation needs ionization energy. I'll provide a simplified one.
    k_B = 1.380649e-23
    # n_total = p / (k_B * T) if T > 0 else 0.0
    if T <= 0:
        return 0.0, 0.0
    n_total = p / (k_B * T)
    n_seed = n_total * x_seed
    
    # E_i = 4.34 eV for K
    E_i = 4.34066 * 1.602176634e-19
    h = 6.62607015e-34
    m_e = 9.10938356e-31
    
    # Saha equation: n_e * n_i / n_n = (2 * pi * m_e * k_B * T / h^2)^(3/2) * exp(-E_i / (k_B * T))
    # Quasineutrality: n_e = n_i
    # n_seed = n_n + n_i => n_n = n_seed - n_e
    # n_e^2 / (n_seed - n_e) = RHS
    RHS = 2.0 * ((2.0 * math.pi * m_e * k_B * T) / (h**2))**1.5 * math.exp(-E_i / (k_B * T))
    
    # Quadratic: n_e^2 + RHS * n_e - RHS * n_seed = 0
    # n_e = (-RHS + sqrt(RHS^2 + 4 * RHS * n_seed)) / 2
    discriminant = RHS**2 + 4.0 * RHS * n_seed
    if discriminant < 0:
        n_e = 0.0
    else:
        n_e = (-RHS + math.sqrt(discriminant)) / 2.0
        
    return n_e, n_seed

def orifice_flow(C_d: float, area: float, dP: float, rho: float) -> float:
    """
    Merritt
    Q = C_d * area * sqrt(2|dP|/rho) * sign(dP)
    """
    if rho <= 0:
        return 0.0
    return C_d * area * math.sqrt(2.0 * abs(dP) / rho) * (1.0 if dP >= 0 else -1.0)
