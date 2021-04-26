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

def main(path, desiredAttr, mutationDic):
    # Set output path
    fileNameNoEx = os.path.splitext(os.path.basename(path))[0]
    outputDir = "./results/" + fileNameNoEx + "_" + str(desiredAttr)

    # Load the network
    with open(path) as file:
        bnOriNet = file.read().strip()
    bnOriNet = bnOriNet.strip()

    # Transform string of one desired attractor to list type
    desiredAttrList = []
    for state in desiredAttr:
        desiredAttrList.append(int(state))

    # Get G network, all plus product network, and format for original FVSs
    proTime_transformation_start = time.time()
    bnGNet, bnAllPlusProductNet, formatFVSori, inputNodeList = allPlusProducts.main(bnOriNet, desiredAttr)
    # print("inputNodeList", inputNodeList)

    # Get the format for first solutions
    formatFVSoptOnePlus = optOnePlusProduct.main(bnAllPlusProductNet)
    proTime_transformation = time.time() - proTime_transformation_start

    # Find FVSs
    with open("./fvsfinder/networks/formatFVSoptOnePlus.csv", "w") as text_file:
        text_file.write(formatFVSoptOnePlus)
    proTime_FVS_start = time.time()
    fv.FVSFinder("formatFVSoptOnePlus.csv", "formatFVSoptOnePlus.txt")
    proTime_FVS = time.time() - proTime_FVS_start

    # First solution sets
    with open("./fvsfinder/result/formatFVSoptOnePlus.txt") as file:
        firstSolutionText = file.read().splitlines()
    firstSolutionListList = []
    for firstSolution in firstSolutionText:
        firstSolutionListList.append(ast.literal_eval(firstSolution))

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

    # Mutations
    # mutationDic = {'G0': ['TWIST1'], 'G1': ['AKT2']}
    mutationList = [mutationDic[x] for x in mutationDic]
    mutationList = sum(mutationList, [])

    # if mutations exist in first solution list, remove that
    newFirstSolutionListList = []
    for firstSolutionList in firstSolutionListList:
        process = True
        for mutationNode in mutationList:
            if mutationNode in firstSolutionList:
                process = False
                continue
        if process:
            newFirstSolutionListList.append(firstSolutionList)
    firstSolutionListList = newFirstSolutionListList

    if len(firstSolutionListList) < 1:
        print("The process aborted because the mutations occurs to the control inputs in all the control input sets")

    # Replace ('&', '|', and '~') with ('and', 'or', and 'not') respectively
    substitutions = {"&": "and", "|": "or", "~": "not "}
    bnGNet = replace(bnGNet, substitutions)

    # Recursive canalization
    finalSolutionListList = []
    for firstSolutionList in firstSolutionListList:
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

            for inputNode in inputNodeList:
                canalizingNodeDic[inputNode] = True

            canalizedNetString, additionalSolutionList, _ = canalizationEffect(bnGNet, canalizingNodeDic)
            # print("additionalSolutionList", additionalSolutionList)
            # print("canalizedNetString", canalizedNetString)

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

        # Final additional inputs ordered
        finalSolutionListList.append([firstSolutionList, priorityAddtionalSolutionList])
        # print("priorityAddtionalSolutionList", priorityAddtionalSolutionList, firstSolutionList)

    # print(finalSolutionListList)

    finalSolutionStr = "Control inputs, Additional control inputs\n"
    for finalSolutionList in finalSolutionListList:
        finalSolutionStr += str(tuple(finalSolutionList[0])) + ", " + str(tuple(finalSolutionList[1])) + "\n"

    print(finalSolutionStr)

    with open(outputDir, "w") as text_file:
        text_file.write(finalSolutionStr)