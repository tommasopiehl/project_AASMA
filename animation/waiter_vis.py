import pygame
import numpy as np
from math import floor
from classes import Kitchen, Table, Door

class Waiter:

    def __init__(self, size_waiter: int) -> None:
        global size_w
        size_w = size_waiter
        self.obj = pygame.Surface((size_waiter, size_waiter))
        self.obj.fill("white")
        pygame.draw.circle(self.obj, "blue", (size_waiter/2, size_waiter/2), size_waiter/2)

    def blitt(self, pos: tuple, screen):
        self.vis = screen.blit(self.obj, pos)

    def smooth_movement(self, posf: tuple, per: float):
        ax = self.vis.x
        coeff = np.array([[1, 1, 1], [3, 4, 5], [6, 12, 20]])
        val = np.array([[posf[0]-ax], [0], [0]])
        bx, cx, dx= np.linalg.inv(coeff) @ val

        ay = self.vis.y
        coeff = np.array([[1, 1, 1], [3, 4, 5], [6, 12, 20]])
        val = np.array([[posf[1]-ay], [0], [0]])
        by, cy, dy= np.linalg.inv(coeff) @ val

        tup = (floor(ax+(bx*per**3)+(cx*per**4)+(dx*per**5)), floor(ay+(by*per**3)+(cy*per**4)+(dy*per**5)))

        return tup

    def color(self, color):
        pygame.draw.circle(self.obj, color, (size_w/2, size_w/2), size_w/2)

    def dest_table(self, table: Table):
        tup = (table.vis.right, (table.vis.top+table.vis.bottom)/2+(self.vis.y-self.vis.bottom)/2)
        return tup
    
    def dest_kitchen(self, kitchen: Kitchen):
        tup = ((kitchen.vis.right+kitchen.vis.left)/2-(self.vis.right-self.vis.x)/2, kitchen.vis.top+(self.vis.y-self.vis.bottom))
        return tup
    
    def dest_door(self, door: Door):
        tup = (door.vis.left-(self.vis.right-self.vis.x), (door.vis.top+door.vis.bottom)/2+(self.vis.y-self.vis.bottom)/2)
        return tup
    
    def take(self, obj, n_table: int, img: pygame.Surface):
        obj.place[n_table].obj.fill("white")
        self.color("red")
        self.obj.blit(img, ((size_w-50)/2, (size_w-50)/2))

    def to_kitchen(self, kitchen: Kitchen, per: float, screen: pygame.Surface):
        if per <= 1:
            self.blitt(self.smooth_movement(self.dest_kitchen(kitchen), per), screen)
            per += 0.005
        else:
            self.color("blue")
            self.blitt((self.vis.x, self.vis.y), screen)
            per = -1
        return per
    
    def to_table(self, origin, table: Table, per: float, screen: pygame.Surface, n_table: int, img: pygame.Surface, color):
        if per == 0:
            self.take(origin, n_table, img)
        if per <= 1:
            self.blitt(self.smooth_movement(self.dest_table(table[n_table]), per), screen)
            per += 0.005
        else:
            self.color("blue")
            self.blitt((self.vis.x, self.vis.y), screen)
            table[n_table].color(color)
            per = -1
        return per
    
    def to_door(self, door: Door, per: float, screen: pygame.Surface):
        if per <= 1:
            self.blitt(self.smooth_movement(self.dest_door(door), per), screen)
            per += 0.005
        else:
            self.color("blue")
            self.blitt((self.vis.x, self.vis.y), screen)
            per = -1
        return per
    
    def bring_bill(self, kitchen: Kitchen, table: Table, per: float, screen, n_table: int, bill_img: pygame.Surface):
        per = self.to_table(kitchen, table, per, screen, n_table, bill_img, "white")
        return per

    def bring_plates(self, kitchen: Kitchen, table: Table, per: float, screen, n_table: int, plate_img: pygame.Surface):
        per = self.to_table(kitchen, table, per, screen, n_table, plate_img, "blue")
        return per

    def bring_guest(self, door: Door, table: Table, per: float, screen, n_table: int, guest_img: pygame.Surface):
        per = self.to_table(door, table, per, screen, n_table, guest_img, "red")
        return per

    def bring_order(self, kitchen: Kitchen, per: float, screen, n_table: int):
        per = self.to_kitchen(kitchen, per, screen)
        if per == 1:
            kitchen.place[n_table].fill("blue")
        return per