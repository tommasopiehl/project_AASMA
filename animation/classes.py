import pygame
from math import floor

class Table:

    def __init__(self, size_place: int, size_table: int) -> None:
        self.obj = pygame.Surface((size_place*size_table/2, 2*size_place))
        self.obj.fill((150, 75, 0))
        self.place = []
        for j in range(floor(size_table/2)):
            self.place.append(Place(size_place, False))
            self.place[-1].blit(self.obj, (size_place/8+j*size_place, 0))
        for j in range(floor(size_table/2)):
            self.place.append(Place(size_place, False))
            self.place[-1].blit(self.obj, (size_place/8+j*size_place, 2*size_place-size_place/4))
        if size_table % 2 > 0:
            self.place.append(Place(size_place, True))
            self.place[-1].blit(self.obj, (size_place*size_table/2-size_place/4, 5*size_place/8))


class Place:

    def __init__(self, size_place: int, rot: bool) -> None:
        sup = pygame.Surface((size_place*3/4, size_place/4))
        if rot:
            self = pygame.transform.rotate(sup, 90)
        else:
            self = sup
        

class Waiter:

    def __init__(self, size_waiter: int) -> None:
        self = pygame.Surface((size_waiter, size_waiter))
        self.fill("white")
        pygame.draw.circle(self, "blue", (size_waiter/2, size_waiter/2), size_waiter/2)


class Kitchen:

    def __init__(self, b_size: int, size_place: int) -> None:
        self = pygame.Surface((b_size/2, size_place))
        self.fill("yellow")