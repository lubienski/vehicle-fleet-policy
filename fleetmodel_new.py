import numpy as np
from scipy.optimize import minimize

# Define your parameters
t = 1.0  # Cost of transferring one vehicle
rlow = 1.0  # Low penalty
rhigh = 2.0  # High penalty

# Define the values for xa, xb, xc, ua, ub, uc, waa, wab, wac, ...
xa = 10
xb = 20
xc = 30
ua = 5
ub = 15
uc = 25
waa = 1
wab = 2
wac = 3

# Define functions for cost and constraints
def cost_function(u, x, w):
    # Calculate cost based on the provided formula
    w_prime = calculate_w_prime(u, w)
    cost = 0.5 * t * np.sum(np.abs(u - x)) - rlow * np.sum(np.maximum(0, w_prime)) - rhigh * np.sum(np.minimum(0, w_prime))
    return cost

def calculate_w_prime(u, w):
    w_prime = np.zeros_like(w)
    for i in range(w.shape[0]):
        for j in range(w.shape[1]):
            w_prime[i, j] = max(0, min(w[i, j] + np.sum(w[i, :]) - u[i], u[i]) - (w[i, j] + np.sum(w[i, :])))
    return w_prime

# Define initial values for xk and uk
xk = np.array([xa, xb, xc])
uk = np.array([ua, ub, uc])

# Define demand matrix W
W = np.array([[waa, wab, wac], [wba, wbb, wbc], [wca, wcb, wcc]])

# Set up bounds and constraints
bounds = [(0, np.inf)] * len(uk)  # Bounds for uk variables
constraints = {'type': 'eq', 'fun': lambda u: np.sum(u) - np.sum(xk)}  # Constraint for the sum of u to be equal to the sum of xk

# Solve the optimization problem
result = minimize(lambda u: cost_function(u, xk, W), uk, bounds=bounds, constraints=constraints)

# Extract the optimal solution
optimal_uk = result.x

print("Optimal uk:", optimal_uk)
