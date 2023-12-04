import numpy as np
from scipy.optimize import minimize
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import MaxNLocator

# # Fleet size
# c_n = 6
# # Days simulated
# c_t = 3

# Low profit
r_low = 1
# High profit
r_high = 2
# Transit cost
r_t = 1

# Initial X
x_0 = np.array([3, 1, 2])

# Find action space
def get_U_space(c_n):
    U_space = []

    for ua in range(c_n + 1):
        for ub in range(c_n - ua + 1):
            uc = c_n - ua - ub
            U_space.append(np.array([ua, ub, uc]))
    return U_space

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
def V(c_t, U_space, t, x):
    if t == c_t+1:
        return 0
    max_income = -np.inf
    w = simulate_demand()
    best_u = None
    for u in U_space:
        x_next = f(x,u,w)
        expected_income = g(x,u,w) + V(c_t, U_space, t+1, x_next)
        if expected_income > max_income:
            max_income = expected_income
            best_u = u

    demands[t] = w
    max_incomes[t] = max_income
    optimal_actions[t] = best_u
    optimal_states[t] = x
    
    return max_income


def measure_exec_time(c_t, U_space):
    start_time = time.time()
    max_income = V(c_t, U_space, 0, x_0)
    end_time = time.time()
    return end_time - start_time


exec_values = []
c_t_values = list(range(2,6))
c_n_values = list(range(2,6))

for c_t in c_t_values:
    for c_n in c_n_values:
        U_space = get_U_space(c_n)
        exec_time = measure_exec_time(c_t, U_space)
        exec_values.append(exec_time)

# Create a 3D line plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

c_t_values = np.array(c_t_values)
c_n_values = np.array(c_n_values)
exec_values = np.array(exec_values)
X, Y = np.meshgrid(c_t_values, c_n_values)
Z = np.array(exec_values).reshape(len(c_n_values), len(c_t_values))

colormap = cm.get_cmap('viridis')

ax.plot_surface(X, Y, Z, cmap=colormap, alpha=0.6)
scatter = ax.scatter(X, Y, Z, c=Z, cmap=colormap, marker='o', alpha=1, edgecolor='k')

ax.set_xlabel('Days simulated')
ax.set_ylabel('Fleet size')
ax.set_zlabel('Codes execution time (in Seconds)')
ax.set_title('Codes Execution Time vs. Days Simulated and Fleet Size')
ax.legend()

color_bar = fig.colorbar(scatter, ax=ax, label='Codes Execution Time (in Seconds)')
color_bar.set_alpha(1)
color_bar.draw_all()

ax.xaxis.set_major_locator(MaxNLocator(integer=True))
ax.yaxis.set_major_locator(MaxNLocator(integer=True))

plt.show()
