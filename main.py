import pygame
import neat
import random

### CONSTANTS ###
WIN_SIZE = 900
GRID_DENSITY = 9

WIN = pygame.display.set_mode((WIN_SIZE, WIN_SIZE))
# We want it squared so it displays nicely
INSTANCES_ROW = 5
INSTANCES = INSTANCES_ROW*INSTANCES_ROW
INSTANCE_SIZE = WIN_SIZE/INSTANCES_ROW
CELL_SIZE = INSTANCE_SIZE/GRID_DENSITY

FPS = 60

class Grid:
    
    APPLE_COLOR = (255, 0, 0)
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = (20, 20, 20)
        self.table = []

        for _ in range(GRID_DENSITY):
            line = []
            for _ in range(GRID_DENSITY):
                line.append(0)
            self.table.append(line)

        self.spawn_apple()

    def spawn_apple(self):
        apple_x = random.randrange(0, GRID_DENSITY)
        apple_y = random.randrange(0, GRID_DENSITY)

        self.table[apple_y][apple_x] = 1

    def draw(self, win):
        for i in range(GRID_DENSITY):
            for j in range(GRID_DENSITY):
                # If cell is apple
                if self.table[i][j] == 1:
                    cell_x = self.x + j*CELL_SIZE
                    cell_y = self.y + i*CELL_SIZE
                    r = pygame.Rect(cell_x, cell_y, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(win, self.APPLE_COLOR, r)

def draw_window(grids):
    # Draw background
    bg_color = pygame.Color('black')
    bg = pygame.Rect(0, 0, WIN_SIZE, WIN_SIZE)
    pygame.draw.rect(WIN, bg_color, bg)

    # Draw grid borders
    border_color = pygame.Color('white')
    border_thickness = round(INSTANCE_SIZE/GRID_DENSITY/10)
    for row in range(INSTANCES_ROW + 1):
        pygame.draw.line(WIN, border_color, (row*INSTANCE_SIZE, 0) , (row*INSTANCE_SIZE, WIN_SIZE), border_thickness)
        pygame.draw.line(WIN, border_color, (0, row*INSTANCE_SIZE) , (WIN_SIZE, row*INSTANCE_SIZE), border_thickness)

    # Draw grids
    for g in grids:
        g.draw(WIN)

    pygame.display.update()

grids = []
for i in range(INSTANCES_ROW):
    for j in range(INSTANCES_ROW):
        x = j * INSTANCE_SIZE
        y = i * INSTANCE_SIZE
        grids.append(Grid(x, y))

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            quit()

    draw_window(grids)