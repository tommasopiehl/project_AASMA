from waiter_new import Agent, Table, ClientGroup, Kitchen, AgentControllerRL, Order
import numpy as np
import random

def main_game(n_tables, n_groups):

    game_over = 0
    agent = Agent()
    agent.action = 0
    agent.init_actions()
    agent.R_total = 0

    controller = AgentControllerRL()
    controller.agent = agent
    controller.diff = 0

    tables = []
    groups = []
    orders = []

    #Init kitchen
    
    kitchen = Kitchen()
    kitchen.init_menu()
    kitchen.waiting_cnt = 0
    kitchen.cooking_cnt = 0
    kitchen.ready_cnt = 0
    agent.kitchen = kitchen

    for i in range(len(n_groups)):
        kitchen.ready[i] = 0

    #Init q-table

    q_rows, rows_count = controller.compute_rows()
    controller.q_init(q_rows=q_rows, rows_count=rows_count)

    # Init lists with all our table, group and order objects

    for i in range(len(n_tables)):

        table = Table(k = n_tables[i])
        group = ClientGroup()
        order = Order()

        table.state = 0
        table.index = i

        group.state = 0
        group.index = i
        group.size = i + 2
        order.state = 0
        order.size = group.size

        order.group = group
        group.order = order

        order.dishes = np.zeros(order.group.size)

        tables.append(table)
        groups.append(group)
        orders.append(order)

    time = 0

    while game_over != 1:

            go = int(input("Press 1 to contiue: "))
            if go == 1:
                terminal = 1
                
                print("-----------")
                print("time: ", time)
                print("CURRENT DIFF", controller.diff)
                print("-----------")

                kitchen.kitchen_step(orders=orders)
                reward = 0

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

                for group in groups:
                    if group.state != 4:
                        terminal = 0
                        group.waiting[group.state] += 1
                    if group.state == 2:
                        if group.waiting[2] == 4:
                            group.state = 3
                        

                current = controller.env2array(agent, groups=groups, tables=tables, orders=orders)
                current_row = controller.Q[q_rows.index(current)]
                check_nan = np.isnan(current_row)

                if False not in check_nan:
                    if terminal == 1:
                        game_over = 1

                allowed_reformat = []
                for i in range(len(current_row)):
                    if(np.isnan(current_row[i]) == False):
                        allowed_reformat.append(i)
                print("allowed moves:", allowed_reformat)
                print("current states, agent:", current[0], ", orders:", current[1:4], " groups:", current[4:7], " tables:", current[7:10])
                int_act = controller.epsilon_greedy(controller.Q, allowed_reformat, q_rows.index(current))
                print("current move: ", agent.act2str(int_act))
                agent.action = int_act

                act_encode = agent.int2act(int_act)

                if act_encode[0] == 0:
                    reward = agent.reward_wait(allowed_reformat)

                if act_encode[0] == 1:
                    group = groups[act_encode[1][0]]
                    table = tables[act_encode[1][1]]
                    agent.act_seat(group, table, kitchen)
                    reward = agent.reward_seat(group, table, groups)

                if act_encode[0] == 2:
                    group = groups[act_encode[1]]
                    agent.act_serve(group, kitchen)
                    reward = agent.reward_serve(group, groups)

                if act_encode[0] == 3:
                    group = groups[act_encode[1]]
                    table = group.table
                    agent.act_bill(group, table)
                    reward = agent.reward_bill(group, groups)

                next = controller.env2array(agent, groups=groups, tables=tables, orders=orders)
                Q_old = controller.Q.copy()
                
                controller.q_update(Q_old, q_rows, current, next, reward, int_act)

                time += 1

                for group in groups:
                    if group.state == 4:
                        group.reset_group()

                print("/\/\/\/\/\/")

    return 0

main_game(n_tables = (2, 3, 4), n_groups = (2, 3, 4))

