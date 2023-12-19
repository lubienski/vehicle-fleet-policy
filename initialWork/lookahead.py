from policySimulations import *
from twoLimitPolicies import *

class Lookahead:
    def __init__(self, defaultPolicyLimits):
        self.lower = defaultPolicyLimits[0]
        self.upper = defaultPolicyLimits[1]
        self.valuesToGo = {}
        self.policy = {}
        self.expectations = {}
        self.numTrials = 50
        self.numDefaultTrials = 30
        self.numDefaultSteps = 300

    def __str__(self):
        summary = ""
        for (x, k) in self.valuesToGo.keys():
            if k >= 2:
                if (x, k) in self.policy.keys():
                    summary += f"k: {k} x: {x} u(x): {self.policy[(x, k)]} J(x): {round(self.valuesToGo[x, k])} \n"
                else:
                    summary += f"k: {k} x: {x} J(x): {round(self.valuesToGo[x, k])} \n"
        return summary
    

    '''
        J(x, k) = max_u { H(u, k) - transferCost(x-->u) }
        - Find all reasonable u's
        - Get H(u, k) (expected value-to-go starting from u)
        - Subtract cost of transfer from x to u
        - Select u with the largest value-to-go
    '''
    def J(self, x, k):
        if (x, k) in self.valuesToGo.keys():
             return self.valuesToGo[(x, k)]
        if k==0:
            valueToGo = twoLimitValueToGo(x, self.lower, self.upper, self.numDefaultTrials, self.numDefaultSteps)
            self.valuesToGo[(x, k)] = valueToGo
            return valueToGo
       
       
        (a, b, c) = x
        n = sum(x)
        center = n//3

        actionCandidates = [(u_a, u_b, u_c) 
            for u_a in range(min(a, center), max(a, center) + 1) 
            for u_b in range(min(b, center), max(b, center) + 1) 
            for u_c in range(min(c, center), max(c, center) + 1)]
        actionCandidates = list(filter(lambda state: sum(state) == n, actionCandidates))
        actionValues = {}

        for u in actionCandidates:
            actionValues[u] = self.H(tuple(sorted(u)), k)
            simulation = ConstantPolicy(x, u)
            simulation.generatePlan()
            transferCost = simulation.cost(simulation.plan) # Cost to get from x to u
            actionValues[u] -= transferCost

        bestAction = max(actionValues, key=actionValues.get)
        self.policy[(x, k)] = bestAction
        self.valuesToGo[(x, k)] = actionValues[bestAction]

        return (actionValues[bestAction])


      
    '''
    H(u, k) = E[stageValue(w) + J(f(u, w), k-1)]

    - Build many simulations(using the "do nothing" base policy with starting state u)
    - Move all simulations one step forward
    - Get the stage profit of each simulation
    - Get J(nextState, k-1)
    - Return expected value of stage profit + J(nextState, k-1)
    '''

    def H(self, u, k):
        if (u, k) in self.expectations.keys():
            return self.expectations[(u, k)]
        
        profitSum = 0
        trials = [BasePolicy(u) for _ in range(self.numTrials)]
        for t in trials:
            t.step()
            nextState = t.state()
            stageValue = t.profit
            valueToGo = self.J(tuple(sorted(nextState)), k-1)
            profitSum += stageValue + valueToGo
        
        self.expectations[(u, k)] = profitSum/self.numTrials
        return self.expectations[(u, k)]
