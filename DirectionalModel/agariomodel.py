import sys
import random
import pygame
from pygame.locals import *
import pygame.locals
pygame.init()

# Game loop.
white = (255, 255, 255)
green = (25, 138, 12)
red = (204, 4, 4)
clist = [green,red]
move_speed = 10



class AgarGame:
    def __init__(self, w= 640, h = 480) -> None:
        self.w = w
        self.h = h
        self.n = 1
        self.state = [0]*9
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption("RL AGARGAME")
        self.clock = pygame.time.Clock()
        self.reset()
        

    def reset(self):
        self.pos = [self.w/2, self.h/2]
        self.food:tuple = (10 * (int(random.random() * (self.w/10 - 1 - self.w/(10*10)))+self.w/(10*10)), 10 * (int(random.random() * (self.h/10 - 1 - self.h/(10*10)))+self.h/(10*10)) )
        self.score = 0
        self.frame_iteration = 0


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
        if not self.is_collision() and not self.frame_iteration > 100*(self.score+1):
            if self.eat_food(self.pos[0], self.pos[1]):
                reward += 10
            # if d_to_food < 200:
            #     reward += 0.5

        else:
            game_over = True
            reward = -10
        self._draw()
        self.clock.tick(60)
        return reward, game_over, self.score


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

        scoretext = font.render(str(self.score), True, green, (0,0,0))
        scoretextRect = scoretext.get_rect()
        scoretextRect.center = (scoretextRect.width , scoretextRect.height)

        itrtext = pygame.font.Font('freesansbold.ttf', 20).render(f"Iteration: {self.n}", True, (255,255, 255), (0,0,0))
        itrtextRec = itrtext.get_rect()
        itrtextRec.center = (self.w - itrtextRec.width/2 - 10, itrtextRec.height)

        labels = ["food_left", "food_right", "food_up", "food_down", "wall_right", "wall_left", "wall_up", "wall_down", "d_to_food"]
        

        self._drawGrid()
        for i in range(len(self.state) - 1):
            itext = pygame.font.Font('freesansbold.ttf', 12).render(f"{labels[i]}: {self.state[i]}", True, (255,255, 255), (0,0,0))
            itextRec = itext.get_rect()
            itextRec.center = (self.w - itextRec.width/2 - 10, itextRec.height + ((i+1) * 40))
            self.screen.blit(itext, itextRec)
        self.screen.blit(scoretext, scoretextRect)
        self.screen.blit(itrtext, itrtextRec)
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
                while ((new_x-ballx)**2 + (new_y-bally)**2) < 50**2:
                    new_x = 10 * (int(random.random() * (self.w/10 - 1 - self.w/(10*10)))+self.w/(10*10))
                    new_y = 10 * (int(random.random() * (self.h/10 - 1 - self.h/(10*10)))+self.h/(10*10))
                self.food = (new_x,new_y)
                self.score += 1
                return True


