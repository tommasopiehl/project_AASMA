import numpy as np
import random
from operator import itemgetter

#from communicator import Communicator
#from shared import SettingLoader

class Table:

    def __init__(self, k):
        
        self.size = k
        self.index = None
        self.group = None
        self.status = 0 #0 = free, 1 = taken
        self.order = None #array with dish for each client

    def status2str(self):
        
        status_dict = {
            "free":(0),
            "waiting for food":(1),
            "eating":(2),
            "waiting for bill":(3)
        }

        for key, val in status_dict.items():
            if val == self.status:
                return key

    def make_order(self):
        #generates a random order for the client

        for i in range(0, self.size):
            self.order[i] = random.randint(0, 2)

class Order:

    def __init__(self):
        self.dishes = None
        self.table = None
        self.group = None
        self.status = None #0 = not made, 1 = waiting, 2 = cooking, 3 = done

class Client:

    def __init__(self):
        self.client_id = None
        self.group = None
        self.table = None
        self.status = None #0 = wait for seat, 1 = waiting for food, 2 = eating, 3 = waiting for bill
        self.waiting = np.zeros(4) #time spent in each client "state"
        self.mood = 0

    def compute_mood(self, wait_time):
        #heuristic function for mood of client
        
        mood_const_ls = [-0.5, -0.5, 0.5, -0.1]
        mood_const = mood_const_ls[self.status]

        self.mood += mood_const*wait_time

    def status2str(self):
        #translates the status of a table to the string 
        
        status_dict = {
            "waiting for seat":(0),
            "waiting for food":(1),
            "eating":(2),
            "waiting for bill":(3)
        }

        for key, val in status_dict.items():
            if val == self.status:
                return key

class Kitchen:

    def __init__(self, max_tables):
        self.menu = None
        self.plates = None
        self.clean_plates = None
        self.n_cooking = 0
        self.n_waiting = 0
        self.n_ready = np.zeros(max_tables) # dim 2 to be replaced by max amount of tables, [-1, table] if not being prepared, [0, table] if being prepared, [table(size), table] if ready
        self.cooking_info = [] # [dish, time left, table]
        self.ready_info = [] # [dish, table, whole table ready]
        self.waiting_info = [] # [dish, preparation time, table]
        self.serve_info = []

    def init_menu(self):

        # self.menu = {
        #     "meat": [10, 10],
        #     "fish": [10, 15],
        #     "vegetarian" : [5, 10]
        # }

        #self.menu = [[5, 5], [5, 5], [5, 5]]
        self.menu = [[3,3]]

    def count_plates(self):

        return self.plates - self.clean_plates

    def status2str(self, dish_status):
        #translates the status of a table to the string 
        
        status_dict = {
            "ready":(2),
            "being prepared":(1),
            "waiting to be prepared":(0),
        }

        for key, val in status_dict.items():
            if val == dish_status:
                return key

    def format_order(self, table_order, table):

        reform_order = np.zeros([table.size, 3])
        i = 0

        for order in table_order.dishes:
            reform_order[i][0] = int(order)
            reform_order[i][1] = self.menu[int(order)][1]
            reform_order[i][2] = table.index
            i += 1

        return reform_order

    def add_order(self, table_order):
        #takes order from entire table to kitchen, last element = 1 (dish is being prepared), = 0 (dish is waiting to be prepared)

        while self.n_cooking < 4 and len(self.waiting_info) > 0:
            self.cooking_info.append(self.waiting_info.pop(0))
            self.n_waiting -= 1
            self.n_cooking += 1
            
        for order in table_order:   
            if self.n_cooking < 4:   
                self.n_cooking += 1     
                self.cooking_info.append(order)
            else:
                self.n_waiting += 1
                self.waiting_info.append(order)

    def kitchen_timer(self, orders):
        #tracks progress of cooking in kitchen

        self.cooking_info = sorted(self.cooking_info, key=itemgetter(1))

        for i in range(0, len(self.cooking_info)):
            if self.cooking_info[i][1] <= 0:
                self.ready_info.append(self.cooking_info[i])
                self.cooking_info[i][1] = -1
                self.n_ready[int(self.cooking_info[i][2])] += 1
                self.n_cooking -= 1
                #CHECK IF ALL DISHES FOR A TABLE ARE DONE
                if self.n_ready[int(self.cooking_info[i][2])] == int(self.cooking_info[i][2])+2:
                    orders[int(self.cooking_info[i][2])].status = 3
                    

        self.cooking_info[:] = [dish for dish in self.cooking_info if dish[1] != -1]

        while self.n_cooking < 4 and len(self.waiting_info) > 0:
            self.cooking_info.append(self.waiting_info.pop(0))
            self.n_waiting -= 1
            self.n_cooking += 1
            self.clean_plates -= 1

        for i in range(0, len(self.cooking_info)):
            self.cooking_info[i][1] -= 1

    def kitchen_serve(self, table):
        #removes served dishes from kitchen data

        self.ready_info[:] = [dish for dish in self.ready_info if dish[2] != table.index]
        self.n_ready[table.index] = 0

    def dishes(self):
        #cleans dishes

        if (self.plates - self.clean_plates > 2):
            self.clean_plates += 2
        else:
            self.clean_plates = self.plates

