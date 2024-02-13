import pygame
import random
from enum import Enum
from collections import namedtuple
from pygame import Vector2 as vec2
from pygame import Vector3 as vec3
import numpy as np
import game

class Action(Enum):
    THROW = 1
    HIT = 2
    WAIT = 3

class PingPongPlayerAI:
    
    def __init__(self, index):
        self.pos = vec3(0, 0, 0)
        self.pad_pos = self.pos
        self.pad_dir = vec3(1, 0, 0)
        self.area_center = vec2(0, 0)
        self.area_size = vec2(0, 0)
        self.facing_dir = vec3(1, 0, 0)
        self.action = Action.WAIT
        self.index = index
        self.reset()

    def setArea(self, center, size):
        self.area_center = center
        self.area_size = size

    def setPlayer(self, pt, direction):
        self.pos = pt
        self.pad_pos = pt
        self.facing_dir = direction
        self.pad_dir = self.facing_dir
        
    def reset(self):        
        # init game state
        self.setPlayer(vec3(0, 0, 0), vec3(1, 0, 0))
        self.pos = vec3(self.area_size.x / 2, self.area_size.y / 2, 1.0)
        self.pad_pos = self.pos
        self.action = Action.WAIT
        
        self.score = 0
        self.ball = None
    
    def drawPlayableArea(self, pp_game):
        pp_game.drawRect(game.YELLOW, self.area_center, self.area_size, 10)
    
    def drawPlayerIcon(self, pp_game):
        pygame.draw.rect(pp_game.display, game.GREEN, pygame.Rect(pp_game.toScreenCoord(self.pos.xy), vec2(game.BLOCK_SIZE)))
        pygame.draw.rect(pp_game.display, game.BLUE2, pygame.Rect(pp_game.toScreenCoord(self.pos.xy)+vec2(4), vec2(game.BLOCK_SIZE)-vec2(8)))

    def playStep(self, action):
        # 2. move
        self.move(action) # update the head
        
        # 3. check if game over
        game_reward = 0
        game_over = False
        if self.isCollision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            game_reward = -10
            return game_reward, game_over, self.score
            
        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            game_reward = 10
            self._place_food()
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(game.SPEED)
        # 6. return game over and score
        return game_reward, game_over, self.score
    
    def isCollision(self, pt=None):
        pass
#        if pt is None:
#            pt = self.head
#        # hits boundary
#        if pt.x > self.w - game.BLOCK_SIZE or pt.x < 0 or pt.y > self.h - game.BLOCK_SIZE or pt.y < 0:
#            return True
        # hits itself
#        if pt in self.snake[1:]:
#            return True
        
#        return False
        
    def move(self, action):
        pass
        # [straight, right, left]

#        clock_wise = [game.Direction.RIGHT, game.Direction.DOWN, game.Direction.LEFT, game.Direction.UP]
#        idx = clock_wise.index(self.direction)

#        if np.array_equal(action, [1, 0, 0]):
#            new_dir = clock_wise[idx] # no change
#        elif np.array_equal(action, [0, 1, 0]):
#            next_idx = (idx + 1) % 4 # right turn r -> d -> l -> u
#            new_dir = clock_wise[next_idx]
#        else: # [0, 0, 1]
#            next_idx = (idx - 1) % 4 # left turn r -> u -> l -> d   
#            new_dir = clock_wise[next_idx]

#        self.direction = new_dir

#        x = self.head.x
#        y = self.head.y
#        if self.direction == game.Direction.RIGHT:
#            x += game.BLOCK_SIZE
#        elif self.direction == game.Direction.LEFT:
#            x -= game.BLOCK_SIZE
#        elif self.direction == game.Direction.DOWN:
#            y += game.BLOCK_SIZE
#        elif self.direction == game.Direction.UP:
#            y -= game.BLOCK_SIZE
            
#        self.head = Point(x, y)
            
