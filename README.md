# RobustStabilization
RobustStabilization is a Python package that determines robust stabilizing control inputs of perturbed biological networks via coordinate transformation and algebraic analysis. Since cells have heterogenous characteristics, it is challenging to control them with the common drug combination. In particular, in the case of cancer cells, it is difficult to apply targeted therapy because each tumor population with various mutation profiles can arise during cancer development. RobustStabilization is an algorithm implemented in python that finds appropriate common control inputs in multiple mutated networks with various mutation profiles. A relevant paper will be soon published.

## Results of comparative study
<img src="./Fig_1.png" alt="fig_1" />
<p align="center">
    <b>Fig. 1. The experimental results on robust stabilization of complex random
BNs. (a) Average stabilization score for 4,000 random BNs, each ensemble of
1,000 BNs having respectively 20, 30, 40, and 50 nodes. (b) Average number
of elements in the derived control input sets. (c) Average computational time
required to derive the solutions for each ensemble of random BNs. The error
bars in (a)–(c) denote the 95% confidence intervals of the average score,
number of elements, and computation time, respectively.</b><br />
    *Please refer to the upcoming paper for more details.
</p>

<img src="./Fig_2.png" alt="fig_2" />
<p align="center">
    <b>Fig. 2. Average stabilization score for each ensemble of 1,000 BNs having
respectively 20, 30, 40, and 50 nodes. Instead of the original FVS, we apply
all the possible subsets of the original FVS that have the same size as the
solution of the proposed algorithm, and take their average scores.</b><br />
    *Please refer to the upcoming paper for more details.
</p>



## Installation
You can simply download RobustStabilization from this git repository, while setup.py is not provided. RobustStabilization is executed on any operating system (Windows, Mac OS, Linux, etc), but Python 3.5 or higher versions must be installed to run the program. The following package is used while running the RobustStabilization.

FVS FINDER: https://github.com/needleworm/fvs

## Input
'RobustStabilization/main.py' allows you to set the name of a file containing network structure information, desired attacter, and mutation profile. For more information, please refer to the comments in main.py.

*A file containing network structure information should be saved in the'RobustStabilization/networks/' directory, and if there are input nodes, the Boolean expression of the nodes should be marked as follows.
```
input_node = _INPUT_
```
## Output
Control inputs and addtional control inputs are saved in the form of a .txt file in the'RobustStabilization/results/' directory.


# BNGenerator
BNGenerator is executed independently of RobustStabilization, and is a software that generates a random Boolean network using Biological Boolean logics extracted from 78 Biological Boolean networks in the Cell Collective (https://cellcollective.org/).

## Example
It can be executed by entering the parameters of the generator function in line 44 of BNGenerator.py.
The result is saved in the name specified by the user in line 46.

```
# generator(Parameter_1, Parameter_2, Parameter_3)
# Parameter_1: The number of nodes in the network to be generated
# Parameter_2: Minimum indegree
# Parameter_3: Maximum indegree
formatNormal = generator(20, 1, 3)

netName = "RBN_1"
with open(netName + ".txt", "w") as text_file:
    text_file.write(formatNormal)
```

The number of nodes in the network to be generated is determined by Parameter_1, and the input link of each node is randomly selected from the uniform distribution with a range between Parameter_2 and Parameter_3. Boolean logic is randomly assigned from the Biological Boolean logic collection data (BNGenerator/data/newTotalLogicDic.p) according to the indegree after the input link of each node is determined.
