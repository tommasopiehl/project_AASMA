import pygame
from math import floor
from classes

size_table = [2, 3, 4]
size_place = 50
size_waiter = 80
h_size = 600
b_size = 800

# initialization
pygame.init()

screen = pygame.display.set_mode((b_size, h_size))
pygame.display.set_caption("Waiter game")
screen.fill("white")

waiter = pygame.Surface((size_waiter, size_waiter))
waiter.fill("white")
pygame.draw.circle(waiter, "blue", (size_waiter/2, size_waiter/2), size_waiter/2)
screen.blit(waiter, ((b_size-size_waiter)/2, size_waiter/2))

table = []
for i in range(len(size_table)):
    table.append(pygame.Surface((size_place*size_table[i]/2, 2*size_place)))
    table[i].fill((150, 75, 0))
    for j in range(floor(size_table[i]/2)):
        pygame.draw.rect(table[i], "white", pygame.Rect((size_place/8+j*size_place, 0), (size_place*3/4, size_place/4)))
    for j in range(floor(size_table[i]/2)):
        pygame.draw.rect(table[i], "white", pygame.Rect((size_place/8+j*size_place, 2*size_place-size_place/4), (size_place*3/4, size_place/4)))
    if size_table[i] % 2 > 0:
        pygame.draw.rect(table[i], "white", pygame.Rect((size_place*size_table[i]/2-size_place/4, 5*size_place/8), (size_place/4, size_place*3/4)))
    screen.blit(table[i], (60, i*size_place*3+10))

kitchen = pygame.Surface((b_size/2, size_place))
kitchen.fill("yellow")
screen.blit(kitchen, (b_size/4, h_size-size_place))

pygame.display.flip()

#pygame.draw.circle(screen, "blue", (500, 500), 30, width=0)
#pygame.Rect((10, 10), (300, 100))
#pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()