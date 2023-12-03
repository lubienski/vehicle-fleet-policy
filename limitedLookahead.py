import time
from policySimulations import *
from twoLimitPolicies import *

def main():
    a = b = c = 60
    initState = (a, b, c) # Assume system is symmetric
    n = sum(initState)

    # comparePolicies(initState)



    # bestTwoLimitPolicy = exploreTwoLimitPolicies(initState, 100, 365)
    bestTwoLimitPolicy = (56, 66)
    print(bestTwoLimitPolicy)

    X = set([
        tuple(sorted((x_a, x_b, x_c)))
        for x_a in range(n+1) 
        for x_b in range(n+1) 
        for x_c in range(n+1)
    ])
    X = set(filter(lambda state: sum(state) == n, X))

    start = time.time()
    kStepLookahead(initState, (55, 65), X, 2)
    end = time.time()
    print((end - start), " seconds")
    

'''
Explore all reasonable policies within a restricted state space.
'''
def kStepLookahead(initState, defaultPolicyLimits, X, k):
    n = sum(initState)
    a = initState[0]
    restrictSizes = [5, 15, 25]

    X = set([
            tuple(sorted((x_a, x_b, x_c)))
            for x_a in range(n+1) 
            for x_b in range(n+1) 
            for x_c in range(n+1)
        ])
    X = set(filter(lambda state: sum(state) == n, X))


    largeSpace = set(filter(lambda state: min(state) > a-restrictSizes[2] and max(state) < a+restrictSizes[2], X))
    mediumSpace = set(filter(lambda state: min(state) > a-restrictSizes[1] and max(state) < a+restrictSizes[1], largeSpace))
    smallSpace = set(filter(lambda state: min(state) > a-restrictSizes[0] and max(state) < a+restrictSizes[0], mediumSpace))

    print(len(X), len(largeSpace), len(smallSpace))
    print(smallSpace)
    (lower, upper) = defaultPolicyLimits
    valuesToGo = {}
    optimalPolicy = {}

    for state in smallSpace:
        val = twoLimitValueToGo(state, lower, upper, 10, 50)
        valuesToGo[state] = val
        optimalPolicy[state] = []
    for state in mediumSpace - smallSpace:
        if spaceFilter(state, 2):
                    val = twoLimitValueToGo(state, lower, upper, 5, 50)
                    valuesToGo[state] = val
                    optimalPolicy[state] = []
    for state in mediumSpace - valuesToGo.keys():
        neighbor = map(lambda x: round(x/2)*2, state)
        if neighbor in valuesToGo.keys():
            valuesToGo[state] = valuesToGo[neighbor]
            optimalPolicy[state] = []
    for state in largeSpace - mediumSpace:
        if spaceFilter(state, 4):
            val = twoLimitValueToGo(state, lower, upper, 3, 50)
            valuesToGo[state] = val
            optimalPolicy[state] = []
    for state in largeSpace - valuesToGo.keys():
        neighbor = map(lambda x: round(x/4)*4, state)
        if neighbor in valuesToGo.keys():
            valuesToGo[state] = valuesToGo[neighbor]                
            optimalPolicy[state] = []
    for state in X - valuesToGo.keys():
        valuesToGo[state] = valuesToGo[initState] - resetCost(state, initState)
        optimalPolicy[state] = []

    print("initialVTG:")
    for key, v in valuesToGo.items():
        print(key, v)

    for i in range(k):
        print(len(X), len(valuesToGo))
        (valuesToGo, optimalPolicy) = updateValuesToGo(X, valuesToGo, optimalPolicy)

    print("OPTIMAL POLICY:")
    for initState in sorted(largeSpace):
            print(f"x = {initState} --> u = {optimalPolicy[initState]}")
    
    return (optimalPolicy, valuesToGo)


def spaceFilter(state, mod):
    return len(list(filter(lambda x: x % mod == 0, state))) == 3

def resetCost(state, initState):
    resetSimulation = ConstantPolicy(state, initState)
    resetSimulation.generatePlan()
    cost = resetSimulation.cost(resetSimulation.plan)
    return cost
   
def updateValuesToGo(X, valuesToGo, optimalPolicy):
    U = X
    expectations = {}
    numTrials = 20
    for u in U:
        trials = [BasePolicy(u) for _ in range(numTrials)]
        profitSum = 0
        for t in trials:
            t.step()
            nextState = tuple(sorted(t.state()))
            profitSum += valuesToGo[nextState]
        expectations[u] = profitSum/numTrials

    for state in valuesToGo.keys():
        (action, value) = getBestTransfer(state, expectations)
        optimalPolicy[state] = action
        valuesToGo[state] = value
    
    return (valuesToGo, optimalPolicy)

def getBestTransfer(state, expectations):
    (a, b, c) = state
    n = sum(state)
    center = n//3

    actionCandidates = [(u_a, u_b, u_c) 
        for u_a in range(min(a, center), max(a, center) + 1) 
        for u_b in range(min(b, center), max(b, center) + 1) 
        for u_c in range(min(c, center), max(c, center) + 1)]
    actionCandidates = list(filter(lambda state: sum(state) == n, actionCandidates))

    values = {}
    for u in actionCandidates:
        simulation = ConstantPolicy(state, u)
        simulation.generatePlan()
        g = simulation.cost(simulation.plan) # Cost to get from x to u
        J = expectations[tuple(sorted(u))] # Expected value to go from u
        values[u] = J - g
    
    bestAction = max(values, key=values.get)
    return (bestAction, values[bestAction])

    
if __name__ == "__main__":
    main()
