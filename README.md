Here are the files that I have been running:

**main.py**
- Gets the best two-limit policy from twoLimitPolicies.py
- Runs lookahead.py, with the chosen two-limit policy as the default

**policySimulations.py**
- Includes a Location class to track data for each city
- BasePolicy class (each instance is a simulation of using a policy, use step() function to move the simulation forward one day
- There are several subclasses of the Base Policy class; each one intended to simulate a different type of policy

**twoLimitPolicies.py**
- Method for comparing different two-limit policies and choosing the best
- Method for finding the value-to-go using a specific two-limit policy

**lookahead.py**
- Finds a more precise value-to-go by choosing policies that maximize J(x) for the first k steps and switching to a default, two-limit policy
-  Value to go: J(x, k) = max{H(u, k) - transferCost(x-->u)}
-  Helper function: H(u, k) = E{stageValue(w) + J(f(u, w), k-1)}

**twocity_numerical.py**
- Stage 1: Gets the optimal fleet size to maximize the all-time total profit
- Stage 2: Gets the exact precise optimal policy and value-to-go function at every step for two cities
- Runs in exponential time

**threecity_numerical_base.py**
- Gets the exact precise optimal policy and value-to-go function at every step or three cities
- Runs in exponential time

**threecity_numerical_advanced.py**
- Consider stage 2, find the optimal fleet size for three cities case as well

**threecity_numerical_plot.py**
- Plot based on threecity_numeric_base.py
