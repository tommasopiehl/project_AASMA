import numpy as np
import random
from operator import itemgetter

# CLASS FOR TABLES

class Table:

    def __init__(self, k):
        
        self.size = k # int
        self.index = None # int 
        self.group = None # Group object
        self.state = 0 #0 = free, 1 = taken

    def status2str(self):
        
        status_dict = {
            "free":(0),
            "taken":(1),
        }

        for key, val in status_dict.items():
            if val == self.state:
                return key

# CLASS FOR GROUP-ORDER 

class Order:

    def __init__(self):

        self.group = None
        self.size = None
        self.state = None #0 = not made, 1 = waiting, 2 = cooking, 3 = done, 4 = served
        self.dishes = None #NOT USED RIGHT NOW, array with index of each dish and preparation time

    def reset_order(self):

        self.state = 0

# CLIENT-GROUP CLASS. CLIENTS ARE TREATED AS GROUPS

class ClientGroup:

    def __init__(self):

        self.table = None
        self.size = None
        self.index = None
        self.state = None # [0 = wait for seat, 1 = waiting for food, 2 = eating, 3 = waiting for bill]
        self.order = None # Order-class object
        self.waiting = np.zeros(4) # Time spent in each group "state"
        #NOTE: 2000 IS USED TO AVOID USING NONE
        self.stop_waiting = [[[1,2,3],[4,5],[6]],[7,8,9],[2000, 2000, 2000],[10,11,12]] #The actions from the agent for which the group are waiting, list[group_state][group_index]
        self.mood = 0 # Current mood of group
        self.batch = None # To track the total waiting time/mood for each "group of groups" that enters the restaurant
        

    def compute_mood(self, wait_time):

        # Heuristic function for mood of client
        
        mood_const_ls = [-0.5, -0.5, 0.5, -0.1]
        mood_const = mood_const_ls[self.state]

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
            if val == self.state:
                return key

    def reset_group(self):
        
        self.table = None
        self.state = 0
        self.waiting = np.zeros(4)
        self.mood = 0
        self.order.reset_order()

#CLASS FOR THE KITCHEN

class Kitchen:

    def __init__(self):
        
        self.menu = None
        self.cooking_cnt = None
        self.ready_cnt = None
        self.waiting_cnt = None
        self.cooking = [] # [time left, group]
        self.ready = {} # {"group": amount ready}
        self.waiting = [] # [preparation time, group]

    def init_menu(self):

        self.menu = [3, 3] #Cooking time for each of the two dishes

    def status2str(self, dish_status):

        # Translates the status of an order to a string 
        
        status_dict = {
            "ready":(2),
            "being prepared":(1),
            "waiting to be prepared":(0),
        }

        for key, val in status_dict.items():
            if val == dish_status:
                return key

    def add_order(self, table_order):
        # Takes order from entire table to kitchen

        while self.cooking_cnt < 4 and self.waiting_cnt > 0:
            self.cooking.append(self.waiting.pop(0))
            self.waiting_cnt -= 1
            self.cooking_cnt += 1
            
        for order in table_order.dishes:   
            if self.cooking_cnt < 4:   
                self.cooking_cnt += 1     
                self.cooking.append([self.menu[order], table_order.group.index])
                table_order.state = 2
            else:
                self.waiting_cnt += 1
                self.waiting.append([self.menu[order], table_order.group.index])

    def kitchen_step(self, orders):
        # Tracks progress of cooking in kitchen

        for i in range(0, self.cooking_cnt):
            if self.cooking[i][0] <= 0 and self.cooking[i][0] != -1:
                self.ready[self.cooking[i][1]] += 1
                self.cooking[i][0] = -1
                self.cooking_cnt -= 1
                self.ready_cnt += 1
        
        for i, order in enumerate(orders):
            if self.ready[order.group.index] == order.size:
                order.state = 3
                    
        self.cooking[:] = [dish for dish in self.cooking if dish[0] != -1]

        while self.cooking_cnt < 4 and self.waiting_cnt > 0:
            self.cooking.append(self.waiting.pop(0))
            self.waiting_cnt -= 1
            self.cooking_cnt += 1

        for i in range(0, len(self.cooking)):
            self.cooking[i][0] -= 1

    def kitchen_serve(self, group):
        #removes served dishes from kitchen data

        self.ready[group.index] = 0
        self.ready_cnt -= group.size

