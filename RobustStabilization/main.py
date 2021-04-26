"""
RobustStabilization
Created on 2021.04.01
Code author : Chun-Kyung Lee(Korea Advanced Institute of Science and Technology)
Contact: chunkyung@kaist.ac.kr
"""

import RobustStabilization as RS
'''
RS.main(Parameter_1, Parameter_2, Parameter_3)
Parameter_1: Boolean network file
Parameter_2: Desired fixed point attractor (steady state) in the network
Parameter_3: Python dictionary object for mutation profile. Here, key is the name of the mutated network and value is the name of the mutated node.
'''
RS.main("./networks/metastasis_influence_network.txt", "00110010110000000000100001001011", {'G0': ['TWIST1'], 'G1': ['AKT2']})
