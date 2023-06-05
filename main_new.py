from waiter_new import Agent, Table, ClientGroup, Kitchen, AgentControllerRL, Order
import numpy as np
import random

# modes: constant = q-learning with constant epsilon, linear = q_learning with linear epsilon, random = random agent
def main_game(n_tables, n_groups, mode="constant"): 

    diff_Q = 0
    n_batches = 35 # How many "groups of client-groups" we will let in during the entire process
    wait_ls = np.zeros(n_batches)
    reward_ls = np.zeros(n_batches)
    bad_moves = np.zeros(n_batches)
    mood_ls = np.zeros(n_batches)
    current_batch = 0
    done_cnt = 0
    
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
        group.batch = current_batch
        order.state = 0
        order.size = group.size

        order.group = group
        group.order = order

        order.dishes = np.zeros(order.group.size)

        tables.append(table)
        groups.append(group)
        orders.append(order)

    time = 0

    while current_batch < n_batches:
                
                print("-----------")
                print("time: ", time)
                print("CURRENT DIFF", diff_Q)
                print("CURRENT BATCH", current_batch)
                print("-----------")

                kitchen.kitchen_step(orders=orders)
                reward = 0

                #Add waiting time to each group
                for group in groups:
                    if group.state != 4:
                        terminal = 0
                        group.waiting[group.state] += 1
                        group.compute_mood(group.waiting[group.state])

                        wait_ls[group.batch] += group.waiting[group.state] #Track the total waiting time of each batch
                        mood_ls[group.batch] += group.mood #Track the mood of each batch
                    if group.state == 2: #Each group stays in eating for 4 steps before asking for bill
                        if group.waiting[2] == 4:
                            group.state = 3
                
                current = controller.env2array(agent, groups=groups, tables=tables, orders=orders)
                current_row = controller.Q[q_rows.index(current)]

                allowed_reformat = []
                for i in range(len(current_row)):
                    if(np.isnan(current_row[i]) == False):
                        allowed_reformat.append(i)

                #Epsilon greedy constant algorithm:
                if mode == "constant":
                    int_act = controller.epsilon_greedy(controller.Q, allowed_reformat, q_rows.index(current), eps_type= "constant")

                if mode == "linear":
                    int_act = controller.epsilon_greedy(controller.Q, allowed_reformat, q_rows.index(current), eps_type= "linear")

                #Random agent
                if mode == "random":
                    int_act = np.random.choice(allowed_reformat)

                agent.action = int_act

                act_encode = agent.int2act(int_act)

                if act_encode[0] == 0:
                    reward = agent.reward_wait(allowed_reformat)
                    reward_ls[current_batch] += reward
                    if len(allowed_reformat) > 1:
                        bad_moves[current_batch] += 1
                    else:
                        print("Only move")

                if act_encode[0] == 1:
                    group = groups[act_encode[1][0]]
                    table = tables[act_encode[1][1]]
                    if group.size != table.size:
                        bad_moves[current_batch] += 1
                    agent.act_seat(group, table, kitchen)
                    reward = agent.reward_seat(group, table, groups, allowed_reformat)
                    reward_ls[group.batch] += reward

                if act_encode[0] == 2:
                    group = groups[act_encode[1]]
                    agent.act_serve(group, kitchen)
                    reward = agent.reward_serve(group, groups, allowed_reformat)
                    reward_ls[group.batch] += reward

                if act_encode[0] == 3:
                    group = groups[act_encode[1]]
                    table = group.table
                    agent.act_bill(group, table)
                    reward = agent.reward_bill(group, groups, allowed_reformat)
                    reward_ls[group.batch] += reward


                #Epsilon greedy algorithm:
                if mode == "constant" or mode == "linear":
                    next = controller.env2array(agent, groups=groups, tables=tables, orders=orders)
                    Q_old = controller.Q.copy()
                    
                    controller.q_update(Q_old, q_rows, current, next, reward, int_act)

                    diff_Q += np.abs(np.nanmean(controller.Q) - np.nanmean(Q_old))

                time += 1

                for group in groups:
                    if group.state == 4:
                        done_cnt += 1
                        if done_cnt == 3:
                            for group in groups:
                                group.reset_group()
                                group.batch += 1
                                current_batch = group.batch
                                done_cnt = 0

    print("Result for ", mode, "mode with alpha:", controller.alpha, " and gamma:", controller.gamma)
    print("waiting time per batch:",wait_ls)
    print("total reward per batch:", reward_ls)
    print("overall mood of clients per batch:", mood_ls)
    print("bad moves per batch:", bad_moves)
    print("diff Q:", diff_Q)

    return 0

main_game(n_tables = (2, 3, 4), n_groups = (2, 3, 4), mode="linear")

