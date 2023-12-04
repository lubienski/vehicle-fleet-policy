import numpy as np
from scipy.optimize import minimize

# Fleet size
c_n = 6
# Days simulated
c_t = 3

# Low profit
r_low = 1
# High profit
r_high = 2
# Transit cost
r_t = 1

# Initial X
x_0 = np.array([3, 1, 2])

# Find action space
U_space = []

for ua in range(c_n + 1):
    for ub in range(c_n - ua + 1):
        uc = c_n - ua - ub
        U_space.append(np.array([ua, ub, uc]))

# Simulate the demand w, I regard it as poisson distribution
def simulate_demand():
    w = np.array([[np.random.poisson(3),np.random.poisson(4),np.random.poisson(1)],
                    [np.random.poisson(2),np.random.poisson(3),np.random.poisson(2)],
                    [np.random.poisson(1),np.random.poisson(4),np.random.poisson(3)]])
    return w

# State transition function
def f(x, u, w):
    x_next = np.array([0, 0, 0])
    x_next[0] = (max(0, min(w[0,1]+w[0,2]+w[0,0], u[0]) - (w[0,1]+w[0,2])) + 
                 max(0, min(w[1,2]+w[1,0],u[1])-w[1,2]) + min(w[2,0], u[2]))
    x_next[1] = (max(0, min(w[1,2]+w[1,0]+w[1,1], u[1]) - (w[1,2]+w[1,0])) + 
                 max(0, min(w[2,0]+w[2,1],u[2])-w[2,0]) + min(w[0,1], u[0]))
    x_next[2] = (max(0, min(w[2,0]+w[2,1]+w[2,2], u[2]) - (w[2,0]+w[2,1])) +
                 max(0, min(w[0,1]+w[0,2],u[0])-w[0,1]) + min(w[1,2], u[1]))
    return x_next

# Cost and revenue calculation function
def g(x, u, w):
    cost = 0.5 * r_t * np.sum(np.abs(u - x))
    low_profit = r_low * (max(0, min(w[0,1]+w[0,2]+w[0,0], u[0]) - (w[0,1]+w[0,2])) + 
                          max(0, min(w[1,2]+w[1,0]+w[1,1], u[1]) - (w[1,2]+w[1,0])) +
                          max(0, min(w[2,0]+w[2,1]+w[2,2], u[2]) - (w[2,0]+w[2,1])))
    high_profit = r_high * (min(w[0,1], u[0]) + max(0, min(w[0,1]+w[0,2],u[0])-w[0,1]) + 
                            min(w[1,2], u[1]) + max(0, min(w[1,2]+w[1,0],u[1])-w[1,2]) +
                            min(w[2,0], u[2]) + max(0, min(w[2,0]+w[2,1],u[2])-w[2,0]))
    return low_profit + high_profit - cost

optimal_actions = {} 
optimal_states = {}
max_incomes = {}
demands = {}

# Dynamic programming function
def V(t, x):
    if t == c_t+1:
        return 0
    max_income = -np.inf
    w = simulate_demand()
    best_u = None
    for u in U_space:
        x_next = f(x,u,w)
        expected_income = g(x,u,w) + V(t+1, x_next)
        if expected_income > max_income:
            max_income = expected_income
            best_u = u

    demands[t] = w
    max_incomes[t] = max_income
    optimal_actions[t] = best_u
    optimal_states[t] = x
    
    return max_income

if __name__ == "__main__":
    max_income = V(0, x_0)
    for t in range(0, c_t + 1):
        print(f"Time period {t}:\n Demand {demands[t]}, State {optimal_states[t]}, Optimal Action {optimal_actions[t]}, Cost-to-go {max_incomes[t]}")