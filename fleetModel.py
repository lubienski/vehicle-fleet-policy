import random

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
Simulation for the default model (no transfers)
'''
class BasePolicy:
    def __init__(self, a, b, c):
        self.n = a + b + c # fleet size
        self.A = Location(a, 0)
        self.B = Location(b, 1)
        self.C = Location(c, 2)
        self.locs = [self.A, self.B, self.C]
        self.demandFunction = lambda: random.randint(0,8) # Assuming demand comes from a uniform distribution
        self.lowerRate = 100 # Price to rent a car locally
        self.higherRate = 150 # Price to rent a car and return it in a different city
        self.transferCost = 50  # Cost to transfer each vehicle overnight
        self.policyName = "Base      "

        self.plan = [0, 0, 0] # Planned increase at each city
        self.W = None   # Matrix of demands. W[i][j] is the demand from city i to city j
        self.profit = 0 # Total profit the company has made so far

        # self.showState()

    def showState(self):
        print(f"{self.policyName}   {self.A}, {self.B}, {self.C}, Profit: {self.profit}\n")

    def generateDemands(self):
        self.W = [[self.demandFunction() for _ in range(3)] for _ in range(3)]

    '''
    Do our best to satisfy demands at each city, prioritizing the higher-rate rentals. (Each city has a different
    neighboring city to prioritize - but we could add a smarter heuristic here).
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
        self.generateDemands()
        self.satisfyDemands()
        # self.showState()
        self.generatePlan()
        self.transferCars()
        # self.showState()

'''
Simulation with a policy that transfers cars to recreate the starting counts between cities.
'''
class ResetPolicy(BasePolicy):
    def __init__(self, a, b, c):
        super().__init__(a, b, c)  
        self.initCounts = [a, b, c]
        self.policyName = "Reset     "

    def generatePlan(self):
        self.plan = [self.initCounts[loc.index] - loc.count for loc in self.locs]

'''
Simulation with a policy that transfers only half of the cars needed to recreate the starting counts between cities.
'''
class HalfResetPolicy(BasePolicy):
    def __init__(self, a, b, c):
        super().__init__(a, b, c)  
        self.initCounts = [a, b, c]
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
    def __init__(self, a, b, c):
        super().__init__(a, b, c)  
        self.initCounts = [a, b, c]
        self.policyName = "Two Limit "
        for loc in self.locs:
            loc.lower = loc.count - 5
            loc.upper = loc.count + 5

    def generatePlan(self):
        for loc in self.locs:
            nextCount = min(max(loc.lower, loc.count), loc.upper)
            self.plan[loc.index] = nextCount - loc.count


def main():
    [a, b, c] = [20, 20, 20] # TODO: The demand function should be associated with the starting ratios?
    policies = [BasePolicy(a, b, c),  HalfResetPolicy(a, b, c), ResetPolicy(a, b, c), TwoLimitPolicy(a, b, c)]

    for p in policies:
        for i in range(2000):
            p.step()
        p.showState()
    
    
if __name__ == "__main__":
    main()

    
