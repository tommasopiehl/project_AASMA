import numpy as np
import random
from operator import itemgetter
from agents import Kitchen, Agent

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
        self.stop_waiting = [[[1,2,3],[4,5],[6]],[7,8,9],[2000, 2000, 2000],[10,11,12]] # The actions from the agent for which the group are waiting, list[group_state][group_index]
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


class Restaurant(Order, Kitchen, Table, ClientGroup):

    def __init__(self):
        
        # VLAUES TO ADJUST FOR Q-LEARNING
        self.alpha = 0.8
        self.gamma = 0.3
        #------------------------------

        self.eps_init = None
        self.eps_final = None
        self.episode_max = None
        self.current_env = None
        self.Q = None #Not sure if its good to have the table as class attribute
        self.diff = 0 #Difference between tables, used as threshold for convergence

    def env2array(self, agent, groups, tables, orders):
            
        self.current_env = []
        self.current_env.append(agent.action)
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

        for state_agent in range(0, 13): # 0 = free, rest is taken from action_dict
            for order_1 in range(0, 5): # States of each order
                for order_2 in range(0, 5):
                    for order_3 in range(0, 5): # -----
                        for state_group_1 in range(0, 5): # States of each group
                            for state_group_2 in range(0, 5):
                                for state_group_3 in range(0, 5): # ------
                                    for state_table_1 in range(0, 2): # States of each table
                                        for state_table_2 in range(0, 2):
                                            for state_table_3 in range(0, 2): # ------
                                                state_rows.append([state_agent, order_1, order_2, order_3, state_group_1, state_group_2, 
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

        all_actions = list(range(0, 14))

        for indx, row in enumerate(q_rows):
            order_states = row[1:4]
            group_states = row[4:7]
            table_states = row[7:10]
            allowed = self.allowed_action_list(group_states, table_states, order_states)

            for i in range(0, 13):
                if all_actions[i] not in allowed:
                    self.Q[indx][i] = np.nan

    def q_update(self, Q_old, q_rows, current_state, next_state, R, act):
        current_indx = q_rows.index(current_state)
        next_indx = q_rows.index(next_state)

        self.Q[current_indx][act] = self.Q[current_indx][act] + self.alpha * ((R + self.gamma * np.nanmax(self.Q[next_indx])) - self.Q[current_indx][act])

        self.diff += np.abs(np.nanmean(self.Q) - np.nanmean(Q_old))

    def sarsaUpdate(self, oldQ, qRows, currentState, nextState, R, act, nextAction):
        current_indx = qRows.index(currentState)
        next_indx = qRows.index(nextState)

        self.Q[current_indx][act] = self.Q[current_indx][act] + self.alpha * ((R + self.gamma * self.Q[next_indx][nextAction]) - self.Q[current_indx][act])

        self.diff += np.abs(np.nanmean(self.Q) - np.nanmean(oldQ))


    def epsilon_greedy(self, Q, all_actions, state_indx, current_total_steps = 0, epsilon_initial = 1, epsilon_final = 0.2, anneal_timesteps = 10000, eps_type= "constant"):
        
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
            if LinearEpsilon(anneal_timesteps, epsilon_final, epsilon_initial).value(current_total_steps) >= p:
                action = np.nanargmax(Q[state_indx])
            else:
                action = np.random.choice(all_actions)

        elif eps_type == 'sarsa':
            epsilon = epsilon_final
            p = np.random.uniform(0, 1)
            if p >= epsilon:
                action = np.nanargmax(Q[state_indx])
                print("best move", action)
            else:
                action = np.random.choice(all_actions)
                print("random move", action)

        return action

