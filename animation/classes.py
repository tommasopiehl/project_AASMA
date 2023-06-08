import pygame
from math import floor
import numpy as np

class Table:

    def __init__(self, size_place: int, size_table: int) -> None:
        self.obj = pygame.Surface((size_place*size_table/2, 2*size_place))
        self.obj.fill((150, 75, 0))

        self.place = []
        for j in range(floor(size_table/2)):
            self.place.append(Place(size_place, False))
            self.place[-1].blitt((size_place/8+j*size_place, 0), self.obj)
        for j in range(floor(size_table/2)):
            self.place.append(Place(size_place, False))
            self.place[-1].blitt((size_place/8+j*size_place, 2*size_place-size_place/4), self.obj)
        if size_table % 2 > 0:
            self.place.append(Place(size_place, True))
            self.place[-1].blitt((size_place*size_table/2-size_place/4, 5*size_place/8), self.obj)

    def blitt(self, pos: tuple, screen):
        self.vis = screen.blit(self.obj, pos)

    def color(self, color):
        for i in range(len(self.place)):
            self.place[i].color(color)
            self.place[i].blitt(self.place[i].vis.topleft, self.obj)


class Place:

    def __init__(self, size_place: int, rot: bool) -> None:
        sup = pygame.Surface((size_place*3/4, size_place/4))
        if rot:
            self.obj = pygame.transform.rotate(sup, 90)
        else:
            self.obj = sup
        self.obj.fill("white")

    def blitt(self, pos: tuple, screen):
        self.vis = screen.blit(self.obj, pos)

    def color(self, color):
        self.obj.fill(color)


class Kitchen:

    def __init__(self, b_size: int, size_place: int, size: int) -> None:
        self.obj = pygame.Surface((3*size_place, size_place))
        self.obj.fill("yellow")
        self.place = []
        for i in range(size):
            self.place.append(Place(size_place, False))
            self.obj.blit(self.place[-1].obj, (size_place/8+i*size_place, 0))

    def blitt(self, pos: tuple, screen):
        self.vis = screen.blit(self.obj, pos)

    def popout(self, n_table: int):
        self.place[n_table].obj.fill("red")


class Door:

    def __init__(self, size_place: int, num_table: int) -> None:
        self.obj = pygame.Surface((size_place, 3*size_place))
        self.obj.fill("green")
        self.place = []
        for j in range(num_table):
            self.place.append(Place(size_place, True))
            self.obj.blit(self.place[-1].obj, (0, size_place/8+j*size_place))
    
    def blitt(self, pos: tuple, screen):
        self.vis = screen.blit(self.obj, pos)

    def popout(self, n_table: int):
        self.place[n_table].obj.fill("red")