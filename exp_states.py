import numpy as np

def is_legit(state):
    if state[0] == 1 and state[6]+state[7]+state[8]+state[9] > 4:
        val = False
    elif state[1] == 1 and state[10]+state[11]+state[12] > 3:
        val = False
    elif state[2] == 1 and state[13]+state[14] > 2:
        val = False
    else:
        val = True
    return val

tables = {'place': {
            '2': 1, 
            '3': 1, 
            '4': 1},
          'state': [
              'empty', 
              'waiting for food', 
              'eating', 
              'waiting for bill']
}

queue = {'place': {
            '2': 1,
            '3': 1,
            '4': 1}
}

plates = {'state': [
            'none',
            'preparing',
            'ready']
}

count = 0
for t1 in range(4):
    print(t1)
    for t2 in range(4):
        for t3 in range(4):
            for q1 in range(2):
                for q2 in range(2):
                    for q3 in range(2):
                        for p1 in range(3):
                            for p2 in range(3):
                                for p3 in range(3):
                                    for p4 in range(3):
                                        for p5 in range(3):
                                            for p6 in range(3):
                                                for p7 in range(3):
                                                    for p8 in range(3):
                                                        for p9 in range(3):
                                                            state = np.array([t1, t2, t3, q1, q2, q3, p1, p2, p3, p4, p5, p6, p7, p8, p9])
                                                            if  is_legit(state):
                                                                count += 1

print(count)
                                                                