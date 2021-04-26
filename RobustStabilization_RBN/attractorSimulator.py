import json
from os.path import exists
from boolean3_addon import attr_cy

def main(modeltext, samples, steps):

    attr_cy.build(modeltext)

    import pyximport; pyximport.install()

    res = attr_cy.run(samples=samples, steps=steps, debug=False, progress=True)
    # on_states*=['A01', 'A51'], off_states*=['A38', 'A40']
    # debug needs to be changed to 'True' to check trajectory
    json.dump(res, open('repeat.json', 'w'), indent=4)

    with open('repeat.json') as data_file:
        data = json.load(data_file)

    attrKeyList = data["attractors"].keys()
    attrAllType = [0, 0, 0]
    z = 1
    for attrKey in attrKeyList:
        attrType = data["attractors"][attrKey]["type"]
        attrRatio = data["attractors"][attrKey]["ratio"]

        if attrType == "point":
            attrAllType[0] = attrAllType[0] + 1
            attrValue = data["attractors"][attrKey]["value"]
            pointAttr = data["state_key"][attrValue]

        elif attrType == "cyclic":
            attrAllType[1] = attrAllType[1] + 1
            for attrValue in data["attractors"][attrKey]["value"]:
                cyclicAttr = data["state_key"][attrValue]

        else:
            attrAllType[2] = attrAllType[2] + 1
        z = z + 1

    totalAttr = attrAllType[0] + attrAllType[1]
    totalPointAttr = attrAllType[0]
    if not ((totalAttr > 1) & (totalPointAttr >= 1)):
        result = False
    else:
        result = pointAttr

    return result