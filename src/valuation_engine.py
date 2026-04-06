import numpy as np
import pandas as pd
from numpy import bool, ndarray

from src.support_functions import spot_to_forward, forward_to_spot, get_correlated_random_shocks

def get_asset_data(file_name : str):

    """Get Asset Data"""

    assets = pd.read_excel(file_name, sheet_name='Assets')
    cash_flows = pd.read_excel(file_name, sheet_name='CFs', header=None)
    spot = pd.read_excel(file_name, sheet_name='Spot', header=None)
    return assets, cash_flows, spot

def simulate_spot_curve(spot : ndarray, vol : ndarray, num_sims : int, correlation:float=0) -> ndarray:

    """Generates random spot interest rate curves.
    Each forward rate is shifted by a correlated random normal variable"""

    forward_curve = spot_to_forward(spot)

    # Get shocks
    shocks = get_correlated_random_shocks(correlation, num_sims, spot)

    # Apply random shocks scaled by volatility
    forward_curve_final = forward_curve.reshape(-1, 1) + shocks * vol.reshape(-1, 1)

    # Convert back to spot
    final_spots = forward_to_spot(forward_curve_final)

    return final_spots

def value_portfolio(cash_flows : ndarray,spreads : ndarray,spot : ndarray, criterion : bool = None):

    """Calculates portfolio value for given spreads and spot curves"""

    # Terms
    t = np.arange(1, len(spot)+1).reshape(-1, 1) / 12

    # Spot curve. Check that it is nx1 but scalars and mxn are OK
    if spot.ndim==1:
        spot_final = spot.reshape(-1, 1)
    else:
        spot_final = spot

    # Spreads. Check that 1xn but scalars and mxn are OK
    if spreads.ndim==1:
        spreads_final = spreads.reshape(1, -1)
    else:
        spreads_final = spreads

    # Cash_flows. Check that it is nx1 but scalars and mxn are OK
    if cash_flows.ndim == 1:
        cash_flows_final = cash_flows.reshape(-1, 1)
    else:
        cash_flows_final = cash_flows

    # Criterion: optionally, only include some cashflows
    if criterion is None:
        criterion = np.ones(np.size(cash_flows,0),dtype=bool)

    # Discount Factors
    discount_factors = (1+spot_final[criterion,:]+spreads_final)**-t[criterion,:]

    # Discounted cash flows
    values = np.sum(cash_flows_final[criterion,:] * discount_factors,axis=0)

    return values

def run_simulations_scenario_loop(cash_flows : ndarray, spreads : ndarray, spot : ndarray)-> ndarray:

    """Perform simulations looping through the scenarios in the typical approach."""

    scenarios=[]  #Initialise list

    for i,spot0 in enumerate(spot.T):

        if i % 1000 == 0:
            print(f"Processing simulation {i}...")

        values = value_portfolio(cash_flows, spreads, spot0)

        # Append result to scenarios list5
        scenarios.append(values)

    return np.sum(np.array(scenarios),axis=1)

def run_simulations_asset_loop_2A(cash_flows : ndarray, spreads : ndarray, spot : ndarray)->ndarray:

    """Run simulations by looping through assets and, for each asset, applying all interest rate stresses"""

    scenarios = []

    for i,(cash_flows0,spread0) in enumerate(zip(cash_flows.T,spreads)):

        if i % 5 == 0:
            print(f"Processing asset {i}...")

        values = value_portfolio(cash_flows0, spread0, spot)

        scenarios.append(values)

    return np.sum(np.array(scenarios),axis=0)

def run_simulations_asset_loop_2B(cash_flows : ndarray, spreads : ndarray, spot : ndarray)->ndarray:

    """Run simulations by looping through assets and, for each asset, applying all interest rate stresses.
    Improve efficiency by only considering non-zero cashflows."""

    scenarios = []

    for i,(cash_flows0,spread0) in enumerate(zip(cash_flows.T,spreads)):

        if i % 5 == 0:
            print(f"Processing asset {i}...")

        # Find non-zero cashflows
        crit = cash_flows0 !=0

        values = value_portfolio(cash_flows0, spread0, spot, criterion = crit)

        scenarios.append(values)

    return np.sum(np.array(scenarios),axis=0)







