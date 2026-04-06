import time
import numpy as np

from src.valuation_engine import get_asset_data, simulate_spot_curve, run_simulations_scenario_loop, \
    run_simulations_asset_loop_2A, run_simulations_asset_loop_2B

def main():

    """
        Demonstration of the increase in speed of running optimised code.
    """

    #
    # 0. Settings
    #
    num_sims = 100000
    selected_percentile = 99.5
    forward_volatility = 0.0075
    forward_shock_volatility = 0.9

    #
    # A. Get asset data
    #
    print(f'\n\n*** Loading Asset Data ***')
    assets, cash_flows, spot = get_asset_data(r'../data/Bonds1.xlsx')
    num_assets = len(assets)

    #
    # B. Get interest rate scenarios
    #
    print(f'\n\n*** Simulating {num_sims} Interest Rate Shocks ***')
    start_time = time.time()
    spot_sims = simulate_spot_curve(spot.to_numpy(),vol=np.array(forward_volatility),num_sims=num_sims,correlation=forward_shock_volatility)
    end_time = time.time()
    print(f'Time taken: {end_time - start_time} seconds for {num_sims} simulations')

    #
    # C. Run simulations and record time taken - loop through SIMULATIONS
    #
    print(f'\n\n*** Calculating Portfolio Impacts - Approach1 ***')
    simulations_to_perform = num_sims
    start_time = time.time()
    simulations = run_simulations_scenario_loop(cash_flows.to_numpy(), assets['Spread'].to_numpy(), spot_sims[:,:simulations_to_perform])
    end_time = time.time()

    def present_results(start_time,end_time,simulations,num_sims,simulations_to_perform):
        """Show results and time taken"""
        result_value = np.percentile(simulations, 100 - selected_percentile)
        result_loss = result_value - np.sum(assets['Price'])
        print(f'Result (Base): {np.sum(assets['Price'])}')
        print(f'Result ({selected_percentile}th percentile): {result_value}')
        print(f'Loss ({selected_percentile}th percentile): {result_loss}')
        print(f'Loss% ({selected_percentile}th percentile): {result_loss/(result_value-result_loss)*100}%')
        print(f'Time taken: {end_time - start_time} seconds for {simulations_to_perform} simulations')
        print(f'Estimated Total Time: {(end_time - start_time) * num_sims/simulations_to_perform/60} minutes')

    present_results(start_time, end_time, simulations,num_sims,simulations_to_perform)

    #
    # D. Run simulations and record time taken - loop through ASSETS
    #
    print(f'\n\n*** Calculating Portfolio Impacts - Approach 2A ***')
    assets_to_consider = num_assets
    start_time = time.time()
    simulations = run_simulations_asset_loop_2A(cash_flows.to_numpy()[:, :assets_to_consider], assets['Spread'].to_numpy()[:assets_to_consider], spot_sims)
    end_time = time.time()
    present_results(start_time, end_time, simulations, num_assets, assets_to_consider)

    #
    # E. Run simulations and record time taken - loop through ASSETS, BUT ignore zero cashflows
    #
    print(f'\n\n*** Calculating Portfolio Impacts - Approach 2B ***')
    assets_to_consider = num_assets
    start_time = time.time()
    simulations = run_simulations_asset_loop_2B(cash_flows.to_numpy()[:, :assets_to_consider],
                                                assets['Spread'].to_numpy()[:assets_to_consider], spot_sims)
    end_time = time.time()
    present_results(start_time, end_time, simulations, num_assets, assets_to_consider)

if __name__ == '__main__':
    main()
