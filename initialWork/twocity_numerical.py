import numpy as np

# Parameters
T = 5  # Planning horizon
n = 5  # Total number of cars
max_n = 20 # Maximum number of total cars
h = 1   # Daily operating cost per car
k = 10  # Cost for transferring one car between two cities
r1 = 30 # Rental rate for type-1
r2 = 20 # Rental rate for type-2

# Initial allocation
x_T = 10

# Demand simulation function (simplified)
def simulate_demand():
    # Returns a tuple of demands (D11, D12, D21, D22)
    return np.random.poisson(3), np.random.poisson(2), np.random.poisson(4), np.random.poisson(1)

# Revenue calculation function
def calculate_revenue(yt, D11, D12, D21, D22):
    inter_city_rental = r1 * (min(yt, D11) + min(n - yt, D21))
    local_rental = r2 * (min(max(yt - D11, 0), D12) + min(max(n - yt - D21, 0), D22))
    return inter_city_rental + local_rental

# Dynamic programming function
def V(t, xt):
    if t == 0:
        return 0
    max_income = -np.inf
    for yt in range(n+1):
        D11, D12, D21, D22 = simulate_demand()
        revenue = calculate_revenue(yt, D11, D12, D21, D22)
        transfer_cost = k * abs(yt - xt)
        expected_income = revenue - transfer_cost + V(t-1, yt - min(yt, D11) + min(n - yt, D21))
        max_income = max(max_income, expected_income)
    return max_income

# Main simulation
def main():
    max_profit = -np.inf
    best_n = best_x_T = 0
    for n in range(1, max_n+1):  # Trying different fleet sizes
        for x_T in range(n+1):  # Trying different initial allocations
            profit = V(T, x_T) - h * n * T
            if profit > max_profit:
                max_profit = profit
                best_n, best_x_T = n, x_T
    print(f"Optimal fleet size: {best_n}, Initial allocation in city 1: {best_x_T}, Max Profit: {max_profit}")

if __name__ == "__main__":
    main()
