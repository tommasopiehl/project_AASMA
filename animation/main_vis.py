import pygame
from classes import Table, Kitchen, Door
from waiter_vis import Waiter
import json

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

def index_data(data, batch: int, time: int):
    for i in range(len(data)):
        if data[i]["batch"] == batch and data[i]["time"] == time:
            return i
    return False

def action_waiter(data, batch: int, time: int):
    index = index_data(data, batch, time)
    current = data[index]["current"][1:]
    if index == 0:
        old = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    else:
        old = data[index-1]["current"][1:]
    tot_t = round(len(current)/3)
    skip = 0
    for i in range(tot_t):
        if current[i+tot_t] != old[i+tot_t]:
            n_table = i
            break
        elif i == tot_t-1:
            skip = 1
    
    if skip == 0:
        if current[n_table+tot_t] == 1:
            return [1, n_table]
        elif current[n_table+tot_t] == 2:
            return [2, n_table]
        elif current[2*tot_t+n_table] == 0:
            return [3, n_table]
    else:
        skip = 0
        return [0, 0]
    
def event_env(data, batch: int, time: int, kitchen: Kitchen, door: Door, table: Table):
    index = index_data(data, batch, time)
    current = data[index]["current"][1:]
    if index == 0:
        old = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    else:
        old = data[index-1]["current"][1:]
    tot_t = round(len(current)/3)
    print(current)
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
for i in range(len(size_table)):
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
batch = 1
time = 1
per = 0
val = 0
running = True
co = 0
per = 0
event_env(data, batch, time, kitchen, door, table)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    if co == 0:
        val, n_table = action_waiter(data, batch, time)
    if val == 0:
        co = 1
        per = -1
    elif val == 1:
        if co == 0:
            co = 1
        if co == 1:
            per = waiter.to_door(door, per, screen)
            if per >= -1:
                co = 2
                per = 0
        elif co == 2:
            per = waiter.bring_guest(door, table, per, screen, n_table, guest_img)
            if per >= -1:
                co = 3
                per = 0
        else:
            per = waiter.bring_order(kitchen, per, screen, n_table)
        
    elif val == 2:
        if co == 0:
            co = 1
        if co == 1:
            per = waiter.to_kitchen(kitchen, per, screen)
            if per >= -1:
                co = 2
                per = 0
        else:
            per = waiter.bring_plates(door, table, per, screen, n_table, plate_img)
    
    elif val == 3:
        if co == 0:
            co = 1
            per = 0.000001
        if co == 1:
            per = waiter.to_table(door, table, per, screen, n_table, bill_img, "white")
            if per >= -1:
                co = 2
                per = 0
        else:
            per = waiter.bring_bill(door, table, per, screen, n_table, bill_img)
    
    if per <= -1:
        per = 0
        co = 0
        time += 1
        event_env(data, batch, time, kitchen, door, table)

    total_blitt(screen, waiter, kitchen, table, door)
    text = fnt.render("val = "+str(val), True, "black")
    screen.blit(text, (b_size-200, 10))
    pygame.display.flip()
    clk.tick(50)

pygame.quit()