class Agent(Kitchen):

    def __init__(self):
        
        self.action = None 
        self.states = None
        self.kitchen = Kitchen(max_tables=3)
        self.action_list = None # [0 = seat at table, 1 = serve, 2 = bring bill, 3 = clean plates], 1 if avaliable, 0 if impossible

    def int2act(self, int_act, groups, tables):

        if int_act == 0:
            self.act_seat(groups[0], tables[0], tables[0].order)
        
        if int_act == 1:
            self.act_seat(groups[0], tables[1], tables[1].order)

        if int_act == 2:
            self.act_seat(groups[0], tables[2], tables[2].order)

        if int_act == 3:
            self.act_seat(groups[1], tables[1], tables[1].order)

        if int_act == 4:
            self.act_seat(groups[1], tables[2], tables[2].order)

        if int_act == 5:
            self.act_seat(groups[2], tables[2], tables[2].order)
        
        if int_act == 6:
            self.act_serve(tables[0])

        if int_act == 7:
            self.act_serve(tables[1])

        if int_act == 8:
            self.act_serve(tables[2])

        if int_act == 9:
            self.act_bill(tables[0])

        if int_act == 10:
            self.act_bill(tables[1])

        if int_act == 11:
            self.act_bill(tables[2])

    def act_seat(self, group, table, order):
        
        order.status = 1
        self.kitchen.add_order(self.kitchen.format_order(order, table))
        
        table.status = 1
        table.group = group

        for client in group:
            client.status = 1
            client.table = table
            client.mood += 5

    def act_serve(self, table):

        for client in table.group:
            client.status = 2
            client.mood += 5

        table.order.status = 3
        self.kitchen.kitchen_serve(table)

    def act_bill(self, table):

        table.status = 0
        table.order.status = 0

        for client in table.group:
            client.status = 4
            client.mood += 5

        table.group = None

    def allowed_seat(self, group_states, table_states):       

        allowed = []
        tables = [2, 3, 4] #predefined sizes of tables
        
        for i, table_state in enumerate(table_states):
            for j, group_state in enumerate(group_states):
                if table_state == 0 and j+2 <= tables[i]:
                    if group_state == 0:
                        allowed.append([j, i]) #array where the groups that can be seated to the corresponding table are included

        return allowed

    #FIXA DENNAAAAAA!!!!!!
    def allowed_serve(self, table_states, ready):

        allowed = []

        for i, table_state in enumerate(table_states):
            if table_state == 1:
                    if ready[i] == 3:
                        allowed.append(i) #array where the tables to which we can bring food are included

        return allowed

    def allowed_bill(self, table_states):

        allowed = []
        
        for i, state in enumerate(table_states):
            if state == 3:
                    allowed.append(i)

        return allowed #array where the tables to which we can bring the bill are included

