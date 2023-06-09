import pygame
from classes import Table, Kitchen, Door, Group
from waiter_vis import Waiter
import json
import numpy as np

# table = red -> waiting for food, blue -> eating, yellow -> waiting for bill, white -> free
# kitchen = red -> ready, blue -> preparing, white -> none
# door = red -> waiting for table, white -> none
# waiter = red -> bring something + img, blue -> moving freely

def total_blitt(screen: pygame.Surface, waiter: Waiter, kitchen: Kitchen, table, door: Door):
    screen.fill("white")
    for i in range(len(size_table)):
        table[i].blitt((table[i].vis.x, table[i].vis.y), screen)
    kitchen.blitt((kitchen.vis.x, kitchen.vis.y), screen)
    door.blitt((door.vis.x, door.vis.y), screen)
    waiter.blitt((waiter.vis.x, waiter.vis.y), screen)

def retrieve_time(data, batch):
    for i in range(len(data)):
        if data[i]["batch"] == batch:
            return i
    return False

def index_data(data, batch: int, time: int):
    for i in range(len(data)):
        if data[i]["batch"] == batch and data[i]["time"] == time:
            return i
    return False

def action_waiter(data, group, batch: int, time: int):
    index = index_data(data, batch, time)
    current = data[index]["current"]
    old = data[index-1]["current"]
    tot_t = round(len(current)/3)
    for i in range(tot_t):
        if current[i+tot_t] != old[i+tot_t]:
            if current[i+tot_t] == 1:
                for j in range(tot_t):
                    if current[2*tot_t+j] != old[2*tot_t+j]:
                        group[i].association(j, table[j])
                return [1, i]
            elif current[i+tot_t] == 2:
                return [2, i]
            elif current[2*tot_t+i] == 0:
                return [3, i]
        elif i == tot_t-1:
            return [0, 0]
    
def event_env(data, batch: int, time: int, kitchen: Kitchen, door: Door, table: Table):
    index = index_data(data, batch, time)
    current = data[index]["current"]
    old = data[index-1]["current"]
    tot_t = round(len(current)/3)
    # print(current)
    for i in range(tot_t):
        if current[i] != old[i] and current[i] == 3:
            kitchen.popout(i)
        if current[i+tot_t] != old[i+tot_t] and current[i+tot_t] == 0:
            door.popout(i)
        if current[i+tot_t] != old[i+tot_t] and current[i+tot_t] == 3:
            table[i].color("yellow")    


size_table = [2, 3, 4]
size_place = 50
size_waiter = 80
h_size = 600
b_size = 800

# initialization
pygame.init()
clk = pygame.time.Clock()

screen = pygame.display.set_mode((b_size, h_size))
pygame.display.set_caption("Waiter game")
screen.fill("white")

plate_img = pygame.transform.scale(pygame.image.load("animation/plate.png").convert_alpha(), (50, 50))
guest_img = pygame.transform.scale(pygame.image.load("animation/guest.png").convert_alpha(), (50, 50))
bill_img = pygame.transform.scale(pygame.image.load("animation/bill.png").convert_alpha(), (50, 50))

fnt = pygame.font.SysFont("Arial", 20)

waiter = Waiter(size_waiter)
waiter.blitt(((b_size-size_waiter)/2, size_waiter/2), screen)

table = []
group = []
for i in range(len(size_table)):
    group.append(Group(size_table[i]))
    table.append(Table(size_place, size_table[i]))
    table[i].blitt((60, i*size_place*3+10), screen)

kitchen = Kitchen(b_size, size_place, len(size_table))
kitchen.blitt((b_size/4, h_size-size_place), screen)

door = Door(size_place, len(size_table))
door.blitt((b_size-size_place, h_size/2-len(size_table)*size_place), screen)

pygame.display.flip()

# opening file
with open("states.json", "r") as json_file:
    data = json.load(json_file)

# param for running
batch = 6
time = retrieve_time(data, batch)
dt = 0

association = np.zeros(round(len(data[0]["current"])/3))

val = 0
co = 0
per = 0
event_env(data, batch, time, kitchen, door, table)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if index_data(data, batch, time) == False:
        running = False
    
    if co == 0:
        val, n_group = action_waiter(data, group, batch, time)
    
    if val == 0:
        co = 1
        per -= 0.005
    
    elif val == 1:
        if co == 0:
            co = 1
        if co == 1:
            per = waiter.to_door(door, per, screen)
            if per <= -1:
                co = 2
                per = 0
        elif co == 2:
            per = waiter.bring_guest(door, table, per, screen, group[n_group].table, guest_img)
            if per <= -1:
                co = 3
                per = 0
        else:
            per = waiter.bring_order(kitchen, per, screen, group[n_group].table)
        
    elif val == 2:
        if co == 0:
            co = 1
        if co == 1:
            per = waiter.to_kitchen(kitchen, per, screen)
            if per <= -1:
                co = 2
                per = 0
        else:
            per = waiter.bring_plates(kitchen, table, per, screen, group[n_group].table, plate_img)
    
    elif val == 3:
        if co == 0:
            co = 1
        if co == 1:
            per = waiter.bring_bill(door, table, per, screen, group[n_group].table, bill_img)
            if per <= -1:
                co = 2
                per = 0
        else:
            per = waiter.to_door(door, per, screen)
    
    if per <= -1:
        per = 0
        co = 0
        time += 1
        dt += 1
        event_env(data, batch, time, kitchen, door, table)

    total_blitt(screen, waiter, kitchen, table, door)
    text = fnt.render("time = "+str(dt)+" val = "+str(val)+" tab = "+str(group[n_group].table), True, "black")
    screen.blit(text, (b_size-200, 10))
    pygame.display.flip()
    clk.tick(200)

pygame.quit()