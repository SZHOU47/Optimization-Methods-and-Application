import gurobipy as gp
from gurobipy import GRB
from gurobipy import *
import pandas as pd
import numpy as np

########################################
########### IMPORT DATA ################
########################################

#list of teams that are included in the analysis
Team_list={
0:"Atlanta Falcons",1:"Carolina Panthers",2:"Chicago Bears",3:"Detroit Lions",
4:"Green Bay Packers",5:"Minnesota Vikings",6:"New Orleans Saints",7:"New York Giants",
8:"Philadelpia Eagles",9:"Tampa Bay Buccaneers",10:"Washington Football Team",11:"Baltimore Ravens",
12:"Buffalo Bills",13:"Cincinnati Bengals",14:"Cleveland Browns",15:"Houston Texans",
16:"Indianapolis Colts",17:"Jacksonville Jaguars",18:"Miami Dolphins",19:"New England Patroits",
20:"New York Jets",21:"Pittsburgh Steelers",22:"Tennessee Titans",23:"Dalls Cowboys"}

W=set(range(0,12)) #set of weeks, total of 12 weeks
T=set(range(0,24)) #set of teams all, total of 24 teams
 #set of conference
D1=set(range(0,12)) #set of AFC teams
D2=set(range(12,24)) #set of NFC teams

#read the distance file
E=pd.read_csv("/Users/apple/Documents/Semester 3/6212 Optimization/Workshop/2/distance.csv",index_col=0)

########################################
########### MODEL ######################
########################################

# Create an empty model
m1= gp.Model(name="NFL1")

# ADD DECISION VARIABLES HERE
# 𝑥𝑖𝑗𝑘 = 1 if a team i is playing a game at home against team j during week k, otherwise 𝑥𝑖𝑗𝑘 =0
x = m1.addVars(T,T,W, vtype=GRB.BINARY,name="x")

########################################
#### CONSTRAINTS & OBJ FUNCTIONS #######
########################################

# ADD CONSTRAINTS HERE

#Each team would play once per week.
for k in range(12):
    for i in range(24):
        m1.addConstr(sum(x[i,j,k] + x[j,i,k] for j in range(24) if j != i)==1,f"c1{k,i}")

#All 12 games that a team played would need to be against a different opponent.
for i in range(24):
    for j in range(24):
        if i != j:
            m1.addConstr(sum(x[i,j,k] + x[j,i,k] for k in range(12))<=1,f"c2{i,j}")

#Each team would play at most six home games (i.e., on their home stadium).
for i in range(24):
     m1.addConstr(sum(x[i,j,k] for j in range(24) for k in range(12) if j != i)<=6,f"c3{i}")

#no team would play more than (i) two consecutive games at home and (ii) two consecutive games away.
for k in range(10):
    for i in range(24):
        m1.addConstr(sum(x[i,j,k]+x[i,j,k+1]+x[i,j,k+2] for j in range(24) if j != i)<=2,f"c4{k,i}")
        m1.addConstr(sum(x[i,j,k]+x[i,j,k+1]+x[i,j,k+2] for j in range(24) if j != i)>=1,f"c5{k,i}")

# ADD OBJECTIVE FUNCTION HERE
obj = sum(2*x[i,j,k]*E.iloc[i,j] for i in range(24) for j in range(24) for k in range(12))
m1.setObjective(obj, GRB.MINIMIZE)

#optimize the model
m1.optimize()

########################################
########### PRINT RESULTS ##############
########################################

# ADD PRINTING HERE:

# print the total distance travelled by all teams
print('\nTotal distance travelled by all teams: %g miles' % m1.objVal)
# print the optimal schedule for Cleveland Browns
print('\nOptimal schedule for Cleveland Browns:')
for k in range(12):
    for z in range(24):
        if x[14,z,k].X==1:
            print(f'\nWeek {k+1}: Home vs. {Team_list[z]}')
        elif x[z,14,k].X==1:
            print(f'\nWeek {k+1}: Away vs. {Team_list[z]}')

# Q3: print distance that each team travels
for i in range(24):
    print(f'\nTotal distance travelled by {Team_list[i]}: {sum(2*x[j,i,k].X*E.iloc[j,i] for j in range(24) for k in range(12))} miles')
# Q4: print distance and schedule for Chicago Bears and Jacksonville Jaguars
print('\nDistance and schedule for Chicago Bears:')
for k in range(12):
    for z in range(24):
        if x[2,z,k].X==1:
            print(f'\nWeek {k+1}: Home vs. {Team_list[z]}, Distance 0 mile')
        elif x[z,2,k].X==1:
            print(f'\nWeek {k+1}: Away vs. {Team_list[z]}, Distance {2*x[z,2,k].X*E.iloc[z,2]} miles')

print('\nDistance and schedule for Jacksonville Jaguars:')
for k in range(12):
    for z in range(24):
        if x[17,z,k].X==1:
            print(f'\nWeek {k+1}: Home vs. {Team_list[z]}, Distance 0 mile')
        elif x[z,17,k].X==1:
            print(f'\nWeek {k+1}: Away vs. {Team_list[z]}, Distance {2*x[z,17,k].X*E.iloc[z,17]} miles')