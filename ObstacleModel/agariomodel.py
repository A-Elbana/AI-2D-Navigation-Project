import math
import sys
import random
import pygame
from pygame.locals import *
import pygame.locals

from helper import distance, do_lines_intersect
pygame.init()

# Game loop.
white = (255, 255, 255)
GREEN = (25, 138, 12)
RED = (204, 4, 4)
wall_size = 8
move_speed = 10
grid_size = 40

class Wall:
    alignment = 0
    def __init__(self, x1, y1, x2, y2, alignment):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.alignment = alignment

    def draw(self, screen, wall_size):
        pygame.draw.line(screen, RED, (self.x1, self.y1), (self.x2, self.y2), wall_size)



def get_random_point(x1, y1, x2, y2, min_distance=40, grid_size=40):
    """
    This function generates a random point on the line segment between two points, 
    ensuring it's at least min_distance away from each point and snaps to a grid of grid_size pixels.

    Args:
        x1: x-coordinate of the first point.
        y1: y-coordinate of the first point.
        x2: x-coordinate of the second point.
        y2: y-coordinate of the second point.
        min_distance: Minimum distance the random point should be from each endpoint (default 40 pixels).
        grid_size: Size of the grid to snap the point to (default 40 pixels).

    Returns:
        A tuple containing the x and y coordinates of the random point, 
        or None if no point can be found within the constraints.
    """
    dx = x2 - x1
    dy = y2 - y1
    segment_length = math.sqrt(dx**2 + dy**2)

    # Ensure min_distance is less than half the segment length to avoid impossible cases
    if min_distance > segment_length / 2:
        return None

    while True:
        t = random.random()
        x = x1 + t * dx
        y = y1 + t * dy

        # Snap coordinates to the grid
        x_grid_snapped = round(x / grid_size) * grid_size
        y_grid_snapped = round(y / grid_size) * grid_size

        distance_to_a = math.sqrt((x_grid_snapped - x1)**2 + (y_grid_snapped - y1)**2)
        distance_to_b = math.sqrt((x_grid_snapped - x2)**2 + (y_grid_snapped - y2)**2)
        if distance_to_a >= min_distance and distance_to_b >= min_distance:
            return (x_grid_snapped, y_grid_snapped)



