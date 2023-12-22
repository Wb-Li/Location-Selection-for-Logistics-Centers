import numpy as np
import pandas as pd

data = pd.read_csv('cn.csv')

cities = data['city'].values
h = data['population'].values/1000000
loc_x = data['lat'].values
loc_y = data['lng'].values

n = len(cities)
c = np.zeros((n,n))
for i in range(n):
    for j in range(n):
        c[i,j] = ((loc_x[i] - loc_x[j])**2 + (loc_y[i] - loc_y[j])**2)**.5

solution = []

p = 5

solution = sorted(range(n), key=lambda x: h[x], reverse=True)[:p]

demand = {i: 0 for i in range(n)}
cost = 0

while sum(demand.values()) < sum(h):
    city_costs = {}
    for j in set(range(n)) - set(solution):
        demand_j = sum(min(h[i], c[i,j]) for i in solution)
        cost_j = sum(c[i,j] for i in solution)
        city_costs[j] = demand_j, cost_j

    j = max(city_costs, key=lambda x: city_costs[x][0] / city_costs[x][1])

    solution.append(j)
    demand = {i: demand[i] + min(h[i], c[i,j]) for i in range(n)}
    cost += city_costs[j][1]

print(f"Selected cities: {[cities[i] for i in solution]}")
