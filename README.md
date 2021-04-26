# RobustStabilization
RobustStabilization is a Python package that determines robust stabilizing control inputs of perturbed biological networks via coordinate transformation and algebraic analysis. Since cells have heterogenous characteristics, it is very challenging to control it with the common control inputs at once. In particular, in the case of cancer cells, it is difficult to apply targeted therapy because each tumor population with various mutation profiles can arise during cancer development. RobustStabilization is an algorithm implemented in python that finds appropriate common control inputs in multiple mutated networks with various mutation profiles. A relevant paper will be soon published.
## Installation
You can simply download RobustStabilization from this git repository, while setup.py is not provided. RobustStabilization is executed on any operating system (Windows, Mac OS, Linux, etc), but Python 3.5 or higher versions must be installed to run the program. The following packages are used while running the RobustStabilization.
1. FVS FINDER: https://github.com/needleworm/fvs
2. BooleanSim: https://github.com/jehoons/BooleanSim

*If you want to do numerical experiences for a random Boolean network, you can download and run RobustStabilization_RBN. RobustStabilization and RobustStabilization_RBN are independent program codes
## Input
'RobustStabilization/main.py' allows you to set the name of a file containing network structure information, desired attacker, and mutation profile. For more information, please refer to the comments at main.py.

*A file containing network structure information should be saved in the'RobustStabilization/networks/' directory, and if there is an input node, the Boolean expression of the node should be marked as
```
input_node = _INPUT_'.
```
## Output
Control inputs and addtional control inputs are saved in the form of a .txt file in the'RobustStabilization/results/' directory.
## Example

# BNGenerator

## Example
