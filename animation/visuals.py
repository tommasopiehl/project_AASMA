import pygame
from math import floor
from classes import Table, Kitchen, Door
from waiter_vis import Waiter
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

def bring_bill(kitchen: Kitchen, table: Table, per: float, screen, n_table: int):
    per = waiter.to_table(kitchen, table, per, screen, n_table, bill_img, "white")
    return per

def bring_plates(waiter: Waiter, kitchen: Kitchen, table: Table, per: float, screen, n_table: int):
    per = waiter.to_table(kitchen, table, per, screen, n_table, plate_img, "blue")
    return per

def bring_guest(waiter: Waiter, door: Door, table: Table, per: float, screen, n_table: int):
    per = waiter.to_table(door, table, per, screen, n_table, guest_img, "red")
    return per

def bring_order(waiter: Waiter, kitchen: Kitchen, per: float, screen, n_table: int):
    per = waiter.to_kitchen(kitchen, per, screen)
    if per == 1:
        kitchen.place[n_table].fill("blue")
    return per

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

global plate_img
global guest_img
global bill_img
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

time_action = 1
per = 0
running = True
co = 0
per = 0
door.popout(0)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if co == 0:
        per = waiter.to_door(door, per, screen)
    if co == 1:
        per = bring_guest(waiter, door, table, per, screen, 0)
    if co == 2:
        per = bring_order(waiter, kitchen, per, screen, 0)
    if co == 3:
        per += -0.05
    if co == 4:
        per = bring_plates(waiter, kitchen, table, per, screen, 0)
    if per <= -1:
        per = 0
        co += 1
    total_blitt(screen, waiter, kitchen, table, door)
    text = fnt.render("per = "+str(per), True, "black")
    screen.blit(text, (b_size-200, 10))
    pygame.display.flip()
    clk.tick(100)

pygame.quit()