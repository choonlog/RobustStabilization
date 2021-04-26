
from numpy.random import random
import os, sys
import time
from ipdb import set_trace
from itertools import combinations, combinations_with_replacement
import hashlib
import json

__start_time = 0

FP_LENGTH = 10

def update(idx, max_idx, updates=1000, blocks=20):    
    global __start_time
    idx += 1
    if idx == 1:
        __start_time = time.time()
    elapsed_time = time.time() - __start_time
    avgtime = elapsed_time / idx;
    remaintime = (max_idx - idx)*avgtime
    if idx>max_idx:
        idx = max_idx
    # updates = 1000
    if max_idx < updates:
        updates = max_idx
    sys.stdout.flush()
    # blocks = 50
    if idx % (max_idx/updates) == 0 or (idx == max_idx):
        p = float(idx)/float(max_idx)
        s = '\r[%s] %.02f%% (%.01fs)' % ('#'*int(p*blocks), p*100.0, remaintime)
        sys.stdout.write(s)
        sys.stdout.flush()

    if idx == max_idx:
        sys.stdout.write('\n')
        sys.stdout.flush()

cdef detect_cycles( data ):
    fsize   = len(data)
    for msize in range(1, int(fsize/2) + 1):
        for index in range(fsize):
            left  = data[index:index+msize]
            right = data[index+msize:index+2*msize]
            if left == right:
                return index, msize

    return 0, 0

DEF num_nodes = 20
ctypedef int (*cfptr)(int*)
cdef cfptr eqlist[num_nodes]

cdef int __bool_fcn_0(int state[]):
    state_0=state[0]
    return state_0

cdef int __bool_fcn_1(int state[]):
    state_1= not state[16]
    return state_1

cdef int __bool_fcn_2(int state[]):
    state_2= not state[14]
    return state_2

cdef int __bool_fcn_3(int state[]):
    state_3=state[15] or ( not state[6] and  not state[8])
    return state_3

cdef int __bool_fcn_4(int state[]):
    state_4=state[12]
    return state_4

cdef int __bool_fcn_5(int state[]):
    state_5=state[2] or state[19]
    return state_5

cdef int __bool_fcn_6(int state[]):
    state_6=state[19]
    return state_6

cdef int __bool_fcn_7(int state[]):
    state_7= not state[19]
    return state_7

cdef int __bool_fcn_8(int state[]):
    state_8= not state[13]
    return state_8

cdef int __bool_fcn_9(int state[]):
    state_9=state[2]
    return state_9

cdef int __bool_fcn_10(int state[]):
    state_10=state[1]
    return state_10

cdef int __bool_fcn_11(int state[]):
    state_11=state[19]
    return state_11

cdef int __bool_fcn_12(int state[]):
    state_12= not state[12] or  not state[3]
    return state_12

cdef int __bool_fcn_13(int state[]):
    state_13=(state[4] and state[8] and  not state[16]) or (state[4] and state[0] and  not state[16])
    return state_13

cdef int __bool_fcn_14(int state[]):
    state_14= not state[12]
    return state_14

cdef int __bool_fcn_15(int state[]):
    state_15=(state[6] and state[1]) or (state[1] and state[4])
    return state_15

cdef int __bool_fcn_16(int state[]):
    state_16=(state[17] and state[8]) or (state[8] and  not state[3])
    return state_16

cdef int __bool_fcn_17(int state[]):
    state_17=state[3]
    return state_17

cdef int __bool_fcn_18(int state[]):
    state_18=state[8] or  not state[18]
    return state_18

cdef int __bool_fcn_19(int state[]):
    state_19=state[17] or  not state[7]
    return state_19

eqlist[0] = &__bool_fcn_0
eqlist[1] = &__bool_fcn_1
eqlist[2] = &__bool_fcn_2
eqlist[3] = &__bool_fcn_3
eqlist[4] = &__bool_fcn_4
eqlist[5] = &__bool_fcn_5
eqlist[6] = &__bool_fcn_6
eqlist[7] = &__bool_fcn_7
eqlist[8] = &__bool_fcn_8
eqlist[9] = &__bool_fcn_9
eqlist[10] = &__bool_fcn_10
eqlist[11] = &__bool_fcn_11
eqlist[12] = &__bool_fcn_12
eqlist[13] = &__bool_fcn_13
eqlist[14] = &__bool_fcn_14
eqlist[15] = &__bool_fcn_15
eqlist[16] = &__bool_fcn_16
eqlist[17] = &__bool_fcn_17
eqlist[18] = &__bool_fcn_18
eqlist[19] = &__bool_fcn_19

