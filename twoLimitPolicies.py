from policySimulations import *

def exploreTwoLimitPolicies(currState, numTrials, numSteps):
    profits = {}
    [a, b, c] = currState
    lowerLimits = list(range(a-7, a-2))
    upperLimits = list(range(a+3, a+8))
    
    for lower in lowerLimits:
        for upper in upperLimits:
            profits[(lower, upper)] = twoLimitValueToGo(currState, lower, upper, numTrials, numSteps)

    bestRange = max(profits, key=profits.get)
    return (bestRange, profits[bestRange])

def twoLimitValueToGo(state, lower, upper, numTrials, numSteps):
    profitSum = 0
    trials = [TwoLimitPolicy(state, lower, upper) for _ in range(numTrials)]

    for t in trials:
        for _ in range(numSteps):
            t.step()
        profitSum += t.profit
    return profitSum/numTrials