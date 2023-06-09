import numpy as np
import random
from operator import itemgetter

from agent import Agent

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
        self.batch = None # To track the total waiting time for each "group of groups" that enters the restaurant


    def status2str(self):
        # Translates the status of a table to the string 
        
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

        self.menu = [3, 5] #Cooking time for each of the two dishes

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


class AgentControllerRL(Agent, Kitchen, Table, ClientGroup):

    def __init__(self):

        self.eps_init = None
        self.eps_final = None
        self.n_episodes = None
        self.current_env = None
        self.agent = None
        

    def env2array(self, groups, tables, orders):

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
    