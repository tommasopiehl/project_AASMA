import random
import numpy

def main():

    state_count = 0
    state_rows = []

    for state_agent in range(0, 4):
        for wait_kitchen in range(0, 9):
            for cook_kitchen in range(0, 4):
                for ready_kitchen in range(0, 9):
                    for i in range(0, 3): #loop over states in groups, kitchen lists and tables
                        for state_group in range(0, 4):
                            for state_table in range(0, 2):
                                state_count += 1

    return state_count

print(main())

#Total amount 31104