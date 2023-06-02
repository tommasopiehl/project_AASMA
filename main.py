from waiter import Agent, Table, Client, Kitchen, AgentControllerRL, Order
import numpy as np
import random

#ciao ciao

def main_game(n_tables = (2, 3), n_groups = (2, 3)):

    game_over = 0
    agent = Agent()
    agent.action = 0
    agent_wait = False
    controlller = AgentControllerRL()

    tables = []
    groups = []
    clients = []
    orders = []
    
    kitchen = agent.kitchen
    kitchen.init_menu()
    kitchen.n_waiting = 0
    kitchen.n_cooking = 0
    kitchen.plates = 10
    kitchen.clean_plates = kitchen.plates

    q_rows, rows_count = controlller.compute_rows()
    q_table = controlller.q_learning(q_rows=q_rows, rows_count=rows_count, kitchen=kitchen)

    for i in range(len(n_tables)):

        table = Table(k = n_tables[i])
        table.status = 0
        table.index = i

        order = Order()
        order.status = 0
        table.order = order
        order.table = table

        tables.append(table)
        groups.append([])
        
        for m in range(n_groups[i]):

            client = Client()
            client.group = i
            client.status = 0
            clients.append(client)
            groups[i].append(client)

        order.group = groups[i]
        order.dishes = np.zeros(len(groups[i]))
        orders.append(order)

    time = 0

    while game_over != 1:

        go = int(input("press 1 to continue: "))

        if go == 1:
            terminal = 1

            for client in clients:
                client.compute_mood(client.waiting[client.status])

            print("-----------")
            print("time: ", time)
            print("tables:")
            for n in range(len(n_tables)):
                print("table size:", tables[n].size, ", table status:", tables[n].status2str(), ", table index:", tables[n].index)

            print("clients")
            for client in clients:
                client.waiting[client.status] += 1
                if client.status == 2:
                    if client.waiting[client.status] == 10:
                        client.status = 3
                print("status:", client.status2str(), ", mood:", client.mood, ", group: ", client.group)

            if time > 0:
                kitchen.kitchen_timer(orders=orders)
                print("kitchen, n_cooking:", kitchen.n_cooking, ", n_ready:", np.sum(kitchen.n_ready))
                print("cooking:")
                for plate in kitchen.cooking_info:
                    print("dish:", plate[0], ", time:", plate[1], ", table: ", plate[2])
                print("waiting:")
                for plate in kitchen.waiting_info:
                    print("dish:", plate[0], ", time:", plate[1], ", table: ", plate[2])
                print("ready:")
                for i, count in enumerate(kitchen.n_ready):
                    print("table:", i, ", count:", count)

                print("Orders:")
                for order in orders:
                    print("table: ", order.table.index, ", group: ", groups.index(order.group), ", state: ", order.status)


            for group in groups:
                if group[0].status != 4:
                    terminal = 0

            current = controlller.env2array(agent, groups=groups, tables=tables, orders=orders)
            current_row = q_table[q_rows.index(current)]
            check_nan = np.isnan(current_row)

            if False not in check_nan:
                if terminal == 1:
                    game_over = 1
                else:
                    agent_wait = True

            #manual actions, to be replace with action found by algorithm
            if agent_wait == False:
                allowed_reformat = []
                for i in range(len(current_row)):
                    if(np.isnan(current_row[i]) == False):
                        allowed_reformat.append(i)
                print("allowed moves:", allowed_reformat)
                int_act = controlller.epsilon_greedy(allowed_reformat, q_rows.index(current))
                agent.int2act(int_act, groups=groups, tables=tables)

            # if int_act == 0:
            #     #seat group: "seat_g" at table "seat_t" and take their orders

            #     seat_g = int(input("group to seat: "))
            #     seat_t = int(input("at table: "))
            #     order = []
            #     for i in range(0, tables[seat_t].size):
            #         # For different dishes in menu
            #         #order.append(random.randint(0, 2)) 

            #         # For only one dish
            #         order.append(0)
            #     agent.act_seat(groups[seat_g], tables[seat_t])
            #     kitchen.add_order(kitchen.format_order(order, tables[seat_t]))

            # if int_act == 1:
            #     serve_t = int(input("serve table: "))
            #     agent.act_serve(tables[serve_t])
            #     kitchen.kitchen_serve(tables[serve_t])

            # if int_act == 2:
            #     bill_t = int(input("bill for table: "))
            #     agent.act_bill(tables[bill_t])

            # if int_act == 3:
            #     kitchen.clean_plates()

            # if int_act == 4:
            #     game_over = 1

            time += 1

        print("-----------")
    
    print("done")

    return 0

main_game(n_tables = (2, 3, 4), n_groups = (2, 3, 4))