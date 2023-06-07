import pygame
from math import floor
from classes import Table, Kitchen, Door
from waiter_vis import Waiter
import numpy as np

def total_blitt(screen: pygame.Surface, waiter: Waiter, kitchen: Kitchen, table, door: Door):
    screen.fill("white")
    for i in range(len(size_table)):
        table[i].blitt((table[i].vis.x, table[i].vis.y), screen)
    kitchen.blitt((kitchen.vis.x, kitchen.vis.y), screen)
    door.blitt((door.vis.x, door.vis.y), screen)
    waiter.blitt((waiter.vis.x, waiter.vis.y), screen)

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
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if co == 0:
        per = waiter.to_kitchen(kitchen, per, screen)
    if co == 1:
        per = waiter.to_table(kitchen, table, per, screen, 1, plate_img, "red")
    if co == 2:
        per = waiter.to_door(door, per, screen)
    if per == -1:
        per = 0
        co += 1
    total_blitt(screen, waiter, kitchen, table, door)
    pygame.display.flip()
    clk.tick(100)

pygame.quit()