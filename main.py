import argparse
import string
from environment import Kitchen, Table, Order, ClientGroup, Restaurant, compute_rows
from agents import RandomAgent, QLearning, SARSA
import numpy as np
import random

# modes: constant = q_learning with constant epsilon, linear = q_learning with linear epsilon, sarsa = q_learning with sarsa algorithm, random = random agent
def main_game(controller, tables, groups, orders, agent, mode="random"): 

    diff_Q = 0
    n_episodes = 35 # How many "groups of client-groups" we will let in during the entire process
    wait_ls = np.zeros(n_episodes)
    reward_ls = np.zeros(n_episodes)
    bad_moves = np.zeros(n_episodes)
    mood_ls = np.zeros(n_episodes)
    episode = 0
    done_cnt = 0

    #Init q-table
    #TODO Change to q table to the agent
    q_rows, rows_count = compute_rows()
    agent.q_init(q_rows=q_rows, rows_count=rows_count)

    
    time = 0
    maxSteps = 100

    if mode == "sarsa":
        while episode < n_episodes:
            allowed_reformat = []

            current = controller.env2array(agent, groups=groups, tables=tables, orders=orders)

            current_row = controller.Q[q_rows.index(current)]

            for i in range(len(current_row)):
                    if(np.isnan(current_row[i]) == False):
                        allowed_reformat.append(i)

            currentAction = controller.epsilon_greedy(controller.Q, allowed_reformat, q_rows.index(current), eps_type= "sarsa")

            while time < maxSteps:
                print("-----------")
                print("time: ", time)
                print("CURRENT DIFF", diff_Q)
                print("CURRENT BATCH", episode)
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
                
                current_row = controller.Q[q_rows.index(current)]

                for i in range(len(current_row)):
                    if(np.isnan(current_row[i]) == False):
                        allowed_reformat.append(i)


                agent.state = currentAction

                act_encode = agent.int2act(currentAction)

                if act_encode[0] == 0:
                    reward = agent.reward_wait(allowed_reformat)
                    reward_ls[episode] += reward
                    if len(allowed_reformat) > 1:
                        bad_moves[episode] += 1
                    else:
                        print("Only move")

                if act_encode[0] == 1:
                    group = groups[act_encode[1][0]]
                    table = tables[act_encode[1][1]]
                    if group.size != table.size:
                        bad_moves[episode] += 1
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

                nextState = controller.env2array(agent, groups=groups, tables=tables, orders=orders)
                oldQ = controller.Q.copy()

                nextAction = controller.epsilon_greedy(controller.Q, allowed_reformat, q_rows.index(nextState))
                controller.sarsaUpdate(oldQ, q_rows, current, nextState, reward, currentAction, nextAction)

                diff_Q += np.abs(np.nanmean(controller.Q) - np.nanmean(oldQ))

                current = nextState
                currentAction = nextAction

                time += 1

                for group in groups:
                    if group.state == 4:
                        done_cnt += 1
                        
                if done_cnt == 3:
                    done_cnt = 0

                    for group in groups:
                        group.reset_group()
                        group.batch += 1
                        episode = group.batch

                    break

                done_cnt = 0
            

    else:
        while episode < n_episodes:
            
            print("-----------")
            print("time: ", time)
            print("CURRENT DIFF", diff_Q)
            print("CURRENT BATCH", episode)
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
            current_row = agent.Q[q_rows.index(current)]

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
                int_act = agent.action(allowed_reformat)

            agent.state = int_act

            act_encode = agent.int2act(int_act)

            if act_encode[0] == 0:
                reward = agent.reward_wait(allowed_reformat)
                reward_ls[episode] += reward
                if len(allowed_reformat) > 1:
                    bad_moves[episode] += 1
                else:
                    print("Only move")

            if act_encode[0] == 1:
                group = groups[act_encode[1][0]]
                table = tables[act_encode[1][1]]
                if group.size != table.size:
                    bad_moves[episode] += 1
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
                nextState = controller.env2array(agent, groups=groups, tables=tables, orders=orders)
                Q_old = controller.Q.copy()
                
                controller.q_update(Q_old, q_rows, current, nextState, reward, int_act)

                diff_Q += np.abs(np.nanmean(controller.Q) - np.nanmean(Q_old))

            time += 1

            for group in groups:
                if group.state == 4:
                    done_cnt += 1
                        
            if done_cnt == 3:
                done_cnt = 0

                for group in groups:
                    group.reset_group()
                    group.batch += 1
                    episode = group.batch
                # break

            done_cnt = 0

    print("Result for ", mode, "mode with alpha:", controller.alpha, " and gamma:", controller.gamma)
    print("waiting time per batch:",wait_ls)
    print("total reward per batch:", reward_ls)
    print("overall mood of clients per batch:", mood_ls)
    print("bad moves per batch:", bad_moves)
    print("diff Q:", diff_Q)

    return 0


if __name__ == '__main__':
    
    n_tables = (2, 3, 4)
    n_groups = (2, 3, 4)

    # 1 - Setup environment
    controller = Restaurant()

    #Init kitchen
    kitchen = Kitchen()

    for i in range(len(n_groups)):
        kitchen.ready[i] = 0

    # Init lists with all our table, group and order objects
    tables = []
    groups = []
    orders = []

    for i in range(len(n_tables)):
        table = Table(index=i, size=n_tables[i])
        group = ClientGroup(index=i, size=n_groups[i], batch=0)
        order = Order(group=group)

        group.order = order

        tables.append(table)
        groups.append(group)
        orders.append(order)

    # 2 - Setup agent
    seat = ()
    serve = ()
    bill = ()

    for i in range(len(n_groups)):
        serve += (i, )

        for j in range(len(n_tables)):
            seat += ([i, j], )
            
    bill = serve

    agent = RandomAgent(seat, serve, bill)
    # agent = QLearning(seat, serve, bill)
    # agent = SARSA(seat, serve, bill)

    # 3 - Evaluate agent
    main_game(controller, tables, groups, orders, agent, "random")
