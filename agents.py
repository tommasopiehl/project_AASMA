import numpy as np

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

        self.menu = [[3,3]]

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
                self.cooking.append([3, table_order.group.index])
            else:
                self.waiting_cnt += 1
                self.waiting.append([3, table_order.group.index])

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

    # VLAUES TO ADJUST FOR Q-LEARNING

    def reward_seat(self, seat_group, table, all_groups, allowed):

        R = 0
        R -= np.abs(table.size - seat_group.size) * 5

        for group in all_groups:
            if group.state != 4:
                if group.stop_waiting[group.state][group.index] in allowed:
                    R += seat_group.waiting[0] - group.waiting[group.state]

        R += seat_group.waiting[0]
        self.R_total += R

        return R
    
    def reward_serve(self, serve_group, all_groups, allowed):
        
        R = 0

        for group in all_groups:
            if group.state != 4:
                if group.stop_waiting[group.state][group.index] in allowed:
                    R += serve_group.waiting[1] - group.waiting[group.state]

        R += group.waiting[group.state]
        self.R_total += R

        return R

    def reward_bill(self, bill_group, all_groups, allowed):
        
        R = 0

        for group in all_groups:
            if group.state != 4:
                if group.stop_waiting[group.state][group.index] in allowed:
                    R += bill_group.waiting[3] - group.waiting[group.state]

        R += bill_group.waiting[3]
        self.R_total += R

        return R

    def reward_wait(self, allowed_actions):

        R = 0

        R -= (len(allowed_actions)-1)*30
        self.R_total += R

        return R

    #------------------------------

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

