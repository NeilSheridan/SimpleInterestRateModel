import numpy as np
from numpy import ndarray


def spot_to_forward(spot: np.ndarray, frequency_per_annum : int = 12, t=None) -> np.ndarray:
    """
    Convert spot to forward rate

    Inputs:
    spot : np.ndarray
    frequency_per_annum : int   default 12
    t : np.ndarray of times corresponding to the rates in the spot curve.
    """

    if t is None:
        t = np.arange(1, len(spot)+1) / frequency_per_annum


    forwards = spot.reshape(-1,1).copy()
    forwards[1:] = (((1+forwards[1:])**t.reshape(-1,1)[1:])/((1+forwards[:-1])**t.reshape(-1,1)[:-1]))**(1/(t.reshape(-1,1)[1:]-t.reshape(-1,1)[:-1]))-1

    return forwards


def forward_to_spot(forward: np.ndarray, frequency_per_annum:int = 12, t:np.ndarray=None) -> np.ndarray:
    """
    Convert spot to forward rate

    Inputs:
    forward : np.ndarray
    frequency_per_annum : int   default 12
    t : np.ndarray of times corresponding to the rates in the spot curve.
    """

    if t is None:
        t = np.arange(1, len(forward)+1) / frequency_per_annum

    t_diffs = np.diff(np.insert(t, 0, 0))

    spot = np.cumprod((1+forward)**t_diffs.reshape(-1,1),axis=0)**(1/t.reshape(-1,1))-1

    return spot


def get_correlated_random_shocks(correlation: float, num_sims: int, spot: ndarray) -> ndarray:
    # Calculate correlated shocks
    shocks = np.random.randn(1, num_sims) * np.sqrt(correlation) + np.random.randn(np.size(spot), num_sims) * np.sqrt(
        1 - correlation)
    return shocks
