import pygame
import neat
import random
import os
import math

### CONSTANTS ###
WIN_SIZE = 870
GRID_DENSITY = 9

WIN = pygame.display.set_mode((WIN_SIZE, WIN_SIZE))
# We want it squared so it displays nicely
INSTANCES_ROW = 1
POP_SIZE = 500
#INSTANCES = INSTANCES_ROW*INSTANCES_ROW
#INSTANCE_SIZE = WIN_SIZE/INSTANCES_ROW
CELL_SIZE = WIN_SIZE/GRID_DENSITY

pygame.font.init()

class Grid:
    APPLE_COLOR = (255, 0, 0)
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.table = []
        self.apple = (1, 1)

        for _ in range(GRID_DENSITY):
            line = []
            for _ in range(GRID_DENSITY):
                line.append(0)
            self.table.append(line)

        self.spawn_apple()

    def spawn_apple(self):
        apple_x = random.randrange(0, GRID_DENSITY-1)
        apple_y = random.randrange(0, GRID_DENSITY-1)
        
        while self.table[apple_y][apple_x] is not 0:
            apple_x = random.randrange(0, GRID_DENSITY-1)
            apple_y = random.randrange(0, GRID_DENSITY-1)

        self.apple = (apple_x, apple_y)
        
        self.table[apple_y][apple_x] = 1
    
    def respawn_apple(self):
        self.table[self.apple[1]][self.apple[0]] = 0
        self.spawn_apple()

    def place_snake(self, snake):
        for row in range(GRID_DENSITY):
            for col in range(GRID_DENSITY):
                if self.table[row][col] != 1:
                    self.table[row][col] = 0
        for x in snake:
            self.table[ x[1] ][ x[0] ] = 2

    def tail_dist(self, head):
        x = head[0]
        y = head[1]

        top = 0
        for i in reversed(range(0, y)):
            top = top + 1
            if self.table[i][y] == 2:
                break
        
        bottom = 0
        for i in range(y+1, GRID_DENSITY):
            bottom = bottom + 1
            if self.table[i][y] == 2:
                break

        left = 0
        for i in reversed(range(0, x)):
            left = left + 1
            if self.table[x][i] == 2:
                break

        right = 0
        for i in range(x+1, GRID_DENSITY):
            right = right + 1
            if self.table[x][i] == 2:
                break

        return (top, right, bottom, left)

    def death_booleans(self, head):
        x = head[0]
        y = head[1]

        top = False
        if y-1 < 0:
            top = True
        elif self.table[y-1][x] == 2:
            top = True
        
        bottom = False
        if y+1 > GRID_DENSITY-1:
            bottom = True
        elif self.table[y+1][x] == 2:
            bottom = True

        left = False
        if x-1 < 0:
            left = True
        elif self.table[y][x-1] == 2:
            left = True

        right = False
        if x+1 > GRID_DENSITY-1:
            right = True
        elif self.table[y][x+1] == 2:
            right = True

        return (top, right, bottom, left)

    def wall_dist(self, head):
        x = head[0]
        y = head[1]

        top = y
        right = x
        bottom = GRID_DENSITY - y - 1
        left = GRID_DENSITY - x - 1

        return (top, right, bottom, left)

    def apple_dist(self, head):
        x = head[0]
        y = head[1]

        top = 0
        for i in reversed(range(0, y)):
            top = top + 1
            if self.table[i][y] == 1:
                return (top, 0, 0, 0)
        
        bottom = 0
        for i in range(y+1, GRID_DENSITY):
            bottom = bottom + 1
            if self.table[i][y] == 1:
                return (0, 0, bottom, 0)

        left = 0
        for i in reversed(range(0, x)):
            left = left + 1
            if self.table[x][i] == 1:
                return (0, 0, 0, left)

        right = 0
        for i in range(x+1, GRID_DENSITY):
            right = right + 1
            if self.table[x][i] == 1:
                return (0, right, 0, 0)

        return (0, 0, 0, 0)

    def is_food_front(self, snake):
        dir = snake.direction
        head = snake.queue[-1]
        head_x = head[0]
        head_y = head[1]
        apple_x = self.apple[0]
        apple_y = self.apple[1]

        if dir == 'left' and apple_x < head_x:
            return True
        if dir == 'right' and apple_x > head_x:
            return True
    
        if dir == 'up' and apple_y < head_y:
            return True
        if dir == 'down' and apple_y > head_y:
            return True
        
        return False

    def is_food_back(self, snake):
        dir = snake.direction
        head = snake.queue[-1]
        head_x = head[0]
        head_y = head[1]
        apple_x = self.apple[0]
        apple_y = self.apple[1]

        if dir == 'left' and apple_x > head_x:
            return True
        if dir == 'right' and apple_x < head_x:
            return True
    
        if dir == 'up' and apple_y > head_y:
            return True
        if dir == 'down' and apple_y < head_y:
            return True
        
        return False

    def is_food_right(self, snake):
        dir = snake.direction
        head = snake.queue[-1]
        head_x = head[0]
        head_y = head[1]
        apple_x = self.apple[0]
        apple_y = self.apple[1]

        if dir == 'down' and apple_x < head_x:
            return True
        if dir == 'up' and apple_x > head_x:
            return True
    
        if dir == 'left' and apple_y < head_y:
            return True
        if dir == 'right' and apple_y > head_y:
            return True
        
        return False

    def is_food_left(self, snake):
        dir = snake.direction
        head = snake.queue[-1]
        head_x = head[0]
        head_y = head[1]
        apple_x = self.apple[0]
        apple_y = self.apple[1]

        if dir == 'up' and apple_x < head_x:
            return True
        if dir == 'down' and apple_x > head_x:
            return True
    
        if dir == 'right' and apple_y < head_y:
            return True
        if dir == 'left' and apple_y > head_y:
            return True
        
        return False

    def dist_to_death_front(self, snake):
        dir = snake.direction
        head = snake.queue[-1]

        if dir == 'left' and head[0]-1 < 0:
            return False
        if dir == 'right' and head[0]+1 > GRID_DENSITY-1:
            return False
        if dir == 'up' and head[1]-1 < 0:
            return False
        if dir == 'down' and head[1]+1 > GRID_DENSITY-1:
            return False

        if dir == 'left':
            if self.table[head[1]][head[0]-1] == 2:
                return False
        if dir == 'right':
            if self.table[head[1]][head[0]+1] == 2:
                return False
        if dir == 'up':
            if self.table[head[1]-1][head[0]] == 2:
                return False
        if dir == 'down':
            if self.table[head[1]+1][head[0]] == 2:
                return False
        
        return True

    def is_front_clear(self, snake):
        dir = snake.direction
        head = snake.queue[-1]

        if dir == 'left' and head[0]-1 < 0:
            return False
        if dir == 'right' and head[0]+1 > GRID_DENSITY-1:
            return False
        if dir == 'up' and head[1]-1 < 0:
            return False
        if dir == 'down' and head[1]+1 > GRID_DENSITY-1:
            return False

        if dir == 'left':
            if self.table[head[1]][head[0]-1] == 2:
                return False
        if dir == 'right':
            if self.table[head[1]][head[0]+1] == 2:
                return False
        if dir == 'up':
            if self.table[head[1]-1][head[0]] == 2:
                return False
        if dir == 'down':
            if self.table[head[1]+1][head[0]] == 2:
                return False
        
        return True

    def is_right_clear(self, snake):
        dir = snake.direction
        head = snake.queue[-1]

        if dir == 'left' and head[1]-1 < 0:
            return False
        if dir == 'right' and head[1]+1 > GRID_DENSITY-1:
            return False
        if dir == 'down' and head[0]-1 < 0:
            return False
        if dir == 'up' and head[0]+1 > GRID_DENSITY-1:
            return False

        if dir == 'left':
            if self.table[head[1]-1][head[0]] == 2:
                return False
        if dir == 'right':
            if self.table[head[1]+1][head[0]] == 2:
                return False
        if dir == 'up':
            if self.table[head[1]][head[0]+1] == 2:
                return False
        if dir == 'down':
            if self.table[head[1]][head[0]-1] == 2:
                return False
        return True

    def is_left_clear(self, snake):
        dir = snake.direction
        head = snake.queue[-1]

        if dir == 'right' and head[1]-1 < 0:
            return False
        if dir == 'left' and head[1]+1 > GRID_DENSITY-1:
            return False
        if dir == 'up' and head[0]-1 < 0:
            return False
        if dir == 'down' and head[0]+1 > GRID_DENSITY-1:
            return False

        if dir == 'left':
            if self.table[head[1]+1][head[0]] == 2:
                return False
        if dir == 'right':
            if self.table[head[1]-1][head[0]] == 2:
                return False
        if dir == 'up':
            if self.table[head[1]][head[0]-1] == 2:
                return False
        if dir == 'down':
            if self.table[head[1]][head[0]+1] == 2:
                return False
        return True


    def draw(self, win):
        for i in range(GRID_DENSITY):
            for j in range(GRID_DENSITY):
                # If cell is apple
                if self.table[i][j] == 1:
                    cell_x = self.x + j*CELL_SIZE
                    cell_y = self.y + i*CELL_SIZE
                    r = pygame.Rect(cell_x, cell_y, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(win, self.APPLE_COLOR, r, border_radius=40)

class Snake:
    SNAKE_COLOR = (0, 200, 0)
    #LIFE_RESET = GRID_DENSITY*GRID_DENSITY # Change to something smarter?
    LIFE_RESET = GRID_DENSITY*4
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.queue = []
        self.grow = False
        self.direction = 'left'
        self.life_left = self.LIFE_RESET
        # Start in center
        self.queue.append((round(GRID_DENSITY/2), round(GRID_DENSITY/2)))

    def draw(self, win):
        for client in self.queue:
            client_x = self.x + client[0]*CELL_SIZE
            client_y = self.y + client[1]*CELL_SIZE
            r = pygame.Rect(client_x, client_y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(win, self.SNAKE_COLOR, r, border_radius=10)

    def eat(self, grid):
        apple = grid.apple
        # If head position == apple
        if self.queue[-1][0] == apple[0] and self.queue[-1][1] == apple[1]:
            self.grow = True
            grid.respawn_apple()
            self.life_left = self.LIFE_RESET
            return True
        
        return False

    def move(self):
        self.life_left -= 1

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
            return True
        if self.queue[-1][1] < 0 or self.queue[-1][1] > GRID_DENSITY-1:
            return True

        head = self.queue[-1]
        for chunk in self.queue[:-1]:
            if head[0] == chunk[0] and head[1] == chunk[1]:
                return True

        return False

    def turn_right(self):
        if self.direction == 'left':
            self.direction = 'up'
        elif self.direction == 'up':
            self.direction = 'right'
        elif self.direction == 'right':
            self.direction = 'down'
        elif self.direction == 'down':
            self.direction = 'left'

    def turn_left(self):
        if self.direction == 'left':
            self.direction = 'down'
        elif self.direction == 'down':
            self.direction = 'right'
        elif self.direction == 'right':
            self.direction = 'up'
        elif self.direction == 'up':
            self.direction = 'left'

    def turn_dir(self, dir):
        if self.direction == 'up' and dir == 'down':
            return
        if self.direction == 'down' and dir == 'up':
            return
        if self.direction == 'right' and dir == 'left':
            return
        if self.direction == 'left' and dir == 'right':
            return

        self.direction = dir

    def too_old(self):
        if self.life_left < 0:
            return True
        else:
            return False
    
    def get_direction(self):
        if self.direction == 'left':
            return 0
        elif self.direction == 'down':
            return 1
        elif self.direction == 'right':
            return 2
        elif self.direction == 'up':
            return 3
    
    def goes_up(self):
        if self.direction == 'up':
            return True
        else:
            return False

    def goes_right(self):
        if self.direction == 'right':
            return True
        else:
            return False

spec = 0
gen = 0

def draw_window(grids, snakes):
    # Draw background
    bg_color = pygame.Color('black')
    bg = pygame.Rect(0, 0, WIN_SIZE, WIN_SIZE)
    pygame.draw.rect(WIN, bg_color, bg)

    # Draw grid borders || Changed to aalines. Maybe delete border thickness?
    border_color = pygame.Color('white')
    border_thickness = round(WIN_SIZE/GRID_DENSITY/10)
    '''
    for row in range(INSTANCES_ROW + 1):
        pygame.draw.aaline(WIN, border_color, (row*INSTANCE_SIZE, 0) , (row*INSTANCE_SIZE, WIN_SIZE), border_thickness)
        pygame.draw.aaline(WIN, border_color, (0, row*INSTANCE_SIZE) , (WIN_SIZE, row*INSTANCE_SIZE), border_thickness)
        

    # Draw grids
    for g in grids:
        g.draw(WIN)

    # Draw snakes
    for s in snakes:
        s.draw(WIN)
    '''

    if (len(grids) > 0):
        grids[0].draw(WIN)
        snakes[0].draw(WIN)


    global gen
    global spec
    STAT_FONT = pygame.font.SysFont("arial", 50)
    # Generation
    text_gen = STAT_FONT.render("generation: " + str(gen), True, pygame.Color("white"))
    WIN.blit(text_gen, (WIN_SIZE/2 - text_gen.get_width()/2, 10))

    # Species left
    text_spec = STAT_FONT.render("species: " + str(spec), True, pygame.Color("white"))
    WIN.blit(text_spec, (WIN_SIZE/2 - text_spec.get_width()/2, WIN_SIZE - 10 - text_spec.get_height()))

    pygame.display.update()

FPS = 10
IS_DISPLAYED = True
def single_player():

    # Initiate containers
    grids = []
    snakes = []
    x = 0
    y = 0
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
            if event.type == pygame.KEYDOWN:
                '''if event.key == pygame.K_a:
                    snakes[0].turn_left()
                if event.key == pygame.K_d:
                    snakes[0].turn_right()'''
                if event.key == pygame.K_a:
                    snakes[0].turn_dir('left')
                if event.key == pygame.K_d:
                    snakes[0].turn_dir('right')
                if event.key == pygame.K_w:
                    snakes[0].turn_dir('up')
                if event.key == pygame.K_s:
                    snakes[0].turn_dir('down')

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
            grids[x].place_snake(s.queue)
            s.move()
            s.eat(grids[x])
            head = s.queue[-1]

            '''
            print('Tail_dist:')
            print(grids[x].tail_dist(head))
            print('Wall_dist:')
            print(grids[x].wall_dist(head))
            print('Apple_dist:')
            print(grids[x].apple_dist(head))
            print('======================')
            '''
            print(grids[x].death_booleans(head))

        
        # Break the loop if there are no snakes
        if len(snakes) <= 0:
            print('All snakes died horribly.')
            run = False
            
        # Render everything
        draw_window(grids, snakes)

#single_player()

def eval_genomes(genomes, config):
    global FPS
    global IS_DISPLAYED
    global gen
    global spec
    gen += 1
    spec = len(genomes)

    # Initiate game containers
    grids = []
    snakes = []
    for _ in range(len(genomes)):
        x = 0
        y = 0
        grids.append(Grid(x, y))
        snakes.append(Snake(x, y))
    clock = pygame.time.Clock()
    run = True

    # Initiate ML stuff
    nets = []
    gens = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)

        g.fitness = 0
        gens.append(g)

    # Draw first frame
    if IS_DISPLAYED:
        draw_window(grids, snakes)

    # Begin the loop
    while run:
        if IS_DISPLAYED:
            clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        if (FPS > 1):
                            FPS = FPS - 1
                    if event.key == pygame.K_d:
                        FPS = FPS + 1
                    if event.key == pygame.K_SPACE:
                        IS_DISPLAYED = not IS_DISPLAYED


        # Snakes eat and move
        if run:
            for x, s in enumerate(snakes):
                s.move()
                if s.eat(grids[x]):
                    gens[x].fitness += 100

        # Check for snake crashes and collect trash
        rem_snakes = []
        rem_grids = []
        rem_nets = []
        rem_gens = []
        for x, s in enumerate(snakes):
            if s.crash():
                #print('sciana mordo')
                gens[x].fitness = 0
                spec = spec-1
                rem_snakes.append(s)
                rem_grids.append(grids[x])
                rem_nets.append(nets[x])
                rem_gens.append(gens[x])
            elif s.too_old():
                gens[x].fitness = gens[x].fitness * 2
                spec = spec-1
                rem_snakes.append(s)
                rem_grids.append(grids[x])
                rem_nets.append(nets[x])
                rem_gens.append(gens[x])
            else:
                gens[x].fitness += 1

        # Throw the trash into the garbage bin
        for s in rem_snakes:
            snakes.remove(s)
        for g in rem_grids:
            grids.remove(g)
        for g in rem_gens:
            gens.remove(g)
        for n in rem_nets:
            nets.remove(n)

        # Break the loop if there are no snakes
        if len(snakes) <= 0:
            print('All snakes died horribly.')
            run = False

        if run:
            for x, s in enumerate(snakes):
                grids[x].place_snake(s.queue)


        # ML DECISIONS
        if run:
            for x, s in enumerate(snakes):
                head = s.queue[-1]
                # wspolrzedne glowy weza i jablek
                head_x = s.queue[-1][0]
                head_y = s.queue[-1][1]
                apple_x = grids[x].apple[0]
                apple_y = grids[x].apple[1]

                # odleglosc glowy weza od jablka
                diff_x = apple_x - head_x
                diff_y = apple_y - head_y
                vec_x = head_x - apple_x
                vec_y = head_y - apple_y

                live_left = s.life_left

                # kierunek jazdy
                goes_right = s.goes_right()
                goes_up = s.goes_up()

                # obliczenie kata do jablka
                myradians = math.atan2(vec_y, vec_x)
                mydegrees = math.degrees(myradians) / 180

                # obliczanie odleglosci euklidesowej
                euclidean_distance = math.sqrt( pow(abs(diff_x), 2) + pow(abs(diff_y), 2) )

                # nagroda za zblizenie sie do jablka
                #gens[x].fitness += (1/euclidean_distance)*10

                wall_distances = grids[x].wall_dist(head)
                apple_distances = grids[x].apple_dist(head)
                tail_distances = grids[x].tail_dist(head)
                death_booleans = grids[x].death_booleans(head)

                # FRONT LEWO PRAWO
                coliders = (grids[x].is_front_clear(s), grids[x].is_left_clear(s), grids[x].is_right_clear(s))
                food_compass = (grids[x].is_food_front(s), grids[x].is_food_left(s), grids[x].is_food_right(s), grids[x].is_food_back(s))

                # INPUTY DO NN
                params = (coliders + food_compass)

                if False:
                    if x is 0:
                        print(params)

                
                # Zbierz wynik
                output = nets[x].activate(params)

                
                # 3 output
                maks = -math.inf
                kierunek = 2137
                for x, o in enumerate(output):
                    if o > maks:
                        kierunek = x
                        maks = o

                if kierunek == 0:
                    s.turn_left()
                elif kierunek == 1:
                    s.turn_right()
                else:
                    continue #go forward
                
                '''
                # 4 output
                # Wybierz kierunek
                maks = -math.inf
                kierunek = 2137
                for x, o in enumerate(output):
                    if o > maks:
                        kierunek = x
                        maks = o

                if kierunek == 0:
                    s.turn_dir('up')
                elif kierunek == 1:
                    s.turn_dir('down')
                elif kierunek == 2:
                    s.turn_dir('left')
                elif kierunek == 3:
                    s.turn_dir('right')
                '''

                # 1 output
                # Podejmij decyzje i skrec w lewo/prawo
                '''pole = 0.33
                if output[0] > pole:
                    s.turn_left()
                elif output[0] < -pole:
                    s.turn_right()'''

        
            
        # Render everything
        if IS_DISPLAYED:
            draw_window(grids, snakes)


def run(config_path):
    # Set configuration file
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Set population
    p = neat.Population(config)

    # Add reported for stats
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Set the fitness function
    winner = p.run(eval_genomes, 500)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)