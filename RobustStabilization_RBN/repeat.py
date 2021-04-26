import os
import time
start_time = time.time()

nodeLen = 20

scorePath = './score/node' + str(nodeLen)
specificationPath1 = './specification/node' + str(nodeLen)
specificationPath2 = './specification/node' + str(nodeLen) + '/maxSolutions'
specificationPath3 = './specification/node' + str(nodeLen) + '/mutations'
specificationPath4 = './specification/node' + str(nodeLen) + '/networks'
specificationPath5 = './specification/node' + str(nodeLen) + '/pro_solutions'

try:
    if not os.path.exists(scorePath):
        os.makedirs(scorePath)
        os.makedirs(specificationPath1)
        os.makedirs(specificationPath2)
        os.makedirs(specificationPath3)
        os.makedirs(specificationPath4)
        os.makedirs(specificationPath5)
except OSError:
    print('Error: Creating directory')

with open('./score/node' + str(nodeLen) + '/result.csv', "w") as text_file:
    text_file.write("")

v = True
while v:
    lines = open('./score/node' + str(nodeLen) + '/result.csv').read().splitlines()
    currentNum = len(lines)
    print("Num: ", currentNum)

    if currentNum > 0:
        i = currentNum + 1
    else:
        i = 1

    if i >= 1000:
        v = False

    path = "python ./scaleFreeBNgenerator.py {0}".format(str(nodeLen))
    os.system(path)

    path = "python ./main.py {0} {1}".format(str(i), str(nodeLen))
    os.system(path)

print(time.time() - start_time)