class Agent(Kitchen):

    def __init__(self):
        
        self.action = None # 0 < Current action < 13
        self.state = None # [0 = free, 1 = busy]
        self.action_dict = None # {"free" = [], "seat" = [groups, tables], "serve" = [groups], "bill" = [groups]}
        self.kitchen = None  
        self.R_total = None #Total reward achieved
        self.R_seat = 0
        self.R_serve = 0
        self.R_bill = 0
        self.R_wait = 0

    def init_actions(self):

        self.action_dict = {
            "free":(),
            "seat":([0,0], [0,1], [0,2], [1,1], [1,2], [2,2]),
            "serve":(0, 1, 2),
            "bill":(0, 1, 2)
        }

    def act2int(self, act, params):

        if act == "free":
            int_act = 0

        if act == "seat":
            int_act = self.action_dict["seat"].index(params) + 1
        
        if act == "serve":
            int_act = self.action_dict["serve"].index(params) + 7

        if act == "bill":
            int_act = self.action_dict["bill"].index(params) + 10

        return int_act

    def act2str(self, act):

        if act == 0:
            return "Wait"

        if act > 0 and act <= 6:
            g = self.action_dict["seat"][act-1][0]
            t = self.action_dict["seat"][act-1][1]
            return "seat group "+str(g)+" at table "+str(t)

        if act > 6 and act <= 9:
            g = self.action_dict["serve"][act-7]
            return "serve group "+str(g)

        if act > 9 and act <= 12:
            g = self.action_dict["bill"][act-10]
            return "bill to group "+str(g)


    def int2act(self, int_act):

        act = []

        if int_act > 0 and int_act <= 6:
            params = self.action_dict["seat"][int_act-1]
            act.append(1)
            act.append(params)
            return act
        
        if int_act > 6 and int_act <= 9:
            params = self.action_dict["serve"].index(int_act - 7)
            act.append(2)
            act.append(params)
            return act

        if int_act > 9 and int_act <= 12:
            params = self.action_dict["bill"].index(int_act - 10)
            act.append(3)
            act.append(params)
            return act

        act.append(0)

        return act
    
    def act_seat(self, group, table, kitchen):
        
        group.order.state = 1
        kitchen.add_order(group.order)
        table.state = 1
        table.group = group
        group.table = table
        group.state = 1
        group.mood += 5

    def act_serve(self, group, kitchen):

        group.state = 2
        group.mood += 5
        group.order.state = 4
        kitchen.kitchen_serve(group)

    def act_bill(self, group, table):

        table.group = None
        table.state = 0
        group.state = 4
        group.table = None
        group.mood += 5

    def allowed_seat(self, groups, tables):       
        #groups and tables are arrays of states not objects

        allowed = []
        table_sizes = [2, 3, 4]
        group_sizes = [2, 3, 4]
        
        for i, table_state in enumerate(tables):
            for j, group_state in enumerate(groups):
                if table_state == 0 and group_sizes[j] <= table_sizes[i]:
                    if group_state == 0:
                        allowed.append(self.act2int("seat", [j, i])) # j & i are indexes of group and table

        return allowed

    def allowed_serve(self, groups, orders):

        allowed = []

        for i, group_state in enumerate(groups):
            if group_state == 1:
                if orders[i] == 3:
                    allowed.append(self.act2int("serve", i))

        return allowed

    def allowed_bill(self, groups):

        allowed = []
        
        for i, group_state in enumerate(groups):
            if group_state == 3:
                allowed.append(self.act2int("bill", i))

        return allowed

    def reward_seat(self, seat_group, table, all_groups, all_tables, allowed):

        R = 0

        #FIXED THIS LAST NIGHT, BEFORE IT JUST CHECKED IF THE SIZE WAS DIFFERENT
        # for other_table in all_tables:
        #     if other_table.index != table.index and other_table.state == 0:
        #         if table.size == seat_group.size:
        #             R -= 15

        R -= np.abs(table.size - seat_group.size)*5

        
        for group in all_groups:
            if group.state != 4:
                if group.stop_waiting[group.state][group.index] in allowed:
                    R += seat_group.waiting[0] - group.waiting[group.state]

        R += 10/(seat_group.waiting[0]+1)
        self.R_total += R

        return R
    
    def reward_serve(self, serve_group, all_groups, allowed):
        
        R = 0

        for group in all_groups:
            if group.state != 4:
                if group.stop_waiting[group.state][group.index] in allowed:
                    R += serve_group.waiting[1] - group.waiting[group.state]

        R += 10/(serve_group.waiting[serve_group.state]+1)
        self.R_total += R

        return R

    def reward_bill(self, bill_group, all_groups, allowed):
        
        R = 0

        for group in all_groups:
            if group.state != 4:
                if group.stop_waiting[group.state][group.index] in allowed:
                    R += bill_group.waiting[3] - group.waiting[group.state]

        R += 10/(bill_group.waiting[3]+1)
        self.R_total += R

        return R

    def reward_wait(self, allowed_actions):

        R = 0

        R -= (len(allowed_actions)-1)*10
        self.R_total += R

        return R

