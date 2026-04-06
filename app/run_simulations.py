import time
import numpy as np
import matplotlib.pyplot as plt

from src.valuation_engine import get_asset_data, simulate_spot_curve, run_simulations_scenario_loop, \
    run_simulations_asset_loop_2A, run_simulations_asset_loop_2B

def main():

    """
        Demonstration of the increase in speed of running optimised code.
    """

    #
    # 0. Settings
    #
    num_sims = 10000
    selected_percentile = 99.5
    forward_volatility = 0.0075
    forward_shock_correlation = 0.6
    plot_spot_curves = False

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
    spot_sims = simulate_spot_curve(spot.to_numpy(),vol=np.array(forward_volatility),num_sims=num_sims,correlation=forward_shock_correlation)
    end_time = time.time()
    print(f'Time taken: {end_time - start_time} seconds for {num_sims} simulations')

    def do_plot():
        """Plot Spot Impacts"""
        step = 12  # keep 1 point per year
        curves_ds = spot_sims.T[:, ::step]

        # Plot spot curves
        plt.figure(figsize=(12, 6))
        plt.plot(curves_ds.T, color='steelblue', alpha=0.01)  # low alpha to show density
        plt.title("Random Interest Rate Spot Curves")
        plt.xlabel("Year")
        plt.ylabel("Spot Rate")
        plt.grid(True, alpha=0.3)
        plt.show()

    if plot_spot_curves:
        do_plot()

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
