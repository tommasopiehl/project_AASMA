from waiter import Agent, Table, Client, Kitchen
import numpy as np
import random

#ciao ciao

class Settings:

    def __init__(self):
        self.max_clients = None
        self.max_plates = None

def main_game(n_tables = (2, 3), n_groups = (2, 3)):

    game_over = 0
    agent = Agent()

    tables = []
    groups = []
    clients = []
    
    kitchen = Kitchen(max_clients=np.sum(n_tables))
    kitchen.init_menu()
    kitchen.n_cooking = 0
    kitchen.n_ready = 0
    kitchen.plates = 10
    kitchen.clean_plates = kitchen.plates

    for i in range(len(n_tables)):

        table = Table(k = n_tables[i])
        table.status = 0
        table.index = i
        tables.append(table)
        groups.append([])

        for m in range(n_groups[i]):
            client = Client()
            client.group = i
            client.status = 0
            clients.append(client)
            groups[i].append(client)

    time = 0

    while game_over != 1:

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
            kitchen.kitchen_timer()
            print("kitchen, n_cooking:", kitchen.n_cooking, ", n_ready:", kitchen.n_ready, ", clean plates:", kitchen.clean_plates)
            print("cooking:")
            for plate in kitchen.cooking_info:
                print("dish:", plate[0], ", time:", plate[1], ", table: ", plate[2])
            print("waiting:")
            for plate in kitchen.waiting_info:
                print("dish:", plate[0], ", time:", plate[1], ", table: ", plate[2])
            print("ready:")
            for plate in kitchen.ready_info:
                print("dish:", plate[0], ", table:", plate[2])

        #manual actions, to be replace with action found by algorithm
        int_act = int(input("Enter move: "))

        if int_act == 0:
            #seat group: "seat_g" at table "seat_t" and take their orders

            seat_g = int(input("group to seat: "))
            seat_t = int(input("at table: "))
            order = []
            for i in range(0, tables[seat_t].size):
                order.append(random.randint(0, 2))
            agent.act_seat(groups[seat_g], tables[seat_t])
            kitchen.add_order(kitchen.format_order(order, tables[seat_t]))

        if int_act == 1:
            serve_t = int(input("serve table: "))
            agent.act_serve(tables[serve_t])
            kitchen.kitchen_serve(tables[serve_t])

        if int_act == 2:
            bill_t = int(input("bill for table: "))
            agent.act_bill(tables[bill_t])

        if int_act == 3:
            kitchen.clean_plates()

        if int_act == 4:
            game_over = 1

        time += 1

        print("-----------")
    
    print("done")

    return 0

main_game(n_tables = (2, 3), n_groups = (2, 3))