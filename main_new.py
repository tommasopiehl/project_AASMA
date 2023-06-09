from waiter_new import Agent, Table, ClientGroup, Kitchen, AgentControllerRL, Order
import numpy as np
import random
import matplotlib.pyplot as plt
import json

# modes: constant = q-learning with constant epsilon, linear = q_learning with linear epsilon, random = random agent
def main_game(n_tables, n_groups, mode="constant", episodes = 20, alpha = 0.8, gamma = 0.3): 
    #
    data = []
    #

    #CHANGE n_batches to episodes
    n_batches = episodes # How many "groups of client-groups" we will let in during the entire process

    reward_ls = np.zeros(n_batches+1)
    bad_moves = np.zeros(n_batches+1)
    complete_ls = np.zeros(n_batches+1)
    q_diff = np.zeros(n_batches+1)

    current_batch = -1
    conv_batch = -1
    n_completed = 0
    max_episode = 30
    
    agent = Agent()
    agent.action = 0
    agent.init_actions()
    agent.R_total = 0

    controller = AgentControllerRL()
    controller.alpha = alpha
    controller.gamma = gamma
    controller.agent = agent
    controller.diff = 0

    #Init q-table

    q_rows, rows_count = controller.compute_rows()
    controller.q_init(q_rows=q_rows, rows_count=rows_count)

    time = 0


    if mode == "sarsa":
        while current_batch < n_batches:

            Q_old = controller.Q.copy()

            current_batch += 1
            episode_time = 0
            episode_done = 0
            done_ls = []

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
                order.dishes = []
                group.order = order

                for j in range(n_tables[i]):
                    order.dishes.append(random.choice([0, 1]))

                tables.append(table)
                groups.append(group)
                orders.append(order)


            #FIRST STEP
            kitchen.kitchen_step(orders=orders)
            reward = 0

            #Add waiting time to each group
            for group in groups:
                if group.state != 4:
                    group.waiting[group.state] += 1
                    group.compute_mood(group.waiting[group.state])
                if group.state == 2: #Each group stays in eating for 4 steps before asking for bill
                    if group.waiting[2] == 4:
                        group.state = 3
            
            current = controller.env2array(agent, groups=groups, tables=tables, orders=orders)
            current_row = controller.Q[q_rows.index(current)]

            allowed_reformat = []
            for i in range(len(current_row)):
                if(np.isnan(current_row[i]) == False):
                    allowed_reformat.append(i)

            int_act = controller.epsilon_greedy(controller.Q, allowed_reformat, q_rows.index(current), current_total_steps = time, eps_type= "sarsa")
            
            agent.action = int_act

            act_encode = agent.int2act(int_act)

            if act_encode[0] == 0:
                reward = agent.reward_wait(allowed_reformat)
                reward_ls[current_batch] += reward
                if len(allowed_reformat) > 1:
                    bad_moves[current_batch] += 1

            if act_encode[0] == 1:
                group = groups[act_encode[1][0]]
                table = tables[act_encode[1][1]]
                if group.size != table.size:
                    bad_moves[group.batch] += 1

                agent.act_seat(group, table, kitchen)
                reward = agent.reward_seat(group, table, groups, tables, allowed_reformat)
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

            while episode_time < max_episode and episode_done == 0:

                    print("time: ", time)
                    print("CURRENT EPISODE", current_batch)

                    kitchen.kitchen_step(orders=orders)
                    reward = 0

                    #Add waiting time to each group
                    for group in groups:
                        if group.state != 4:
                            group.waiting[group.state] += 1
                            group.compute_mood(group.waiting[group.state])
                        if group.state == 2: #Each group stays in eating for 4 steps before asking for bill
                            if group.waiting[2] == 4:
                                group.state = 3
                    
                    nextState = controller.env2array(agent, groups=groups, tables=tables, orders=orders)
                    nextRow = controller.Q[q_rows.index(nextState)]

                    allowed_reformat = []
                    for i in range(len(nextRow)):
                        if(np.isnan(nextRow[i]) == False):
                            allowed_reformat.append(i)

                    nextAct = controller.epsilon_greedy(controller.Q, allowed_reformat, q_rows.index(nextState), current_total_steps = time, eps_type= "sarsa")

                    agent.action = nextAct

                    act_encode = agent.int2act(nextAct)

                    if act_encode[0] == 0:
                        reward = agent.reward_wait(allowed_reformat)
                        reward_ls[current_batch] += reward
                        if len(allowed_reformat) > 1:
                            bad_moves[current_batch] += 1

                    if act_encode[0] == 1:
                        group = groups[act_encode[1][0]]
                        table = tables[act_encode[1][1]]
                        if group.size != table.size:
                            bad_moves[group.batch] += 1

                        agent.act_seat(group, table, kitchen)
                        reward = agent.reward_seat(group, table, groups, tables, allowed_reformat)
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

                    controller.sarsaUpdate(Q_old, q_rows, current, nextState, reward, int_act, nextAct)

                    current = nextState
                    int_act = nextAct

                    for group in groups:
                        if group.state == 4 and group.index not in done_ls:
                            done_ls.append(group.index)

                    if len(done_ls) == 3:
                        episode_done = 1

                    time += 1
                    episode_time += 1

            if len(done_ls) == 3:  
                n_completed += 1
        
            complete_ls[current_batch] = episode_time  

            q_diff[current_batch] = np.abs(np.nanmean(controller.Q) - np.nanmean(Q_old))
        

    else:
        while current_batch < n_batches:

            Q_old = controller.Q.copy()

            current_batch += 1
            episode_time = 0
            episode_done = 0
            done_ls = []

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
                order.dishes = []
                group.order = order

                for j in range(n_tables[i]):
                    order.dishes.append(random.choice([0, 1]))

                tables.append(table)
                groups.append(group)
                orders.append(order)

            while episode_time < max_episode and episode_done == 0:

                print("time: ", time)
                print("CURRENT EPISODE", current_batch)

                kitchen.kitchen_step(orders=orders)
                reward = 0

                #Add waiting time to each group
                for group in groups:
                    if group.state != 4:
                        group.waiting[group.state] += 1
                        group.compute_mood(group.waiting[group.state])
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
                    int_act = controller.epsilon_greedy(controller.Q, allowed_reformat, q_rows.index(current), current_total_steps = time, eps_type= "constant")

                if mode == "linear":
                    int_act = controller.epsilon_greedy(controller.Q, allowed_reformat, q_rows.index(current), current_total_steps = time, eps_type= "linear")

                #Random agent
                if mode == "random":
                    int_act = np.random.choice(allowed_reformat)

                agent.action = int_act

                #
                add_data = {
                    "batch": current_batch,
                    "time": time,
                    "current": np.array(current).tolist(),
                    "action": int_act
                }
                data.append(add_data)
                #

                act_encode = agent.int2act(int_act)

                if act_encode[0] == 0:
                    reward = agent.reward_wait(allowed_reformat)
                    reward_ls[current_batch] += reward
                    if len(allowed_reformat) > 1:
                        bad_moves[current_batch] += 1

                if act_encode[0] == 1:
                    group = groups[act_encode[1][0]]
                    table = tables[act_encode[1][1]]
                    if group.size != table.size:
                        bad_moves[group.batch] += 1

                    agent.act_seat(group, table, kitchen)
                    reward = agent.reward_seat(group, table, groups, tables, allowed_reformat)
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
                    controller.q_update(Q_old, q_rows, current, next, reward, int_act)

                for group in groups:
                    if group.state == 4 and group.index not in done_ls:
                        done_ls.append(group.index)

                if len(done_ls) == 3:
                    episode_done = 1

                time += 1
                episode_time += 1

            if len(done_ls) == 3:  
                n_completed += 1
        
            complete_ls[current_batch] = episode_time  

        if mode == "constant" or mode == "linear":
            q_diff[current_batch] = np.abs(np.nanmean(controller.Q) - np.nanmean(Q_old))

    print("Result for ", mode, "mode with alpha:", controller.alpha, " and gamma:", controller.gamma)
    print("total reward per batch:", reward_ls)
    print("bad moves per batch:", bad_moves)
    print("random:", controller.n_random, " best:", controller.n_best)
    print("average episode len:", np.sum(complete_ls)/len(complete_ls))
    print("n completed:", n_completed)
    print("n bad moves", np.sum(bad_moves))
    print("total reward", np.sum(reward_ls))

    plt.figure()
    plt.plot(reward_ls)
    plt.xlabel("Episode")
    plt.ylabel("Total reward")

    plt.figure()
    plt.plot(bad_moves)
    plt.xlabel("Episode")
    plt.ylabel("Bad moves")

    plt.figure()
    plt.plot(complete_ls)
    plt.xlabel("Episode")
    plt.ylabel("Time to complete")

    plt.figure()
    plt.plot(q_diff)
    plt.xlabel("Episode")
    plt.ylabel("Q diff")

    plt.show()

    #
    with open("states.json", "w") as json_file:
        json.dump(data, json_file)
        json_file.close()
    #
    
    return 0


main_game(n_tables = (2, 3, 4), n_groups = (2, 3, 4), mode="linear", episodes = 100, alpha = 0.9, gamma = 0.3)

#CONVERGES LATER BECAUSE OF EPS_INIT = 0.5

main_game(n_tables = (2, 3, 4), n_groups = (2, 3, 4), mode="linear", episodes = 200, alpha = 0.7, gamma = 0.3)
