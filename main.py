import time
from policySimulations import *
from twoLimitPolicies import *
from lookahead import *

def main():
    a = b = c = 60
    initState = (a, b, c) # Assume system is symmetric
    n = sum(initState)

    # viewPolicies(initState)

    # bestTwoLimitPolicy = exploreTwoLimitPolicies(initState, 100, 365)

    bestTwoLimitPolicy = (56, 66)
    print(bestTwoLimitPolicy)
    lookahead = Lookahead(bestTwoLimitPolicy)

    start = time.time()
    lookahead.J(initState, k=3)
    end = time.time()

    print(lookahead)
    print((end - start), " seconds")
    


    
if __name__ == "__main__":
    main()
