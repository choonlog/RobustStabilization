from sklearn.preprocessing import MinMaxScaler
import numpy as np
import random
import pickle
import attractorSimulator
import sys

nodeLen = int(sys.argv[1])
totalLogicDic = pickle.load(open("./Data/newTotalLogicDic.p", "rb"))
minIndegree = 1
maxIndegree = 4
a = 100. # shape
m = 1.  # mode
def main(nodeNum):

    allNodeLength = nodeNum
    data = (np.random.pareto(a, allNodeLength) + 1) * m
    data = np.reshape(data, (-1, 1))
    scaler = MinMaxScaler(copy=True, feature_range=(minIndegree, maxIndegree))  # Column을 기준으로 한다.
    scaler.fit(data)
    data = scaler.transform(data)
    data = np.round(data)
    data = np.reshape(data, (-1))
    data = data.tolist()
    indegreeList = list(map(int, data))
    indegreeTotalLength = sum(indegreeList)

    fillNumber = len(str(allNodeLength))
    allNodes = ["x" + str(i).zfill(fillNumber) for i in range(1, allNodeLength + 1)]
    formatAttr = ""
    formatNormal = ""

    for k in allNodes:
        initialStateLine = k + " = Random" + "\n"
        formatAttr = formatAttr + initialStateLine
    formatAttr = formatAttr + "\n\n"

    for node, indegree in zip(allNodes, indegreeList):

        selectedNodes = random.sample(allNodes, indegree)
        biologicalRandomLogic = random.choice(totalLogicDic[str(indegree)])

        for n, selectNode in enumerate(selectedNodes):
            existingNode = "z" + str(n + 1).zfill(2)
            biologicalRandomLogic = biologicalRandomLogic.replace(existingNode, selectNode)

        biologicalRandomLogic = biologicalRandomLogic.replace("&", "and").replace("|", "or").replace("~", "not ")
        formatNormal = formatNormal + node + " = " + biologicalRandomLogic + "\n"
        formatAttr = formatAttr + node + " *= " + biologicalRandomLogic + "\n"

    return formatAttr, formatNormal, indegreeTotalLength

formatAttr, bnOriNet, _ = main(nodeLen)
desiredAttr = attractorSimulator.main(formatAttr, 1000, 100)

if desiredAttr:
    with open("./RBN/bnOriNet.txt", "w") as text_file:
         text_file.write(bnOriNet)
    with open("./RBN/desiredAttr.txt", "w") as text_file:
         text_file.write(desiredAttr)
else:
    with open("./RBN/bnOriNet.txt", "w") as text_file:
         text_file.write("")
    with open("./RBN/desiredAttr.txt", "w") as text_file:
         text_file.write("")