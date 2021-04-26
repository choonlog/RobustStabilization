import allPlusProducts
import optOnePlusProduct
import fvsFinder as fv
import ast
import re
import random
from sympy.logic import simplify_logic
import json
from boolean3_addon import attr_cy
import itertools
import time
import pickle
import os
import sys
import math



def nCr(n, r):
    '''
   :param n: Number of population
   :param r: Number of sample
   :return:
       combination: Number of combination
   '''
    f = math.factorial
    return f(n) / f(r) / f(n - r)



def jaccardSimilarity(list1, list2):
    '''
    :param list1: list
    :param list2: list
    :return:
        jaccardSimilarity: Jaccard similarity
    '''
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection) / union



def averageActivity(path):
    '''
    :param path: Path for saving a result file
    :return:
        averageActivity: Average activity based on all attractors
    '''

    with open(path) as data_file:
        data = json.load(data_file)

    attrKeyList = data["attractors"].keys()
    eachActivity = []
    dic = {}

    for attrKey in attrKeyList:
        if data["attractors"][attrKey]["type"] == "point":
            pointRatio = data["attractors"][attrKey]["ratio"]
            pointValue = data["attractors"][attrKey]["value"]
            pointAttr = data["state_key"][pointValue]

            for eachNode in pointAttr:
                nodeRatio = float(eachNode) * float(pointRatio)
                eachActivity.append(nodeRatio)
                dic[pointValue] = eachActivity
            else:
                eachActivity = []

        elif data["attractors"][attrKey]["type"] == "cyclic":
            cyclicRatio = data["attractors"][attrKey]["ratio"]
            cyclicValue = data["attractors"][attrKey]["value"]
            cyclicLength = len(cyclicValue)

            for eachValue in cyclicValue:
                cyclicAttr = data["state_key"][eachValue]
                for eachNode in cyclicAttr:
                    nodeRatio = float(eachNode) * float(cyclicRatio) * (1/cyclicLength)
                    eachActivity.append(nodeRatio)
                    dic[eachValue] = eachActivity
                else:
                    eachActivity = []

    averageActivity = []
    for k in range(0, len(data["labels"])):
        averageActivity.append(0)

    for eachValue in data["state_key"]:
        z = 0
        for eachNode in dic[eachValue]:
            if float(averageActivity[z]) + float(eachNode) > 0.99999:
                averageActivity[z] = 1.0
            else:
                averageActivity[z] = float(averageActivity[z]) + float(eachNode)
            z = z + 1
        else:
            z = 0

    return averageActivity



def attractorSimulation(modeltext, samples, steps, onList, offList, path):
    '''
    :param modeltext: Network model
    :param samples: Number of initial states
    :param step: Number of Boolean function update
    :param onList: On perturbation
    :param offList: Off perturbation
    :param path: Path for saving a result file
    :return:
    '''

    attr_cy.build(modeltext)

    import pyximport; pyximport.install()

    res = attr_cy.run(samples=samples, steps=steps, debug=False, progress=False, on_states=onList, off_states=offList)
    # on_states*=['A01', 'A51'], off_states*=['A38', 'A40']
    # debug needs to be changed to 'True' to check trajectory
    json.dump(res, open(path, 'w'), indent=4)



def replace(string, substitutions):
    '''
    :param string: String
    :param substitutions: substitutions
    :return:
        substitutedString: substituted string
    '''
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)



