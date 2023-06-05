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


#MANUAL CONTROLL CODE

# act_int = int(input("Enter move: "))

            # agent.action = act_int

            # act_encode = agent.int2act(act_int)

            # if act_encode[0] == 1:
            #     agent.act_seat(groups[act_encode[1][0]], tables[act_encode[1][1]], kitchen)

            # if act_encode[0] == 2:
            #     agent.act_serve(groups[act_encode[1]], kitchen)

            # if act_encode[0] == 3:
            #     group = groups[act_encode[1]]
            #     table = group.table
            #     agent.act_bill(group, table)