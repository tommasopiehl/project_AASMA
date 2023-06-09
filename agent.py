import numpy as np


class Agent():

    def __init__(self):
                
        # VALUES TO ADJUST FOR Q-LEARNING
        self.alpha = None
        self.gamma = None
        #------------------------------

        self.action = None # 0 < Current action < 13
        self.state = None # [0 = free, 1 = busy]
        self.action_dict = None # {"free" = [], "seat" = [groups, tables], "serve" = [groups], "bill" = [groups]}
        self.kitchen = None  
        self.Q = None
        self.R_total = None #Total reward achieved
        self.R_seat = 0
        self.R_serve = 0
        self.R_bill = 0
        self.R_wait = 0
        self.n_random = 0 #Only to check
        self.n_best = 0 #Only to check
        self.eps=[]

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

    def act_serve(self, group, kitchen):

        group.state = 2
        group.order.state = 4
        kitchen.kitchen_serve(group)

    def act_bill(self, group, table):

        table.group = None
        table.state = 0
        group.state = 4
        group.table = None

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

        R -= np.abs(table.size - seat_group.size) * 5

        
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

        R -= (len(allowed_actions)-1)*30
        self.R_total += R

        return R
    
    def q_init(self,controller, q_rows, rows_count):

        q_cols = 13 # each action and variation of action

        #Define the q-table
        self.Q = np.random.uniform(low=0.0, high=1.0, size=(rows_count, q_cols))

        all_actions = list(range(0, q_cols)) #Define list with values 0-13

        for indx, row in enumerate(q_rows):
            order_states = row[0:3] #The elements in the env array that represent order states
            group_states = row[3:6] #The elements in the env array that represent group states
            table_states = row[6:9] #The elements in the env array that represent table states
            allowed = controller.allowed_action_list(group_states, table_states, order_states)
            
            nan_cnt = 0
            for i in range(0, 13): #Wait is always allowed
                if all_actions[i] not in allowed:
                    nan_cnt += 1
                    self.Q[indx][i] = np.nan
                if nan_cnt == 13:
                    print(allowed)
                    print(row)

    def q_update(self, q_rows, current_state, next_state, R, act):
        
        current_indx = q_rows.index(current_state) #Current state
        next_indx = q_rows.index(next_state) #Next state

        #Bellmans update equation
        self.Q[current_indx][act] = self.Q[current_indx][act] + self.alpha * ((R + self.gamma * np.nanmax(self.Q[next_indx])) - self.Q[current_indx][act])

    def sarsaUpdate(self, qRows, currentState, nextState, R, act, nextAction):
        current_indx = qRows.index(currentState)
        next_indx = qRows.index(nextState)

        self.Q[current_indx][act] = self.Q[current_indx][act] + self.alpha * ((R + self.gamma * self.Q[next_indx][nextAction]) - self.Q[current_indx][act])

    def epsilon_greedy(self, Q, all_actions, state_indx, current_total_steps = 0, epsilon_initial = 0.4, epsilon_final = 0.1, anneal_timesteps = 2500, eps_type= "constant"):
        
        if eps_type == 'constant':
            epsilon = epsilon_final
            p = np.random.uniform(0, 1)
            if p >= epsilon:
                action = np.nanargmax(Q[state_indx])
            else:
                action = np.random.choice(all_actions)

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

        elif eps_type == 'sarsa':
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

