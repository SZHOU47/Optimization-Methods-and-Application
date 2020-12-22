import gurobipy as gp
from gurobipy import GRB
from math import sqrt
import pandas as pd
import numpy as np

########################################
########### IMPORT DATA ################
########################################

# Import drug data using pandas
data = pd.read_csv('/Users/apple/Documents/Semester 3/6212 Optimization/Workshop/3/drugs.csv', index_col=0)
projects = data.columns
t_area = data.iloc[0]
ttm = data.iloc[1]
enpv = data.iloc[2]
cost = data.iloc[3]

#import covariance matrix
cov=pd.read_csv('/Users/apple/Documents/Semester 3/6212 Optimization/Workshop/3/drugs_cov.csv', index_col=0)

#therapeutic areas
ther=[
"Oncology", "Cardiovascular", "Respiratory and dermatology", "Transplantation",
"Rheumatology and hormone therapy", "Central nervous system", "Ophtalmics"]

#budget constraints for therapeutic areas
t_bud={"Oncology": 100,
       "Cardiovascular": 200,
       "Respiratory and dermatology": 150,
       "Transplantation": 100,
       "Rheumatology and hormone therapy": 300,
       "Central nervous system": 100,
       "Ophtalmics": 50}

interest_rate=0.03

additional_budget=50

# creates lower triangular matrix needed in Value at Risk analysis in Q4 using Cholesky factorization
# Note that this results in L to be in matrix format (i.e., not in the dataframe format anymore)
L = np.linalg.cholesky(cov)

########################################
########### MODEL ######################
########################################

# Create an empty model
m = gp.Model('portfolio')
m.update()

# ADD DECISION VARIABLES (AND FOR Q4 HELPER DECISION VARIABLES) HERE
vars = pd.Series(m.addVars(projects,vtype=GRB.BINARY), index=projects)

########################################
#### CONSTRAINTS & OBJ FUNCTIONS #######
########################################

# ADD CONSTRAINTS HERE
for x in ther:
       m.addConstr(sum(vars*cost*(t_area==x)) <= t_bud[x], f'{x} budget')

m.addConstr(sum(vars*(ttm=='1'))>=0.15*sum(vars), '1 year')
m.addConstr(sum(vars*((ttm=='2')|(ttm=='3')))>=0.2*sum(vars), '2,3 year')
m.addConstr(sum(vars*((ttm=='4')|(ttm=='5')))>=0.25*sum(vars), '4,5 year')

# ADD OBJECTIVE FUNCTION HERE
portfolio_enpv = sum(vars*enpv)
portfolio_totalcost = sum(vars*cost)
portfolio_risk = cov.values.dot(vars).dot(vars)
m.setObjective(portfolio_enpv, GRB.MAXIMIZE) 

m.update()
m.optimize()

########################################
########### PRINT RESULTS ##############
########################################


# ADD PRINTING HERE:
    # selected projects
    # cost of funded projects
    # selected therapeutic area with additional budget
    # portfolio's enpv, st.dev., variance, 5th percentile

print('Selected projects:\n')
print(', '.join([str(v.index+1) for v in vars if v.x == 1]))

print('\nCost of funded projects:\n')
for (i,v) in enumerate(vars):
    if v.x == 1:
        print('\t%g\t: %s' % (v.index+1, cost[i]))

print('Portfolio cost = %g' % portfolio_totalcost.getValue())
print('Portfolio ENPV = %g' % portfolio_enpv.getValue())
print('Portfolio Standard Deviation= %g' % sqrt(portfolio_risk.getValue()))
print('Portfolio Variance= %g' % portfolio_risk.getValue())
print('Portfolio VaR at 5th percentile= %g' % (portfolio_enpv.getValue()-1.645*sqrt(portfolio_risk.getValue())))