cdef int state0[num_nodes]
cdef int state1[num_nodes]

def simulate(steps=10, on_states=[], off_states=[]):
    node_list = ['x01', 'x02', 'x03', 'x04', 'x05', 'x06', 'x07', 'x08', 'x09', 'x10', 'x11', 'x12', 'x13', 'x14', 'x15', 'x16', 'x17', 'x18', 'x19', 'x20']
    state0[0]=random()>0.5
    state0[1]=random()>0.5
    state0[2]=random()>0.5
    state0[3]=random()>0.5
    state0[4]=random()>0.5
    state0[5]=random()>0.5
    state0[6]=random()>0.5
    state0[7]=random()>0.5
    state0[8]=random()>0.5
    state0[9]=random()>0.5
    state0[10]=random()>0.5
    state0[11]=random()>0.5
    state0[12]=random()>0.5
    state0[13]=random()>0.5
    state0[14]=random()>0.5
    state0[15]=random()>0.5
    state0[16]=random()>0.5
    state0[17]=random()>0.5
    state0[18]=random()>0.5
    state0[19]=random()>0.5
    on_idxes = [ node_list.index(s) for s in on_states]
    off_idxes = [ node_list.index(s) for s in off_states]
    state_list = []
    state_list.append(state0)

    for i in range(steps):
        for k in range(num_nodes):
            state1[k] = eqlist[k](state0)
        for k in on_idxes:
            state1[k] = True
        for k in off_idxes:
            state1[k] = False
        for k in range(num_nodes):
            state0[k] = state1[k]
        state_list.append(state0)

    return state_list


def fp(s):
    res = hashlib.sha224(repr(s).encode('utf-8')).hexdigest()
    return res[0:FP_LENGTH]

def prettify(state_data, trajectory=False):
    if trajectory==False: 
        return "".join( ['%d'%s for s in state_data] )        
    else:
        traj_value = [] 
        for state in state_data: 
            state_str = []
            for st0 in state:
                state_str.append('%d' % st0)

            traj_value.append("".join(state_str))

        return "-".join(traj_value)

def main(steps=30, samples=100, debug=False, progress=False, on_states=[], off_states=[]):

    res = {} 
    seen = {} 
    traj = {}
    
    for i in range(samples):
        if progress: 
            update(i, samples)

        values = simulate(steps=steps, on_states=on_states, off_states=off_states)
        idx, size = detect_cycles(values)

        if size == 1:
            attr_type = 'point'
        elif size > 1:
            attr_type = 'cyclic'
        elif size == 0:
            attr_type = 'unknown'
        else:        
            assert False        

        if attr_type == 'cyclic':
            cyc = values[idx : idx + size]
            head = sorted(cyc)[0]
            left = cyc[cyc.index(head) : len(cyc)]
            right = cyc[0 : cyc.index(head)]
            raw_attr = left + right 
            attr_id = fp(raw_attr)
            attr = [] 
        
            for state in raw_attr:
                fp_value = fp(state)
                attr.append(fp_value)
                seen[fp_value] = prettify(state, trajectory=False)
        else: # point
            raw_attr = values[-1]
            attr_id = fp(raw_attr)
            attr = attr_id
            seen[attr_id] = prettify(raw_attr, trajectory=False)
        
        if attr_id in res: 
            res[attr_id]['count'] += 1
        else: 
            res[attr_id] = {} 
            res[attr_id]['count'] = 1 
            res[attr_id]['type'] = attr_type
            res[attr_id]['value'] = attr
    
        res[attr_id]['ratio'] = float(res[attr_id]['count']) / float(samples)

        if debug: 
            if attr_type=='cyclic':
                has_trajectory=True
            else: 
                has_trajectory=False

            traj[i] = {
                'value': prettify(values, trajectory=True),
                'type': attr_type, 
                'attr': prettify(raw_attr, trajectory=has_trajectory)
                }

    result = {
        'attractors': res, 
        'state_key': seen, 
        'trajectory': traj, 
        'labels': ['x01', 'x02', 'x03', 'x04', 'x05', 'x06', 'x07', 'x08', 'x09', 'x10', 'x11', 'x12', 'x13', 'x14', 'x15', 'x16', 'x17', 'x18', 'x19', 'x20']
        }

    return result
