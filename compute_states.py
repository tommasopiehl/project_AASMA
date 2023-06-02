import random
import numpy
import itertools

def main():

    state_count = 0
    state_rows = []

    for state_agent in range(0, 4):
        for wait_kitchen in range(0, 9):
            for cook_kitchen in range(0, 4):
                for ready_kitchen in range(0, 9):
                        for state_group_1 in range(0, 4):
                            for state_group_2 in range(0, 4):
                                for state_group_3 in range(0, 4):
                                    for state_table_1 in range(0, 2):
                                        for state_table_2 in range(0, 2):
                                            for state_table_3 in range(0, 2):
                                                state_rows.append([state_agent, wait_kitchen, cook_kitchen, ready_kitchen, 
                                                state_group_1, state_group_2, state_group_3, state_table_1, state_table_2, state_table_3])

    return state_rows

#Total amount 31104