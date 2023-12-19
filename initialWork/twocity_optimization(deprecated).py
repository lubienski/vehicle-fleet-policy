import numpy as np
from scipy.optimize import minimize

T = 5  # Planning horizon, for example, 30 days
h = 5   # Daily operating cost per car
k = 10  # Cost for transferring one car between two cities
r1 = 30 # Rental rate for type-1
r2 = 20 # Rental rate for type-2
n = 10

def simulate_demand(i, j):
    # Returns demand for city i and type j customer
    # This is a placeholder. Replace with an actual distribution.
    return np.random.poisson(lam=(i+j)*2)

def calculate_revenue(yt, D11, D12, D21, D22):
    inter_city_rental = r1 * (min(yt, D11) + min(n - yt, D21))
    local_rental = r2 * (min(max(yt - D11, 0), D12) + min(max(n - yt - D21, 0), D22))
    return inter_city_rental + local_rental

def V(t, xt, n):
    if t == 0:
        return 0
    max_income = -np.inf
    for yt in range(n+1):
        D11 = simulate_demand(1, 1)
        D12 = simulate_demand(1, 2)
        D21 = simulate_demand(2, 1)
        D22 = simulate_demand(2, 2)
        revenue = calculate_revenue(yt, D11, D12, D21, D22)
        transfer_cost = k * abs(yt - xt)
        next_xt = yt - min(yt, D11) + min(n - yt, D21)
        expected_income = revenue - transfer_cost + V(t-1, next_xt, n)
        max_income = max(max_income, expected_income)
    return max_income

def optimize_fleet_size():
    def objective(vars):
        n, x_T = int(vars[0]), int(vars[1])
        return -(V(T, x_T, n) - h * n * T)  # Negative profit for minimization

    initial_guess = [10, 5]  # Initial guess for n and x_T
    bounds = [(1, 50), (0, 50)]  # Bounds for n and x_T
    result = minimize(objective, initial_guess, bounds=bounds, method='SLSQP')
    return result.x

def main():
    optimal_n, optimal_x_T = optimize_fleet_size()
    print(f"Optimal fleet size: {int(optimal_n)}, Initial allocation in city 1: {int(optimal_x_T)}")

if __name__ == "__main__":
    main()
