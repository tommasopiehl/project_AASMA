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
        self.status = 0 #0 = free, 1 = waiting for food, 2 = eating, 3 = waiting for bill
        self.order = -1*np.ones(self.size) #array with dish for each client

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

class Client:

    def __init__(self):
        self.client_id = None
        self.group = None
        self.table = None
        self.status = None #0 = wait for seat, 1 = waiting for food, 2 = eating, 3 = waiting for bill, 4 = left
        self.waiting = np.zeros(4) #time spent in each client "state"
        self.mood = 0

    def compute_mood(self, wait_time):
        #heuristic function for mood of client

        mood_const = 0.5

        if self.status == 2:
            self.mood += mood_const*wait_time
        else:
            self.mood -= wait_time*mood_const

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

    def __init__(self, max_clients):
        self.menu = None
        self.plates = None
        self.clean_plates = None
        self.n_cooking = 0
        self.n_ready = 0
        self.n_waiting = 0
        self.cooking_info = [] # [dish, time left, table]
        self.ready_info = [] # [dish, table]
        self.waiting_info = [] # [dish, preparation time, table]

    def init_menu(self):
        #name of dish: (price, preparation time)

        # self.menu = {
        #     "meat": [10, 10],
        #     "fish": [10, 15],
        #     "vegetarian" : [5, 10]
        # }

        self.menu = [[10, 3], [10, 3], [5, 3]]

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
        for order in table_order:
            reform_order[i][0] = order
            reform_order[i][1] = self.menu[order][1]
            reform_order[i][2] = table.index
            i += 1

        return reform_order

    def add_order(self, table_order):
        #takes order from entire table to kitchen, last element = 1 (dish is being prepared), = 0 (dish is waiting to be prepared)

        while self.n_cooking < 4 and len(self.waiting_info) > 0:
            self.cooking_info.append(self.waiting_info.pop(0))
            self.n_waiting -= 1
            self.n_cooking += 1
            self.clean_plates -= 1
            
        for order in table_order:   
            if self.n_cooking < 4:
                self.n_cooking += 1
                self.clean_plates -= 1
                self.cooking_info.append(order)
            else:
                self.n_waiting += 1
                self.waiting_info.append(order)

    def kitchen_timer(self):
        #tracks progress of cooking in kitchen

        self.cooking_info = sorted(self.cooking_info, key=itemgetter(1))

        for i in range(0, len(self.cooking_info)):
            if self.cooking_info[i][1] <= 0:
                self.ready_info.append(self.cooking_info[i])
                self.cooking_info[i][1] = -1
                self.n_ready += 1
                self.n_cooking -= 1

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
        self.n_ready -= table.size

    def dishes(self):
        #cleans dishes

        if (self.plates - self.clean_plates > 2):
            self.clean_plates += 2
        else:
            self.clean_plates = self.plates

class Agent(Kitchen):

    def __init__(self):
        # self.alpha = 0
        # self.gamma = 0
        # self.episode_max = 300
        # self.action_list = None

        self.action = None 
        self.states = None
        self.action_list = None # [0 = seat at table, 1 = serve, 2 = bring bill, 3 = clean plates], 1 if avaliable, 0 if impossible

    def init_actions(self):
        #name of dish: (price, preparation time)

        self.action_list = [1, 0, 0, 0]

    def act_seat(self, group, table):
        
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

        table.status = 2

    def act_bill(self, table):

        table.status = 0
        for client in table.group:
            client.status = 4
            client.mood += 5

        table.group = None

