# DKFZ
#
#
# Copyright (c) German Cancer Research Center,
# Division of Medical Image Computing.
# All rights reserved.
#
# This software is distributed WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.
#
# See LICENSE

# A hyppopy minimal example optimizing a simple demo function f(x,y) = x**2+y**2

# import the HyppopyProject class keeping track of inputs
from hyppopy.HyppopyProject import HyppopyProject

# import the HyperoptSolver class
from hyppopy.solvers.HyperoptSolver import HyperoptSolver

# To configure the Hyppopy solver we use a simple nested dictionary with two obligatory main sections,
# hyperparameter and settings. The hyperparameter section defines your searchspace. Each hyperparameter
# is again a dictionary with:
#
# - a domain ['categorical', 'uniform', 'normal', 'loguniform']
# - the domain data [left bound, right bound] and
# - a type of your domain ['str', 'int', 'float']
#
# The settings section has two subcategories, solver and custom. The first contains settings for the solver,
# here 'max_iterations' - is the maximum number of iteration.
#
# The custom section allows defining custom parameter. An entry here is transformed to a member variable of the
# HyppopyProject class. These can be useful when implementing new solver classes or for control your hyppopy script.
# Here we use it as a solver switch to control the usage of our solver via the config. This means with the script
# below your can try out every solver by changing use_solver to 'optunity', 'randomsearch', 'gridsearch',...
# It can be used like so: project.custom_use_plugin (see below) If using the gridsearch solver, max_iterations is
# ignored, instead each hyperparameter must specifiy a number of samples additionally to the range like so:
# 'data': [0, 1, 100] which means sampling the space from 0 to 1 in 100 intervals.

config = {
"hyperparameter": {
    "x": {
        "domain": "normal",
        "data": [-10.0, 10.0],
        "type": float
    },
    "y": {
        "domain": "uniform",
        "data": [-10.0, 10.0],
        "type": float
    }
},
"max_iterations": 500
}


# When creating a HyppopyProject instance we
# pass the config dictionary to the constructor.
project = HyppopyProject(config=config)


# The user defined loss function
def my_loss_function(x, y):
    return x**2+y**2

# create a solver instance
solver = HyperoptSolver(project)
# pass the loss function to the solver
solver.blackbox = my_loss_function
# run the solver
solver.run()

df, best = solver.get_results()

print("\n")
print("*"*100)
print("Best Parameter Set:\n{}".format(best))
print("*"*100)