def canalizationEffect(modeltext, canalizingNodeDic):
    '''
    :param modeltext: Network model
    :param canalizingNodeDic: Canalizing node dictionary
    :return:
        modeltext: residual network
        canalizedStateVectorDic: canalized state vector dictionary
        stepCanalizedStateVectorList: canalized state vector list according to the step
        allStateVectorDic: all state vector dictionary
    '''

    # Strip whitespace
    modeltext = modeltext.strip()

    # Replace the logics with symbols
    modeltext = re.sub(r"\band\b", "&", modeltext)
    modeltext = re.sub(r"\bor\b", "|", modeltext)
    modeltext = re.sub(r"\bnot\b", "~", modeltext)

    # Split text lines
    modeltextLine = modeltext.splitlines()

    # Get all nodes
    allNodeList = []
    for line in modeltextLine:
        allNodeList += re.findall(r'\w+', line)

    # Deduplication
    allNodeList = [x for i, x in enumerate(allNodeList) if i == allNodeList.index(x)]

    # Create a all state vector dictionary with no values
    allStateVectorDic = {}
    for node in allNodeList:
        allStateVectorDic[node] = ""

    # Recursive process
    canalizedStateVectorDic = {}
    stepCanalizedStateVectorList = []
    process = True
    while process:

        # Update canalizing node list
        if canalizingNodeDic:
            for node in canalizingNodeDic:
                allStateVectorDic[node] = canalizingNodeDic[node]

            # Append canalized state vector list according to the step
            stepCanalizedStateVectorList.append(canalizingNodeDic)

            # Merge two dictionaries
            canalizedStateVectorDic = dict(**canalizedStateVectorDic, **canalizingNodeDic)

            # Get canalizing node list
            canalizingNodeList = list(canalizingNodeDic.keys())

            # Split text lines
            modeltextLine = modeltext.splitlines()

            # Apply the canalization effect
            newCanalizingNodeDic = {}
            newModeltext = ""
            for line in modeltextLine:
                str1 = line.split("=")
                stateVariable = str1[0].strip()
                BooleanExpression = str1[1].strip()

                if not stateVariable in canalizingNodeList:

                    for fixedNode in canalizingNodeDic:
                        BooleanExpression = re.sub(r"\b" + fixedNode + r"\b", str(canalizingNodeDic[fixedNode]).lower(), BooleanExpression)
                    simplifiedExpression = simplify_logic(BooleanExpression)

                    if simplifiedExpression in [True]:
                        newCanalizingNodeDic[stateVariable] = simplifiedExpression
                    else:
                        if not simplifiedExpression:
                            simplifiedExpression = stateVariable
                        newModeltext += stateVariable + " = " + str(simplifiedExpression) + "\n"

            modeltext = newModeltext
            canalizingNodeDic = newCanalizingNodeDic
        else:
            break

    # Ordering
    canalizedStateVectorDic = dict(sorted(canalizedStateVectorDic.items(), reverse=False))
    allStateVectorDic = dict(sorted(allStateVectorDic.items(), reverse=False))

    # Node with value is False or logic
    additionalSolutionList = []
    for node in allStateVectorDic:
        if allStateVectorDic[node] == "":
            additionalSolutionList.append(node)

    # If the canalizing node is not included in the network, subtract it
    newCanalizedStateVectorDic = {}
    for canalizedNode in canalizedStateVectorDic:
        if canalizedNode in allNodeList:
            newCanalizedStateVectorDic[canalizedNode] = canalizedStateVectorDic[canalizedNode]

    return modeltext, additionalSolutionList, len(newCanalizedStateVectorDic)



repeat = sys.argv[1]
nodeLen = int(sys.argv[2])
net = "RBN" + str(nodeLen) + "_" + str(repeat.zfill(4))
# net = "RBN20_0001"

# bnOriNet = '''
# x01 = not x04 or not x17
# x02 = x19
# x03 = x20
# x04 = not x12 and not x02
# x05 = x02 or (x01 and x17)
# x06 = not x18 or not x16
# x07 = (x17 and not x06 and not x15) or (x03 and x04 and not x06 and not x15)
# x08 = x19 and x07
# x09 = not x13
# x10 = (x19 and not x11) or (x09 and x18 and not x11)
# x11 = x05
# x12 = x09 or x12 or not x17
# x13 = not x15
# x14 = x10 and x15
# x15 = not x17
# x16 = x20 or x11
# x17 = (not x04 and not x12) or (not x15 and not x12)
# x18 = x04 and not x14
# x19 = not x05 and not x17
# x20 = x17 or (x12 and not x04) or (x19 and not x20)
# '''
# bnOriNet = bnOriNet.strip()
# desiredAttr = "00110010000010011101"

with open('./RBN/bnOriNet.txt') as file:
    bnOriNet = file.read()
with open('./RBN/desiredAttr.txt') as file:
    desiredAttr = file.read()

print("bnOriNet", bnOriNet)
print("desiredAttr", desiredAttr)

