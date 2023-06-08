import numpy as np


class Agent():

    def __init__(self, seat, serve, bill):
        self.state = 0 # 0 < Current action < 13
        self.action_dict = {
            "free":(),
            "seat":seat,
            "serve":serve,
            "bill":bill
        } # {"free" = [], "seat" = [groups, tables], "serve" = [groups], "bill" = [groups]}
        
        self.Q = None 
        self.totalReward = 0 #Total reward achieved

    
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

        if table.state == 0 and group.state == 0:
            table.state = 1
            table.group = group
            group.state = 1
            group.table = table
            kitchen.add_order(group.order)
            group.order.state = 1
            group.mood += 5

    def act_serve(self, group, kitchen):

        if group.state == 1 and group.order.state == 3:
            group.state = 2
            group.mood += 5
            group.order.state = 4
            kitchen.kitchen_serve(group)

    def act_bill(self, group, table):

        if group.state == 3:
            group.state = 4
            group.mood += 5
            group.table = None
            table.group = None
            table.state = 0

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

    def allowed_action_list(self, groups, tables, orders):

        allowed = []

        allowed.append(0)
        for action in self.allowed_seat(groups=groups, tables=tables):
            allowed.append(action)
        
        for action in self.allowed_serve(groups=groups, orders=orders):
            allowed.append(action)
        
        for action in self.allowed_bill(groups=groups):
            allowed.append(action)

        return allowed

    # VLAUES TO ADJUST FOR Q-LEARNING

    def reward_seat(self, seat_group, table, all_groups, allowed):

        R = 0
        R -= np.abs(table.size - seat_group.size) * 5

        for group in all_groups:
            if group.state != 4:
                if group.stop_waiting[group.state][group.index] in allowed:
                    R += seat_group.waiting[0] - group.waiting[group.state]

        R += seat_group.waiting[0]
        self.totalReward += R

        return R
    
    def reward_serve(self, serve_group, all_groups, allowed):
        
        R = 0

        for group in all_groups:
            if group.state != 4:
                if group.stop_waiting[group.state][group.index] in allowed:
                    R += serve_group.waiting[1] - group.waiting[group.state]

        R += group.waiting[group.state]
        self.totalReward += R

        return R

    def reward_bill(self, bill_group, all_groups, allowed):
        
        R = 0

        for group in all_groups:
            if group.state != 4:
                if group.stop_waiting[group.state][group.index] in allowed:
                    R += bill_group.waiting[3] - group.waiting[group.state]

        R += bill_group.waiting[3]
        self.totalReward += R

        return R

    def reward_wait(self, allowed_actions):

        R = 0

        R -= (len(allowed_actions)-1)*30
        self.totalReward += R

        return R

    #------------------------------

class RandomAgent(Agent):

    def __init__(self, seat, serve, bill):
        super(RandomAgent, self).__init__(seat, serve, bill)

    def action(self, allowed_reformat) -> int:
        return np.random.choice(allowed_reformat)

class QLearning(Agent):

    def __init__(self, seat, serve, bill):
        super(QLearning, self).__init__(seat, serve, bill)

class SARSA(Agent):

    def __init__(self, seat, serve, bill):
        super(SARSA, self).__init__(seat, serve, bill)


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

