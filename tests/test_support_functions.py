import numpy as np

from src.support_functions import spot_to_forward, forward_to_spot, get_correlated_random_shocks


def test_spot_to_forward_round_trip_conversion():
    """
    Test that converting Spot -> Forward -> Spot returns the original values.
    """
    original_spot = np.array([0.04, 0.045, 0.05, 0.055, 0.06]).reshape(-1,1)

    # 1. Spot to Forward
    fwd = spot_to_forward(original_spot)

    # 2. Forward back to Spot
    recovered_spot = forward_to_spot(fwd)

    # Assert they are equal within a very small tolerance
    np.testing.assert_allclose(original_spot, recovered_spot, atol=1e-10)

def test_spot_to_forward_flat_curve():
    """
    If the spot curve is flat at 5%, the forward curve must also be flat at 5%.
    """
    flat_spot = np.array([0.05, 0.05, 0.05, 0.05])
    fwd = spot_to_forward(flat_spot)

    np.testing.assert_allclose(fwd, 0.05, atol=1e-10)

def test_spot_to_forward_custom_time_steps():
    """
    Test that the functions handle non-standard time steps (e.g. 0.5yr, 1yr, 2yr).
    """
    spots = np.array([0.03, 0.04, 0.05]).reshape(-1,1)
    times = np.array([0.5, 1.0, 2.0])  # Half year, One year, Two years

    fwds = spot_to_forward(spots, t=times)
    recovered = forward_to_spot(fwds, t=times)

    np.testing.assert_allclose(spots, recovered, atol=1e-10)

def test_spot_to_forward_second_element():
    """
    Test second forward in sequence
    """
    spots = np.array([0.03, 0.04, 0.05]).reshape(-1,1)
    times = np.array([0.5, 1.0, 2.0])  # Half year, One year, Two years

    fwd = spot_to_forward(spots, t=times)[1]
    expected = (((1+spots[1])**times[1])/((1+spots[0])**times[0]))**(1/(times[1]-times[0]))-1

    np.testing.assert_allclose(fwd, expected, atol=1e-10)

def test_spot_to_forward_first_element_equality():
    """
    The 1st spot rate and 1st forward rate must always be identical at t1.
    """
    spots = np.array([0.042, 0.051, 0.058])
    forwards = spot_to_forward(spots)

    assert forwards[0] == spots[0]


def test_get_correlated_random_shocks_correct_correlation():
    """
    Test that the generated shocks actually reflect the requested correlation.
    Note: Use a large num_sims to reduce sampling error.
    """
    corr_input = 0.6
    num_sims = 100000
    mock_spot = np.zeros(10)  # 10 points on the curve

    shocks = get_correlated_random_shocks(corr_input, num_sims, mock_spot)

    # Calculate correlation matrix between the first two rows (time points)
    emp_corr = np.corrcoef(shocks[0, :], shocks[1, :])[0, 1]

    # Assert within a 1% tolerance for large samples
    np.testing.assert_allclose(emp_corr, corr_input, atol=0.01)

def test_get_correlated_random_shocks_variance_is_unit():
    """
    Ensure the shocks still have a standard deviation of 1 (Unit Variance).
    """
    shocks = get_correlated_random_shocks(0.5, 50000, np.zeros(5))

    # Standard deviation should be 1.0
    np.testing.assert_allclose(np.std(shocks, axis=1), 1.0, atol=0.01)