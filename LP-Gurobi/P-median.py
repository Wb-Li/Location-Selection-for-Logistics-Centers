import numpy as np
import pandas as pd
import gurobipy as gp
import folium


# ----- data ------
# read data for all cities
data = pd.read_csv('cn.csv')
# only captials
data = data[(data['capital'] == 'admin') | (data['capital'] == 'primary') ]

# parameters
n = data.shape[0]
cities = data['city'].values
loc_x_vals = data['lat'].values
loc_y_vals = data['lng'].values
loc_x = dict(zip(cities, loc_x_vals))
loc_y = dict(zip(cities, loc_y_vals))
h_vals = data['population'].values/1000000 #for calculate easily
h = dict(zip(cities, h_vals)) #demand
I = cities
J = cities
k=10000
h={i:h[i] for i in I}
p = round(n * .2)



# calculate distance
c = {(i,j):((loc_x[i] - loc_x[j])**2 + (loc_y[i] - loc_y[j])**2)**.5 
     for i in I for j in J}

# ----- model ------
m = gp.Model('pmedian')


# decision variable
y = m.addVars(I, J, vtype=gp.GRB.BINARY, name='y')
x = m.addVars(I, vtype=gp.GRB.BINARY, name='x')
w = m.addVars(I, J, vtype=gp.GRB.CONTINUOUS, name='volume')
f = m.addVars(I, vtype=gp.GRB.CONTINUOUS, name= 'cost')
z = m.addVars(I, vtype=gp.GRB.CONTINUOUS, name='z')

# objective
m.setObjectiveN(-gp.quicksum(w[i,j] for i in I for j in J), gp.GRB.MINIMIZE,0)
m.setObjectiveN(gp.quicksum(y[i,j]*c[i,j] for i in I for j in J) +
                gp.quicksum(z[j] for j in J),gp.GRB.MINIMIZE,1)


# constraints

m.addConstrs((y[i,j] <= x[j] for i in I for j in J), name='capacity')
m.addConstrs((gp.quicksum(w[i,j] for j in J) <= h[i] for i in I) , name='volume limit')
m.addConstr(x.sum() == p, name='p_location')
m.addConstrs((y.sum(i,'*') == 1 for i in I), name='cover')
m.addConstrs(gp.quicksum(y[i,j]*w[i,j] for i in I for j in J) <= 
             gp.quicksum(k*f[j]*x[j] for j in J) for i in I)
m.addConstrs((z[j] == f[j]*x[j] for j in J), name='linearization')

# optimize

m.optimize()

# ----- analysis -----
if m.status != gp.GRB.INFEASIBLE:
    pmedian_map = folium.Map(location=[34.32,108.55], zoom_start = 4)

    # mark the captials
    cities_selected = [j for j in J if x[j].x > .9]
    for i in I:
        if i in cities_selected:
            folium.Marker(location=(loc_x[i], loc_y[i]), popup=i, icon=folium.Icon(color='red', icon='info-sign')).add_to(pmedian_map)
        else:
            folium.Marker(location=(loc_x[i],loc_y[i]), popup=i).add_to(pmedian_map)
    
    # draw lines between cities
    for i in I:
        for j in J:
            if y[i,j].x > 0.9:
                folium.PolyLine([[loc_x[i], loc_y[i]], [loc_x[j], loc_y[j]]], color="blue", weight=1.5, opacity=0.5, popup=f"w[{i},{j}]={w[i,j].x}").add_to(pmedian_map)

pmedian_map.save('pmedian_map.html')


