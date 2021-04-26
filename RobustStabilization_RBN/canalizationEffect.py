"""
BNsimpleReduction
Created on Jan Feb 8 2021
Code author : Chun-Kyung Lee(Korea Advanced Institute of Science and Technology)
Contact: chunkyung@kaist.ac.kr
"""
import re
from sympy.logic import simplify_logic

def main(modeltext, canalizingNodeDic):
    '''
    :param modeltext: Network model
    :param canalizingNodeDic: Canalizing node dicttionary
    :return:
        modeltext: residual network
        canalizedStateVectorDic: canalized state vector list
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

    newCanalizedStateVectorDic = {}
    for canalizedNode in canalizedStateVectorDic:
        if canalizedNode in allNodeList:
            newCanalizedStateVectorDic[canalizedNode] = canalizedStateVectorDic[canalizedNode]


    return modeltext, newCanalizedStateVectorDic, stepCanalizedStateVectorList, allStateVectorDic, additionalSolutionList

modeltext = '''
x02 = x05
x04 = x12 | x13
x05 = x17 | x18
x06 = x04 | ~x10
x07 = x10
x08 = x10 | (x13 & x18)
x09 = x09
x10 = ~x13
x12 = x12
x13 = ~x02 | (x04 & x10)
x15 = x02
x17 = x13 | ~x05
x18 = x04 & (x08 | ~x15)
'''
canalizingNodeDic = {'x30': True, 'x02': True}

modeltext = modeltext.strip()



modeltext, canalizedStateVectorDic, stepCanalizedStateVectorList, allStateVectorDic, additionalSolutionList = main(modeltext, canalizingNodeDic)
print("1. modeltext:")
print(modeltext)
print("2. canalizedStateVectorDic:", canalizedStateVectorDic)
print("3. stepCanalizedStateVectorList:", stepCanalizedStateVectorList)
print("4. allStateVectorDic:", allStateVectorDic)
print("5, additionalSolutionList:", additionalSolutionList)