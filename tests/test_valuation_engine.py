import numpy as np

from src.valuation_engine import get_asset_data, value_portfolio

def test_value_portfolio():
    """
    Check that the calculated value of assets is close to the data value.
    """

    # 1. Get asset data
    assets, cash_flows, spot = get_asset_data('../data/Bonds1.xlsx')

    # 2. Get actual value of assets
    expected=sum(assets['Price'])

    # 3. Calculate using valuator
    obtained = sum(value_portfolio(cash_flows.to_numpy(), assets['Spread'].to_numpy(), spot.to_numpy()))

    # Check if approximately equal
    np.testing.assert_almost_equal(expected,obtained, decimal=-1)