class AgarGame:
    def __init__(self, w= 640, h = 480) -> None:
        self.w = w
        self.h = h
        self.n = 1
        self.d_to_food = 0
        self.d_to_wall = 0
        self.state = [0]*9
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption("RL AGARGAME")
        self.clock = pygame.time.Clock()
        self.reset()
        

    def reset(self):
        self.pos = [self.w / 2, self.h / 2]
        self.food: tuple = (
            10
            * (
                int(random.random() * (self.w / 10 - 1 - self.w / (10 * 10)))
                + self.w / (10 * 10)
            ),
            10
            * (
                int(random.random() * (self.h / 10 - 1 - self.h / (10 * 10)))
                + self.h / (10 * 10)
            ),
        )
        while ((self.food[0] - self.pos[0]) ** 2 + (self.food[1] - self.pos[1]) ** 2) < 100**2:
            self.food = (10 * (
                int(random.random() * (self.w / 10 - 1 - self.w / (10 * 10)))
                + self.w / (10 * 10)
            ), 10 * (
                int(random.random() * (self.h / 10 - 1 - self.h / (10 * 10)))
                + self.h / (10 * 10)
            ))
        self.wall = self._generate_wall()
        self.d_to_food = (
            (self.pos[0] - self.food[0]) ** 2 + (self.pos[1] - self.food[1]) ** 2
        ) ** 0.5
        self.d_to_wall = distance(self.pos, self.wall)
        self.score = 0
        self.frame_iteration = 0


    def _generate_wall(self):
    # Ensure walls stay within grid boundaries
        x1, y1 = get_random_point(self.pos[0],self.pos[1], self.food[0], self.food[1])
        # Randomly choose horizontal or vertical wall
        a = 0
        if abs((self.food[1]-self.pos[1])/(self.food[0]-self.pos[0])) > 1 :
            x2 = x1 + 2*grid_size
            x1 = x1 - 2*grid_size
            y2 = y1
            
        else:
            x2 = x1
            y2 = y1 + 2*grid_size
            y1 = y1 - 2*grid_size
            a = 1
        return Wall(x1, y1, x2, y2, a)

    def play_step(self, action:list):
        self.frame_iteration += 1
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        
        if action[0]:
            self.pos[0] += move_speed
        if action[1]:
            self.pos[0] -= move_speed
        if action[2]:
            self.pos[1] -= move_speed
        if action[3]:
            self.pos[1] += move_speed
        reward = 0
        game_over = False
        d_to_food = ((self.pos[0] - self.food[0])**2 + (self.pos[1] - self.food[1])**2)**0.5
        d_to_wall = distance(self.pos, self.wall)
        if not self.is_collision() and not self.frame_iteration > 200*(self.score+1) and not self._hit_wall_simplified():
            if self.eat_food(self.pos[0], self.pos[1]):
                reward += 10
            if not do_lines_intersect((self.pos[0], self.pos[1]), (self.food[0], self.food[1]), (self.wall.x1,self.wall.y1),(self.wall.x2,self.wall.y2)):
                if self.d_to_food > d_to_food:
                    reward += 1
                else:
                    reward -= 1
            else:
                if self.wall.alignment and (action[2] or action[3]):
                    reward += 1
                if self.wall.alignment == 0 and (action[0] or action[1]):
                    reward += 1

            self.d_to_food = d_to_food
            self.d_to_wall = d_to_wall
        else:
            game_over = True
            reward = -10
        self._draw()
        self.clock.tick(60)
        return reward, game_over, self.score


    def _hit_wall_simplified(self):
        wall = self.wall
        pos = self.pos
        return pos[0] >= wall.x1 and pos[0] <= wall.x2 and pos[1] >= wall.y1 and pos[1] <= wall.y2



    def _hit_wall(self):
        wall = self.wall
        pos = self.pos
        if wall.x1 == wall.x2 :
            if pos[1] + 30 > wall.y1 and pos[1] < wall.y1:
                return ((pos[0] - wall.x1)**2 + (pos[1] - wall.y1)**2) <= 30**2
            if pos[1] <= wall.y2 and pos[1] >= wall.y1:
                return abs(wall.x1 - pos[0]) < 30
            if pos[1]  > wall.y2 and pos[1] - 30 < wall.y2:
                return ((pos[0] - wall.x2)**2 + (pos[1] - wall.y2)**2) <= 30**2
        else:
            if pos[0] + 30 > wall.x1 and pos[0] < wall.x1:
                return ((pos[0] - wall.x1)**2 + (pos[1] - wall.y1)**2) <= 30**2
            if pos[0] <= wall.x2 and pos[0] >= wall.x1:
                return abs(wall.y1 - pos[1]) < 30
            if pos[0]  > wall.x2 and pos[0] - 30 < wall.x2:
                return ((pos[0] - wall.x2)**2 + (pos[1] - wall.y2)**2) <= 30**2

    def is_collision(self):
        if self.pos[0] + 30 > self.w:
            return True
        if self.pos[0] - 30 < 0:
            return  True
        
        if self.pos[1] + 30 > self.h:
            return True
        if self.pos[1] - 30 < 0:
            return True
    def _drawFood(self, x,y) -> pygame.Rect:
        pygame.draw.circle(self.screen,(100,255,100), (x,y), 10)


    def _drawGrid(self):
        blockSize = 40 #Set the size of the grid block
        for x in range(0, self.w, blockSize):
            for y in range(0, self.h, blockSize):
                rect = pygame.Rect(x, y, blockSize, blockSize)
                pygame.draw.rect(self.screen, (75,75,75), rect, 1)
    
    def _draw(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font('freesansbold.ttf', 32)

        scoretext = font.render(str(self.score), True, GREEN, (0,0,0))
        scoretextRect = scoretext.get_rect()
        scoretextRect.center = (scoretextRect.width , scoretextRect.height)

        itrtext = pygame.font.Font('freesansbold.ttf', 20).render(f"Iteration: {self.n}", True, (255,255, 255), (0,0,0))
        itrtextRec = itrtext.get_rect()
        itrtextRec.center = (self.w - itrtextRec.width/2 - 10, itrtextRec.height)

        labels = ["x","y","food_y","food_x", "d_to_food"]
        

        self._drawGrid()
        for i in range(len(self.state)-5):
            itext = pygame.font.Font('freesansbold.ttf', 12).render(f"{self.state[i]}", True, (255,255, 255), (0,0,0))
            itextRec = itext.get_rect()
            itextRec.center = (self.w - itextRec.width/2 - 10, itextRec.height + ((i+1) * 40))
            self.screen.blit(itext, itextRec)
        self.screen.blit(scoretext, scoretextRect)
        self.screen.blit(itrtext, itrtextRec)
        self.wall.draw(self.screen, wall_size)
        
        intersection = do_lines_intersect((self.pos[0], self.pos[1]), (self.food[0], self.food[1]), (self.wall.x1,self.wall.y1),(self.wall.x2,self.wall.y2))
        pygame.draw.line(self.screen, [GREEN,RED][intersection], (self.pos[0], self.pos[1]), (self.food[0], self.food[1]), 3)
        self._drawFood(self.food[0],self.food[1])
        pygame.draw.circle(self.screen, (100,100,255), tuple(self.pos), 30)
        pygame.draw.circle(self.screen, (0,0,255),tuple( self.pos), 20)
        
        pygame.display.flip()



    def eat_food(self, ballx, bally):
        if bally - 30 < (self.food[1]) and bally + 30 > (self.food[1]):
            if (ballx-30 < self.food[0]
                and ballx+30 > (self.food[0])):
                new_x = 10 * (int(random.random() * (self.w/10 - 1 - self.w/(10*10)))+self.w/(10*10))
                new_y = 10 * (int(random.random() * (self.h/10 - 1 - self.h/(10*10)))+self.h/(10*10))
                while ((new_x-ballx)**2 + (new_y-bally)**2) < 100**2:
                    new_x = 10 * (int(random.random() * (self.w/10 - 1 - self.w/(10*10)))+self.w/(10*10))
                    new_y = 10 * (int(random.random() * (self.h/10 - 1 - self.h/(10*10)))+self.h/(10*10))
                self.food = (new_x,new_y)
                self.wall = self._generate_wall()
                self.score += 1
                return True


