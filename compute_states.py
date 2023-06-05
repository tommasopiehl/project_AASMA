import random
import numpy
import itertools

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


#Code for printing info while running

# print("tables:")
                # for table in tables:
                #     print("table index:", table.index, ", table status:", table.status2str(), ", table size:", table.size)

                # print("groups")
                # for group in groups:
                #     if group.state != 4:
                #         group.waiting[group.state] += 1
                #     if group.state == 2:
                #         if group.waiting[2] == 4:
                #             group.state = 3
                #     print("index:", group.index, ", mood:", group.mood, ", state: ", group.state, "order state", group.order.state)

                # if time > 0:

                #     #Update kitchen before printing info

                #     print("cooking:", kitchen.cooking_cnt)
                #     for dish in kitchen.cooking:
                #         print("time left:", dish[0], ", group: ", dish[1])
                #     print("waiting:", kitchen.waiting_cnt)
                #     for dish in kitchen.waiting:
                #         print("time:", dish[0], ", group: ", dish[1])
                #     print("ready:", kitchen.ready_cnt)
                #     for dish in kitchen.ready.keys():
                #         print("group:", dish, ", count:", kitchen.ready[dish])

    #print("allowed moves:", allowed_reformat)
    #print("chosen move: ", agent.act2str(int_act))
    #print("Q row before update:", controller.Q[q_rows.index(current)])