import pygame
import random
from enum import Enum
from collections import namedtuple
from pygame import Vector2 as vec2
import numpy as np
import game

class Action(Enum):
    THROW = 1
    HIT = 2
    WAIT = 3

class PingPongPlayerAI:
    
    def __init__(self):
        self.pos = vec2(0, 0)
        self.area_center = vec2(0, 0)
        self.area_size = vec2(0, 0)
        self.facing_dir = game.Direction.RIGHT
        self.action = Action.WAIT
        self.reset()

    def set_area(self, center, size):
        self.area_center = center
        self.area_size = size

    def set_player(self, pt, direction):
        self.pos = pt
        self.facing_dir = direction
        
    def reset(self):        
        # init game state
        self.set_player(vec2(0, 0), game.Direction.RIGHT)
        self.pos = vec2(self.area_size.x // 2, self.area_size.y // 2)
        self.action = Action.WAIT
        
        self.score = 0
        self.ball = None
    
    def getArea(self):
        area = pygame.Rect(self.area_center.x - self.area_size.x//2, self.area_center.y - self.area_size.y//2, self.area_size.x, self.area_size.y)
        return area

    def play_step(self, action):
        # 2. move
        self._move(action) # update the head
        self.snake.insert(0, self.head)
        
        # 3. check if game over
        game_reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
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
    
    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.w - game.BLOCK_SIZE or pt.x < 0 or pt.y > self.h - game.BLOCK_SIZE or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True
        
        return False
        
    def _move(self, action):
        # [straight, right, left]

        clock_wise = [game.Direction.RIGHT, game.Direction.DOWN, game.Direction.LEFT, game.Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx] # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4 # right turn r -> d -> l -> u
            new_dir = clock_wise[next_idx]
        else: # [0, 0, 1]
            next_idx = (idx - 1) % 4 # left turn r -> u -> l -> d   
            new_dir = clock_wise[next_idx]

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == game.Direction.RIGHT:
            x += game.BLOCK_SIZE
        elif self.direction == game.Direction.LEFT:
            x -= game.BLOCK_SIZE
        elif self.direction == game.Direction.DOWN:
            y += game.BLOCK_SIZE
        elif self.direction == game.Direction.UP:
            y -= game.BLOCK_SIZE
            
        self.head = Point(x, y)
            
