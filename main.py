import pygame
import neat
import random

### CONSTANTS ###
WIN_SIZE = 900
GRID_DENSITY = 9

WIN = pygame.display.set_mode((WIN_SIZE, WIN_SIZE))
# We want it squared so it displays nicely
INSTANCES_ROW = 2
INSTANCES = INSTANCES_ROW*INSTANCES_ROW
INSTANCE_SIZE = WIN_SIZE/INSTANCES_ROW
CELL_SIZE = INSTANCE_SIZE/GRID_DENSITY



class Grid:
    APPLE_COLOR = (255, 0, 0)
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.table = []
        self.apple = (4, 5)

        for _ in range(GRID_DENSITY):
            line = []
            for _ in range(GRID_DENSITY):
                line.append(0)
            self.table.append(line)

        self.spawn_apple()

    def spawn_apple(self):
        apple_x = random.randrange(0, GRID_DENSITY)
        apple_y = random.randrange(0, GRID_DENSITY)
        
        while apple_x == self.apple[0]:
            apple_x = random.randrange(0, GRID_DENSITY)

        while apple_y == self.apple[1]:
            apple_y = random.randrange(0, GRID_DENSITY)

        self.apple = (apple_x, apple_y)
        
        self.table[apple_y][apple_x] = 1
    
    def respawn_apple(self):
        self.table[self.apple[1]][self.apple[0]] = 0
        self.spawn_apple()


    def draw(self, win):
        for i in range(GRID_DENSITY):
            for j in range(GRID_DENSITY):
                # If cell is apple
                if self.table[i][j] == 1:
                    cell_x = self.x + j*CELL_SIZE
                    cell_y = self.y + i*CELL_SIZE
                    r = pygame.Rect(cell_x, cell_y, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(win, self.APPLE_COLOR, r)

class Snake:
    SNAKE_COLOR = (0, 200, 0)
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.queue = []
        self.grow = False
        self.direction = 'left'
        # Start in center
        self.queue.append((round(GRID_DENSITY/2), round(GRID_DENSITY/2)))

    def draw(self, win):
        for client in self.queue:
            client_x = self.x + client[0]*CELL_SIZE
            client_y = self.y + client[1]*CELL_SIZE
            r = pygame.Rect(client_x, client_y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(win, self.SNAKE_COLOR, r)

    def eat(self, grid):

        apple = grid.apple
        # If head position == apple
        if self.queue[-1][0] == apple[0] and self.queue[-1][1] == apple[1]:
            self.grow = True
            grid.respawn_apple()

    def move(self):
        if self.direction == 'left':
            self.queue.append( (self.queue[-1][0]-1, self.queue[-1][1]) )
        elif self.direction == 'right':
            self.queue.append( (self.queue[-1][0]+1, self.queue[-1][1]) )
        elif self.direction == 'up':
            self.queue.append( (self.queue[-1][0], self.queue[-1][1]-1) )
        elif self.direction == 'down':
            self.queue.append( (self.queue[-1][0], self.queue[-1][1]+1) )

        if self.grow:
            self.grow = False
            return
        else:
            self.queue.pop(0)

    def crash(self):
        if self.queue[-1][0] < 0 or self.queue[-1][0] > GRID_DENSITY-1:
            print('crash')
            return True
        if self.queue[-1][1] < 0 or self.queue[-1][1] > GRID_DENSITY-1:
            print('crash')
            return True
            

        return False


def draw_window(grids, snakes):
    # Draw background
    bg_color = pygame.Color('black')
    bg = pygame.Rect(0, 0, WIN_SIZE, WIN_SIZE)
    pygame.draw.rect(WIN, bg_color, bg)

    # Draw grid borders || Changed to aalines. Maybe delete border thickness?
    border_color = pygame.Color('white')
    border_thickness = round(INSTANCE_SIZE/GRID_DENSITY/10)
    for row in range(INSTANCES_ROW + 1):
        pygame.draw.aaline(WIN, border_color, (row*INSTANCE_SIZE, 0) , (row*INSTANCE_SIZE, WIN_SIZE), border_thickness)
        pygame.draw.aaline(WIN, border_color, (0, row*INSTANCE_SIZE) , (WIN_SIZE, row*INSTANCE_SIZE), border_thickness)

    # Draw grids
    for g in grids:
        g.draw(WIN)

    # Draw snakes
    for s in snakes:
        s.draw(WIN)

    pygame.display.update()

FPS = 2
def main():

    # Initiate containers
    grids = []
    snakes = []
    for i in range(INSTANCES_ROW):
        for j in range(INSTANCES_ROW):
            x = j * INSTANCE_SIZE
            y = i * INSTANCE_SIZE
            grids.append(Grid(x, y))
            snakes.append(Snake(x, y))
    clock = pygame.time.Clock()
    run = True

    # Draw first frame
    draw_window(grids, snakes)

    # Begin the loop
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # Check for snake crashes
        rem_s = []
        rem_g = []
        for x, s in enumerate(snakes):
            if s.crash():
                rem_s.append(s)
                rem_g.append(grids[x])

        # Remove crashed snakes and grids
        for s in rem_s:
            snakes.remove(s)
        for g in rem_g:
            grids.remove(g)

        # Snakes eat and move
        for x, s in enumerate(snakes):
            s.move()
            s.eat(grids[x])

        
        # Break the loop if there are no snakes
        if len(snakes) <= 0:
            print('All snakes died horribly.')
            run = False
            
        # Render everything
        draw_window(grids, snakes)

main()