class AgentControllerRL(Agent, Kitchen, Table, ClientGroup):

    def __init__(self):
        
        # VLAUES TO ADJUST FOR Q-LEARNING
        self.alpha = None
        self.gamma = None
        #------------------------------

        self.eps_init = None
        self.eps_final = None
        self.n_episodes = None
        self.current_env = None
        self.agent = None
        self.Q = None #Not sure if its good to have the table as class attribute
        self.diff = None #Difference between tables, used as threshold for convergence
        self.n_random = 0 #Only to check
        self.n_best = 0 #Only to check
        self.eps=[]

    def env2array(self, agent, groups, tables, orders):
            
        self.current_env = []
        for order in orders:
            self.current_env.append(order.state)
        for group in groups:
            self.current_env.append(group.state)
        for table in tables:
            self.current_env.append(table.state)

        return self.current_env

    def compute_rows(self):

        state_rows = []
        state_count = 0

        #NOTE: WE JUST TRACK ORDERS OF TABLES/GROUPS INSTEAD OF INDIVIDUAL DISHES

        #for state_agent in range(0, 13): # 0 = free, rest is taken from action_dict
        for order_1 in range(0, 5): # States of each order
            for order_2 in range(0, 5):
                for order_3 in range(0, 5): # -----
                    for state_group_1 in range(0, 5): # States of each group
                        for state_group_2 in range(0, 5):
                            for state_group_3 in range(0, 5): # ------
                                for state_table_1 in range(0, 2): # States of each table
                                    for state_table_2 in range(0, 2):
                                        for state_table_3 in range(0, 2): # ------
                                            state_rows.append([order_1, order_2, order_3, state_group_1, state_group_2, 
                                            state_group_3, state_table_1, state_table_2, state_table_3])  
                                            state_count += 1

        return state_rows, state_count

    def allowed_action_list(self, groups, tables, orders):

        allowed = []

        allowed.append(0)
        for action in self.agent.allowed_seat(groups=groups, tables=tables):
            allowed.append(action)
        
        for action in self.agent.allowed_serve(groups=groups, orders=orders):
            allowed.append(action)
        
        for action in self.agent.allowed_bill(groups=groups):
            allowed.append(action)

        return allowed

    def q_init(self, q_rows, rows_count):

        q_cols = 13 # each action and variation of action

        #Define the q-table
        self.Q = np.random.uniform(low=0.0, high=1.0, size=(rows_count, q_cols))

        all_actions = list(range(0, q_cols)) #Define list with values 0-13

        for indx, row in enumerate(q_rows):
            order_states = row[0:3] #The elements in the env array that represent order states
            group_states = row[3:6] #The elements in the env array that represent group states
            table_states = row[6:9] #The elements in the env array that represent table states
            allowed = self.allowed_action_list(group_states, table_states, order_states)
            
            nan_cnt = 0
            for i in range(0, 13): #Wait is always allowed
                if all_actions[i] not in allowed:
                    nan_cnt += 1
                    self.Q[indx][i] = np.nan
                if nan_cnt == 13:
                    print(allowed)
                    print(row)

    def q_update(self, Q_old, q_rows, current_state, next_state, R, act):
        
        current_indx = q_rows.index(current_state) #Current state
        next_indx = q_rows.index(next_state) #Next state

        #Bellmans update equation
        self.Q[current_indx][act] = self.Q[current_indx][act] + self.alpha * ((R + self.gamma * np.nanmax(self.Q[next_indx])) - self.Q[current_indx][act])

        #Kepp track of how much we change the Q-table
        self.diff += np.abs(np.nanmean(self.Q) - np.nanmean(Q_old))

    def epsilon_greedy(self, Q, all_actions, state_indx, current_total_steps = 0, epsilon_initial = 0.1, epsilon_final = 0.1, anneal_timesteps = 2500, eps_type= "constant"):
        
        if eps_type == 'constant':
            epsilon = epsilon_final
            p = np.random.uniform(0, 1)
            if p >= epsilon:
                action = np.nanargmax(Q[state_indx])
                print("best move", action)
            else:
                action = np.random.choice(all_actions)
                print("random move", action)

        elif eps_type == 'linear':
            p = np.random.uniform(0, 1)
            val = LinearEpsilon(anneal_timesteps, epsilon_final, epsilon_initial).value(current_total_steps)
            self.eps.append(val)
            if val <= p:
                action = np.nanargmax(Q[state_indx])
                self.n_best += 1
            else:
                action = np.random.choice(all_actions)
                self.n_random += 1
        return action

#for linear epsilon

class LinearEpsilon(object):
    def __init__(self, schedule_timesteps, final_p, initial_p=1.0):
        self.schedule_timesteps = schedule_timesteps
        self.final_p = final_p
        self.initial_p = initial_p

    def value(self, t):
        # Return the annealed linear value
        delta_e = self.final_p - self.initial_p
        e_t = self.initial_p + delta_e * (t/self.schedule_timesteps)
        return e_t