if desiredAttr:



    # Transform string of one desired attractor to list type
    desiredAttrList = []
    for state in desiredAttr:
        desiredAttrList.append(int(state))



    # Get G network, all plus product network, and format for original FVSs
    proTime_transformation_start = time.time()
    bnGNet, bnAllPlusProductNet, formatFVSori = allPlusProducts.main(bnOriNet, desiredAttr)



    # Get the format for first solutions
    formatFVSoptOnePlus = optOnePlusProduct.main(bnAllPlusProductNet)
    proTime_transformation = time.time() - proTime_transformation_start



    # Find FVSs
    with open("./networks/formatFVSoptOnePlus.csv", "w") as text_file:
        text_file.write(formatFVSoptOnePlus)
    with open("./networks/formatFVSori.csv", "w") as text_file:
        text_file.write(formatFVSori)

    proTime_FVS_start = time.time()
    fv.FVSFinder("formatFVSoptOnePlus.csv", "formatFVSoptOnePlus.txt")
    proTime_FVS = time.time() - proTime_FVS_start

    oriTime_FVS_start = time.time()
    fv.FVSFinder("formatFVSori.csv", "formatFVSori.txt")
    oriTime = time.time() - oriTime_FVS_start



    # First solution sets
    with open("./result/formatFVSoptOnePlus.txt") as file:
        firstSolutionText = file.read().splitlines()
    firstSolutionListList = []
    for firstSolution in firstSolutionText:
        firstSolutionListList.append(ast.literal_eval(firstSolution))



    # Original solution sets
    with open("./result/formatFVSori.txt") as file:
        originalSolutionText = file.read().splitlines()
    originalSolutionListList = []
    for originalSolution in originalSolutionText:
        originalSolutionListList.append(ast.literal_eval(originalSolution))
    print("1. firstSolutionListList:\n", firstSolutionListList, "\n")
    print("2. originalSolutionListList:\n", originalSolutionListList, "\n")
    print("3. bnGNet:\n", bnGNet, "\n")



    # All node information
    modeltext = bnGNet.strip()
    modeltextLine = modeltext.splitlines()
    allNodeList = []
    for line in modeltextLine:
        allVariable = re.findall(r'\w+', line)
        allNodeList = allNodeList + allVariable
    allNodeList = [x for i, x in enumerate(allNodeList) if i == allNodeList.index(x)]
    allNodeList.sort(reverse=False)
    allNodeDic = {}
    for node in allNodeList:
        allNodeDic[node] = ''



    # Random mutation candidates
    noMutationCandidateList = sum(firstSolutionListList, []) + sum(originalSolutionListList, [])    # (2dim list, []): 2dim list to 1dim list
    noMutationCandidateList = [x for i, x in enumerate(noMutationCandidateList) if i == noMutationCandidateList.index(x)]
    mutationCandidateList = list(set(allNodeList) - set(noMutationCandidateList))
    print("mutationCandidateList", mutationCandidateList)
    netNum = 2
    muNum = 2
    mutationList = random.sample(mutationCandidateList, netNum * muNum)     # Sampling mutations without duplications
    mutationDic = {}
    for i in range(netNum):
        mutationDic["G" + str(i)] = mutationList[i * muNum:i * muNum + muNum]



    # example
    # mutationDic = {'G0': ['x03', 'x07'], 'G1': ['x01', 'x13']}
    # mutationList = ['x03', 'x07', 'x01', 'x13']
    print("4. Mutation candidate nodes:\n", mutationCandidateList, "\n")
    print("5. mutationDic:\n", mutationDic, mutationList, "\n")



    # Replace ('&', '|', and '~') with ('and', 'or', and 'not') respectively
    substitutions = {"&": "and", "|": "or", "~": "not "}
    bnGNet = replace(bnGNet, substitutions)
    print(bnGNet)

    substitutions = {"=": "*="}
    bnGNetForAttr = replace(bnGNet, substitutions)
    initialStateForAttr = ""
    for node in allNodeList:
        initialStateForAttr += str(node) + " = Random\n"
    initialStateForAttr.strip()
    bnGNetForAttr = initialStateForAttr + "\n\n" + bnGNetForAttr
    bnGNetForAttr = bnGNetForAttr.strip()
    print(bnGNetForAttr)



    # Recursive canalization
    firstSolutionScoreDic = {}
    firstSolutionNumDic = {}
    firstSolutionAdd1ScoreDic = {}
    firstSolutionAdd1NameDic = {}
    originalSolutionScoreDic = {}
    proTime_AddtionalInput_List = []
    for firstSolutionList in firstSolutionListList:
        proTime_AddtionalInput_start = time.time()
        canalizedNetDic = {}
        additionalSolutionDic = {}
        addtionalSolutionLen = 0
        for mutationNet in mutationDic:
            canalizingNodeDic = {}
            currentMutationList = mutationDic[mutationNet]
            for currentMutation in currentMutationList:
                canalizingNodeDic[currentMutation] = False

            for firstSolution in firstSolutionList:
                canalizingNodeDic[firstSolution] = True

            canalizedNetString, additionalSolutionList, _ = canalizationEffect(bnGNet, canalizingNodeDic)
            addtionalSolutionLen += len(additionalSolutionList)
            # print(firstSolutionList, mutationNet, additionalSolutionList, canalizingNodeDic, canalizedNetString)
            canalizedNetDic[mutationNet] = canalizedNetString
            for additionalSolution in additionalSolutionList:
                additionalSolutionDic[additionalSolution] = True

        additionalSolutionDic_copy = additionalSolutionDic.copy()
        priorityAddtionalSolutionList = []
        while True:
            additionalSolutionTotalScoreDic = {x: 0 for x in list(additionalSolutionDic.keys())}
            for additionalSolution in additionalSolutionDic:
                totalScore = 0
                for canalizedNet in canalizedNetDic:
                    # print(canalizedNetDic[canalizedNet])
                    candidate = {k: additionalSolutionDic_copy for k, additionalSolutionDic_copy in additionalSolutionDic_copy.items() if k in [additionalSolution] + priorityAddtionalSolutionList}
                    _, _, canalizedLen = canalizationEffect(canalizedNetDic[canalizedNet], candidate)
                    # print([additionalSolution] + priorityAddtionalSolutionList, canalizedNet, additionalSolution, canalizedLen)
                    totalScore += canalizedLen
                additionalSolutionTotalScoreDic[additionalSolution] = totalScore
            priorityAddtionalSolution = max(additionalSolutionTotalScoreDic, key=additionalSolutionTotalScoreDic.get)
            priorityAddtionalSolutionList.append(priorityAddtionalSolution)
            # print(priorityAddtionalSolution)
            del additionalSolutionDic[priorityAddtionalSolution]
            # print("priorityAddtionalSolution", additionalSolutionTotalScoreDic[priorityAddtionalSolution], addtionalSolutionLen)
            if additionalSolutionTotalScoreDic[priorityAddtionalSolution] == addtionalSolutionLen:
                break

        # Save time for finding addtional inputs
        proTime_AddtionalInput_end = time.time() - proTime_AddtionalInput_start
        proTime_AddtionalInput_List.append(proTime_AddtionalInput_end)

        # Final additional inputs ordered
        print("priorityAddtionalSolutionList", priorityAddtionalSolutionList)



        # Addtional input Score
        firstSolutionScoreSubDic = {}
        for i in range(len(priorityAddtionalSolutionList) + 1):
            priorityAddtionalSolutionSubList = priorityAddtionalSolutionList[0:i]
            onList = firstSolutionList + priorityAddtionalSolutionSubList
            totalScore = 0
            for mutationNet in mutationDic:
                offList = mutationDic[mutationNet]
                path = "./perturbation/" + str(mutationNet) + "_" + str(onList) + ".json"
                # print(mutationNet, onList, offList)
                attractorSimulation(bnGNetForAttr, 1000, 200, onList, offList, path)
                averageActivityList = averageActivity(path)
                # print("averageActivityList", averageActivityList, len(mutationDic))
                os.remove(path)
                totalScore += (averageActivityList.count(1.0) / (len(averageActivityList) - len(offList))) / len(mutationDic)
                # print("attractorSimulation", mutationNet, (sum(averageActivityList) / (len(averageActivityList) - len(offList))))

            if len(priorityAddtionalSolutionSubList) == 1:
                additionalInput1score = totalScore
                add1Len = len(onList)
                addName = onList

            firstSolutionScoreSubDic[str(onList)] = totalScore
            print(onList, totalScore)
        firstSolutionScoreDic[str(firstSolutionList)] = firstSolutionScoreSubDic
        firstSolutionNumDic[str(firstSolutionList)] = len(onList)
        firstSolutionAdd1ScoreDic[str(firstSolutionList)] = additionalInput1score
        firstSolutionAdd1NameDic[str(firstSolutionList)] = addName



    '''
    Score 1. Average of add one solutions vs Average of all combinations in original FVSs
    '''
    # Average of add one solutions
    firstSolutionAdd1List = [firstSolutionAdd1ScoreDic[x] for x in firstSolutionAdd1ScoreDic]
    firstSolutionAdd1Avg = sum(firstSolutionAdd1List) / len(firstSolutionAdd1List)


    # Average of all combinations in original FVSs
    totalScoreList = []
    s = 0
    totalCombinationNumber = nCr(len(originalSolutionListList[0]), add1Len) * len(originalSolutionListList)
    for originalSolutionList in originalSolutionListList:
        for originalSolutionSampleList in itertools.combinations(originalSolutionList, add1Len):
            s += 1
            onList = originalSolutionSampleList
            totalScore = 0
            for mutationNet in mutationDic:
                offList = mutationDic[mutationNet]
                path = "./perturbation/" + str(mutationNet) + "_" + str(onList) + ".json"
                attractorSimulation(bnGNetForAttr, 1000, 200, onList, offList, path)
                averageActivityList = averageActivity(path)
                os.remove(path)
                totalScore += (averageActivityList.count(1) / (len(averageActivityList) - len(offList))) / len(mutationDic)
            totalScoreList.append(totalScore)
            print(str(s) + "/" + str(totalCombinationNumber) + ":",  onList, totalScore)
    originalSolutionAvg = sum(totalScoreList) / len(totalScoreList)
    # print(firstSolutionAdd1Avg, originalSolutionAvg)



    '''
    Score 2. Max of add one solutions vs max of original FVSs
    '''
    # Max of add one solutions
    optimalFirstSolution = max(firstSolutionAdd1ScoreDic, key=firstSolutionAdd1ScoreDic.get)
    firstSolutionAdd1MaxName = firstSolutionAdd1NameDic[optimalFirstSolution]
    firstSolutionAdd1Max = firstSolutionAdd1ScoreDic[optimalFirstSolution]
    firstSolutionNum = firstSolutionNumDic[optimalFirstSolution]



    # Max of original FVSs
    originalSolutionScoreDic = {}
    for originalSolutionList in originalSolutionListList:
        onList = originalSolutionList
        totalScore = 0
        for mutationNet in mutationDic:
            offList = mutationDic[mutationNet]
            path = "./perturbation/" + str(mutationNet) + "_" + str(onList) + ".json"
            attractorSimulation(bnGNetForAttr, 1000, 200, onList, offList, path)
            averageActivityList = averageActivity(path)
            os.remove(path)
            totalScore += (averageActivityList.count(1) / (len(averageActivityList) - len(offList))) / len(mutationDic)
        originalSolutionScoreDic[str(onList)] = totalScore
    originalSolutionMaxName = ast.literal_eval(max(originalSolutionScoreDic, key=originalSolutionScoreDic.get))
    originalSolutionMax = originalSolutionScoreDic[str(originalSolutionMaxName)]



    # Time result
    oriTime = oriTime
    proTime = proTime_transformation + proTime_FVS + sum(proTime_AddtionalInput_List) / len(proTime_AddtionalInput_List)



    # Result
    net = str(net)
    pro_avg = str(firstSolutionAdd1Avg)
    ori_avg = str(originalSolutionAvg)
    pro_max = str(firstSolutionAdd1Max)
    ori_max = str(originalSolutionMax)
    pro_max_num = str(len(firstSolutionAdd1MaxName))
    ori_max_num = str(len(originalSolutionMaxName))
    pro_ori_max_jaccard = str(jaccardSimilarity(firstSolutionAdd1MaxName, originalSolutionMaxName))
    pro_max_control100_num = str(firstSolutionNum)
    pro_time = str(proTime)
    ori_time = str(oriTime)

    "net,pro_avg,ori_avg,pro_max,ori_max,pro_max_num,ori_max_num,pro_ori_max_jaccard,pro_max_control100_num,pro_time,ori_time\n"
    result = net + "," + pro_avg + "," + ori_avg + "," + pro_max + "," + ori_max + "," + pro_max_num + "," + ori_max_num + "," + pro_ori_max_jaccard + "," + pro_max_control100_num + "," + pro_time + "," + ori_time + "\n"
    print(result + "\n\n")



    # Save files
    with open("./score/node" + str(nodeLen) + "/result.csv", "a") as text_file:
        text_file.write(result)

    with open("./specification/node" + str(nodeLen) + "/networks/" + net + ".txt", "w") as text_file:
        text_file.write(bnOriNet)

    pickle.dump(firstSolutionScoreDic, open("./specification/node" + str(nodeLen) + "/pro_solutions/" + net + ".p", "wb"))

    pickle.dump(mutationDic, open("./specification/node" + str(nodeLen) + "/mutations/" + net + ".p", "wb"))

    maxSolutions = "pro: " + str(firstSolutionAdd1MaxName) + "\nori: " + str(originalSolutionMaxName)
    with open("./specification/node" + str(nodeLen) + "/maxSolutions/" + net + ".txt", "w") as text_file:
        text_file.write(maxSolutions)


