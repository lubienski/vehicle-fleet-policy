import random
import numpy as np
from scipy.stats import lognorm

'''
Location object created for each city.
0 ~ A
1 ~ B
2 ~ C 
'''
class Location:
    def __init__(self, vehicle_count, index, lowerLimit=None, upperLimit=None):
        self.index = index # 0, 1, or 2
        self.name = ['A', 'B', 'C'][index]
        self.lower = lowerLimit
        self.upper = upperLimit

        self.count = vehicle_count
        self.incoming = 0   # Vehicles on their way to this city

    def __str__(self):
        return f"{self.name} ({self.count})"
    
    def processNewCars(self):
        self.count += self.incoming
        self.incoming = 0

'''
Simulation for the default model with no transfers (u = x)
'''
class BasePolicy:
    def __init__(self, state):
        self.n = sum(state) # fleet size
        self.A = Location(state[0], 0)
        self.B = Location(state[1], 1)
        self.C = Location(state[2], 2)
        self.initCounts = state
        self.locs = [self.A, self.B, self.C]

        self.demandFunction = lambda: round(np.random.lognormal(3, 0.25)) # Same demand function for all 9 demands
        self.lowerRate = 100 # Price to rent a car locally
        self.higherRate = 150 # Price to rent a car and return it in a different city
        self.transferCost = 50  # Cost to transfer each vehicle overnight
        self.policyName = "Base      "

        self.plan = [0, 0, 0] # Planned increase at each city
        self.W = None   # Matrix of demands. W[i][j] is the demand from city i to city j
        self.profit = 0 # Total profit the company has made so far

    def state(self):
        return (self.A.count, self.B.count, self.C.count)
    
    def showState(self):
        print(f"{self.policyName}   {self.A}, {self.B}, {self.C}, Profit: ${round(self.profit/1000)} K \n")

    def generateDemands(self):
        self.W = [[self.demandFunction() for _ in range(3)] for _ in range(3)]

    '''
    Do our best to satisfy demands at each city, prioritizing the higher-rate rentals. Each city has a different
    neighboring city to prioritize.
    '''
    def satisfyDemands(self):
        # print(self.W, "\n...satisfying customer demand...")
        for loc in self.locs:
            self.satisfyDemandFromCity(loc)
        
        for loc in self.locs:
            loc.processNewCars()

    def satisfyDemandFromCity(self, start):
        demands = self.W[start.index]
        for i in range(1, 4):
            end = self.locs[(start.index + i) % 3] # Prioritize demand to the other two cities
            self.satisfyDemandFromCityToCity(start, end, demands[end.index])

    def satisfyDemandFromCityToCity(self, start, end, count):
        count = min(start.count, count)
        self.profit += count * (self.lowerRate if (start == end) else self.higherRate)
        start.count -= count
        end.incoming += count
        #print(f"moving {count} cars from {start} to {end}")

    def cost(self, plan):
        return sum(map(abs, plan))*self.transferCost/2
    
    def transferCars(self):
        # print("...transfering cars...")
        for i in range(3):
            self.locs[i].count += self.plan[i]
        self.profit -= self.cost(self.plan)

    # Default Policy: do nothing
    def generatePlan(self):
        self.plan = [0, 0, 0]   
    
    def step(self):
        self.generatePlan()
        self.transferCars()
        # self.showState()
        self.generateDemands()
        self.satisfyDemands()
        # self.showState()

'''
Simulation with a policy that transfers cars to recreate the starting counts between cities.
'''
class ResetPolicy(BasePolicy):
    def __init__(self, state):
        super().__init__(state)  
        self.policyName = "Reset     "

    def generatePlan(self):
        self.plan = [self.initCounts[loc.index] - loc.count for loc in self.locs]

'''
Simulation with a policy that transfers only half of the cars needed to recreate the starting counts between cities.
'''
class HalfResetPolicy(BasePolicy):
    def __init__(self, state):
        super().__init__(state)  
        self.policyName = "Half Reset"

    def generatePlan(self):
        odd_adjustment = random.choice([-1, 1])
        for loc in self.locs:
            diff = self.initCounts[loc.index] - loc.count
            if (diff % 2 == 1):
                diff += odd_adjustment # adjust odd differences to make them even
                odd_adjustment *= -1 # the next adjustment should be in the opposite direction so that the plan sums to 0
            self.plan[loc.index] = diff//2

'''
Simulation where each city's vehicle count is brought within some range [loc.lower, loc.upper]
'''    

class TwoLimitPolicy(BasePolicy):
    def __init__(self, state, lower=50, upper=70):
        super().__init__(state)  
        self.policyName = "Two Limit "
        for loc in self.locs:
            loc.lower = lower
            loc.upper = upper

    def generatePlan(self):
        nextCount = [min(max(loc.lower, loc.count), loc.upper) for loc in self.locs]    # Bring all cities within limits
        nextCount = self.correctDistribution(nextCount) # Adjust to account for all cars
        self.plan = [nextCount[loc.index] - loc.count for loc in self.locs] # How many cars are gained/lost at each city
   
    # Make sure the total number of cars is still n       
    def correctDistribution(self, nextCount):
        if sum(nextCount) == self.n:
            return nextCount
        
        small = nextCount.index(min(nextCount))
        temp = [nextCount[i] if i!= small else -1 for i in range(2)]
        large = temp.index(max(temp))
        medium = 3 - (small + large)

        # We have extra cars that need to go somewhere - should be transfered to the smallest cities
        if self.n > sum(nextCount):
            excess = self.n - sum(nextCount)
            gap = medium - small
            if gap >= excess: # medium city is large enough that all extra cars go to smallest city
                nextCount[small] += excess
            else: # distribute cars so that medium and small become the same size
                total = self.n - nextCount[large]
                nextCount[medium] = total//2
                nextCount[small] = self.n - (nextCount[large] + nextCount[medium])

        # We need more cars sent to the smallest cities
        else:
            deficit = sum(nextCount) - self.n
            gap = large - medium
            if gap >= deficit: # medium city is small enough that all cars should be taken from the largest city only
                nextCount[large] -= deficit
            else: # take cars from both large and medium, so that they become the same size
                total = self.n - nextCount[small]
                nextCount[medium] = total//2
                nextCount[large] = self.n - (nextCount[medium] + nextCount[small])

        return nextCount

'''
Simulation with a policy that does not depend on state. (Choose the same u everytime.)
'''
class ConstantPolicy(BasePolicy):
    def __init__(self, state, u):
        super().__init__(state)  
        self.constantPolicy = u
        self.policyName = "Constant     "

    def generatePlan(self):
        self.plan = [self.constantPolicy[loc.index] - loc.count for loc in self.locs] 

def viewPolicies(initState):
    policies = [
        BasePolicy(initState),  
        HalfResetPolicy(initState), 
        ResetPolicy(initState), 
        TwoLimitPolicy(initState), 
        ConstantPolicy(initState, [55, 55, 70])]

    for p in policies:
        for _ in range(20):
            p.step()
        p.showState()
