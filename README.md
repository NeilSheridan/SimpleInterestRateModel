Python Code Example
The code demonstrates a simple interest to demonstrate a simple stochastic interest rate risk model inspired by the SBA stresses. Using three different versions of the simulator I show that, by making simple changes to the code, one can dramatically speed up the running of the code (c.25 times increased speed).

Model Dimensions
Simulations: 		100,000
Assets: 			52
Cash-flow projections: 1200 months.
Stress:			99.5th percentile

Results
Step	Description	Observed Time (s)	Realistic Time*
	Simulate 100,000 spot curves	16	16s
1	Loop through simulations: 	246	3.5 hours
2A	Loop through assets: 	252	3.5 hours
2B	Loop through assets (sparse overlay): 	10	8 minutes
* The realistic time is extrapolated from observed for a more realistic portfolio of 2,600 assets, a 50-fold increase.

Using all three cases, 1, 2A and 2B, the 99.5th percentile fall in market value is c.11% of the start market value.

Interest Rate Shock Model
Initially, the model simulates 100,000 spot curves. Each monthly forward rate is shocked by correlated Normally distributed shocks. Illustrative volatility of 0.75% (chosen such that 2 standard deviations is broadly in line with the BMA SBA 1.5% IR shock) and a 60% correlation between forwards is assumed for illustration. 
This calculation is fully vectorised and is therefore completed in a single step. The time taken, 16s, is small and is not dependent on the size of the portfolio. 
A weakness of using a fixed volatility in that the shifts are largely parallel beyond the short term. A simple extension to increase control would be to use a volatility vector increasing volatility with term. 
More flexibility could also be introduced by increasing the number of correlated factors or using a principal components model. 

Asset Valuation
I test three valuation approaches 

Methodology 1: Typical Simulation Loop
For each of the 100,000 simulations, using matrix multiplication to obtain a portfolio value using the formula: 
Value(k)=ΣΣ(CFṡ∙(1+IR(k)+spread)^(-t))
Where CFs (1200x52) is the cash-flow matrix
IR(k) (1200x1) is the spot curve for scenario k=1…100,000
spread (1x52) is the vector of asset spreads
t (1200x1) is the vector of cashflow terms.
Summation is over the 52 asset columns and 1200 cashflow rows

However, the inner portfolio calculations are fully vectorised in Python therefore there is only one explicit loop in the code across the 100,000 IR curves.
The 99.5th percentile is then the 99.5th percentile loss for Value.

Methodology 2A: Asset Loop
The model loops through each asset.
For each asset, all 100,000 interest rate simulations are applied.
Using matrix multiplication so, as before, there are no explicit inner loops.
Under this approach, all 100,000 simulations need to be recorded for each asset
Value(l,:)=Σ(CFs ̇(l)∙(1+IR+spread(l))^(-t))
Where CFs (1200x1) is the cash-flow matrix for asset l=1…52
IR (1200x100,000) is the spot curve for all scenarios
spread(l) the asset spread for l
t (1200x1) is the vector of cashflow terms.
Summation is over the 1200 cashflow rows
Value(l,:) is now 1x100,000 instead of a scalar 
i.e. Value(l,:) forms one row of Value(:,:) (52x100,000)
To determine the 99.5th loss take 99.5th percentile loss of the sum of the columns of Value. 

Methodology 2B: Asset Loop With Heuristics
The model loops through each asset as with 2A above. However, we now consider the heuristic observation that typical assets have << 1200 non-zero cash-flows. Therefore, for each asset, the model determines which cash-flows are non-zero and applies the appropriate spots only to these cashflows. 

Conclusion
Changing from a 100,000-simulation loop to a 52 asset loop initially results in a small increase in run time. However, the asset simulation approach facilitates a simple refinement to the calculation based on the features of the individual asset. These changes result in a dramatic increase in run time. 

Checking/Testing/Governance
The following tests have been applied to the model:
	Unit Tests have been developed for selected functions. These are in the \tests folder. As further development these would be extended to cover all parts of the code. 
	The loss result, 11% is broadly in line with a rough back of the envelope 99.5th percentile 2.56 x 0.75% x 10=19.2% assuming an average duration of 10 years and a parallel shift but a reasonable  reduction because of the 60% diversification factor applied.
	The model has been loaded to source control (GitHub) to ensure change control.