class AgentControllerRL(Agent, Kitchen, Table, Client):

        def __init__(self):
        
            self.alpha = 0
            self.gamma = 0
            self.eps_init = None
            self.eps_final = None
            self.episode_max = None
            self.current_env = None
            self.q_table = None

        def env2array(self, agent, groups, tables, orders):
            
            self.current_env = []
            self.current_env.append(agent.action)
            for order in orders:
                self.current_env.append(order.status)
            for group in groups:
                self.current_env.append(group[0].status)
            for table in tables:
                self.current_env.append(table.status)

            return self.current_env

        def compute_rows(self):

            state_rows = []
            state_count = 0

            #NOTE: WE JUST TRACK ORDERS OF TABLES/GROUPS INSTEAD OF INDIVIDUAL DISHES

            for state_agent in range(0, 12):
                for order_1 in range(0, 4):
                    for order_2 in range(0, 4):
                        for order_3 in range(0, 4):
                            for state_group_1 in range(0, 4):
                                for state_group_2 in range(0, 4):
                                    for state_group_3 in range(0, 4):
                                        for state_table_1 in range(0, 2):
                                            for state_table_2 in range(0, 2):
                                                for state_table_3 in range(0, 2):
                                                    state_rows.append([state_agent, order_1, order_2, order_3, state_group_1, state_group_2, 
                                                    state_group_3, state_table_1, state_table_2, state_table_3])  
                                                    state_count += 1

            #IMPORTANT: agent action = [0:seat(0, 0), 1:seat(0, 1), 2:seat(0, 2), 3:seat(1, 1), 4:seat(1, 2), 5:seat(2, 2), 6:serve(0), 7:serve(1), 8:serve(2), 9:bill(0), 10:bill(1), 11:bill(2)]

            return state_rows, state_count

        def allowed_action_list(self, groups, tables, orders):

            allowed = []

            allowed.append(self.allowed_seat(group_states=groups, table_states=tables))
            allowed.append(self.allowed_serve(table_states=tables, ready=orders))
            allowed.append(self.allowed_bill(table_states=tables))

            return allowed

        def q_learning(self, q_rows, rows_count, kitchen):
            
            #q_rows, rows_count = self.compute_rows() #q_rows = [action of agent, dishes in wait, dishes being cooked, dishes ready, state of group 1-3, state of table 1-3]

            q_cols = 12 # each action and variation of action
            # discount = self.gamma
            # lr = self.alpha

            #Define the q-table
            self.q_table = np.random.uniform(low=0.0, high=1.0, size=(rows_count, q_cols))

            #IMPORTANT: agent action = [0:seat(0, 0), 1:seat(0, 1), 2:seat(0, 2), 3:seat(1, 1), 4:seat(1, 2), 5:seat(2, 2), 6:serve(0), 7:serve(1), 8:serve(2), 9:bill(0), 10:bill(1), 11:bill(2)]

            all_actions = [[[0,0],[0,1],[0,2],[1,1],[1,2],[2,2]],[0,1,2],[0,1,2]]

            for indx, row in enumerate(q_rows):
                kitchen_states = row[1:4]
                group_states = row[4:7]
                table_states = row[7:10]
                # allowed = [[groups, tables (seat)], [tables (serve)], [tables (bill)]]]
                allowed = self.allowed_action_list(group_states, table_states, kitchen_states)

                for i in range(0, 6):
                    if all_actions[0][i] not in allowed[0]:
                        self.q_table[indx][i] = np.nan
                for j in range(0, 3):
                    if all_actions[1][j] not in allowed[1]:
                        self.q_table[indx][j+6] = np.nan
                for k in range(0, 3):
                    if all_actions[2][k] not in allowed[2]:
                        self.q_table[indx][k+9] = np.nan

            return self.q_table

        def epsilon_greedy(self, all_actions, state_indx, current_total_steps = 0, epsilon_initial = 1, epsilon_final = 0.2, anneal_timesteps = 10000, eps_type= "constant"):
            
            if eps_type == 'constant':
                epsilon = epsilon_final
                p = np.random.uniform(0, 1)
                if p >= epsilon:
                    action = np.nanargmax(self.q_table[state_indx])
                    print("best move", action)
                else:
                    action = np.random.choice(all_actions)
                    print("random move", action)
            return action

            

            


            
            
            
                











