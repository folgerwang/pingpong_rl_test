import pygame
import random
from enum import Enum
from collections import namedtuple
from pygame import Vector2 as vec2
from pygame import Vector3 as vec3
import numpy as np
import player
import ball

pygame.init()
font = pygame.font.Font('arial.ttf', 25)
#font = pygame.font.SysFont('arial', 25)

# reset
# reward
# play(action) -> direction
# game_iteration
# is_collision


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    
# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
LIGHT_BLUE = (100, 100, 150)
BLUE1 = (100, 100, 255)
BLUE2 = (0, 100, 255)
GREEN = (0, 255, 0)
BLACK = (0,0,0)
YELLOW = (255, 255, 0)

DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720

DISPLAY_ASPECT = DISPLAY_HEIGHT / DISPLAY_WIDTH

FIELD_LONGTH_FEET = 16 # 16 feet
FIELD_WIDTH_FEET = FIELD_LONGTH_FEET * DISPLAY_ASPECT # 9 feet

TABLE_LONGTH_FEET = 9 # 9 feet
TABLE_WIDTH_FEET = 5 # 5 feet
TABLE_HEIGHT_FEET = 2.5 # 2.5 feet

NET_WIDTH_FEET = 0.1 # 0.1 feet
NET_HEIGHT_FEET = 0.5 # 0.5 feet

FOOT_TO_METER = 0.3048

FIELD_LONGTH = FIELD_LONGTH_FEET * FOOT_TO_METER
FIELD_WIDTH = FIELD_WIDTH_FEET * FOOT_TO_METER

TABLE_LONGTH = TABLE_LONGTH_FEET * FOOT_TO_METER
TABLE_WIDTH = TABLE_WIDTH_FEET * FOOT_TO_METER
TABLE_HEIGHT = TABLE_HEIGHT_FEET * FOOT_TO_METER

NET_WIDTH = NET_WIDTH_FEET * FOOT_TO_METER
NET_LONGTH = TABLE_WIDTH
NET_HEIGHT = NET_HEIGHT_FEET * FOOT_TO_METER

BLOCK_SIZE = 20
SPEED = 20

class PingPongGameAI:
    
    def __init__(self, w=DISPLAY_WIDTH, h=DISPLAY_HEIGHT):
        self.display_size_ = vec2(w, h)
        self.to_display_ = w/FIELD_LONGTH
        self.field_size_ = vec2(FIELD_LONGTH, FIELD_WIDTH)
        self.table_size_ = vec2(TABLE_LONGTH, TABLE_WIDTH)
        self.net_size_ = vec2(NET_WIDTH, NET_LONGTH)
        self.half_field_size_ = self.field_size_ / 2
        self.player_area_size_ = vec2((self.field_size_.x - self.table_size_.x) / 2, self.field_size_.y)
        self.field_origin_ = -self.half_field_size_
        self.table_origin_ = -self.table_size_ / 2

        self.players = [None, None]
        self.players[0] = player.PingPongPlayerAI()
        self.players[1] = player.PingPongPlayerAI()
        self.ball = ball.PingPongBall()

        self.players[0].action = player.Action.THROW
        self.players[1].action = player.Action.WAIT
        
        # init display
        self.display = pygame.display.set_mode(self.display_size_)
        pygame.display.set_caption('PingPongGame')
        self.clock = pygame.time.Clock()
        self.reset()
    
    def toScreenCoord(self, pos):
        return (pos + self.half_field_size_) * self.to_display_

    def toScreen(self, size):
        return size * self.to_display_

    def reset(self):        
        # init game state
        self.direction = Direction.RIGHT

        player_distance_to_center = (self.table_size_.x + self.player_area_size_.x) / 2

        self.players[0].reset()
        self.players[0].setArea(vec2(-player_distance_to_center, 0.0), self.player_area_size_)
        self.players[0].setPlayer(vec2(-player_distance_to_center, 0.0), Direction.RIGHT)
        self.players[0].action = player.Action.THROW

        self.players[1].reset()
        self.players[1].setArea(vec2(player_distance_to_center, 0.0), self.player_area_size_)
        self.players[1].setPlayer(vec2(player_distance_to_center, 0.0), Direction.LEFT)
        self.players[1].action = player.Action.WAIT

        self.score = 0
        self.ball.reset()
        self.ball.pos = vec3(-player_distance_to_center + 0.1, 0, 1.0)
        self.ball.speed = vec3(0.1, 0.0, 0.1)
        self.frame_iteration = 0
    
    def playStep(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. throw up ball.
        self.ball.playStep(1.0/30.0)

        # 2. move
        self.move(action) # update the head
        
        # 3. check if game over
        game_reward = 0
        game_over = False
#        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
#           game_over = True
#          game_reward = -10
#            return game_reward, game_over, self.score
        
        # 5. update ui and clock
        self.updateUI()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return game_reward, game_over, self.score
    
    def isCollision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.display_size_.x - BLOCK_SIZE or pt.x < 0 or pt.y > self.display_size_.y - BLOCK_SIZE or pt.y < 0:
            return True

        return False
        
    def drawRect(self, color, center, size, edge=0):
        pygame.draw.rect(self.display, color, pygame.Rect(self.toScreenCoord(center - size / 2), self.toScreen(size)), edge)

    def updateUI(self):
        self.display.fill(BLACK)

        # draw players.
        self.players[0].drawPlayableArea(self)
        self.players[1].drawPlayableArea(self)
        self.players[0].drawPlayerIcon(self)
        self.players[1].drawPlayerIcon(self)
        
        # draw table.
        self.drawRect(LIGHT_BLUE, vec2(0, 0), self.table_size_)
        self.drawRect(BLUE1, vec2(0, 0), self.table_size_ - vec2(0.1))

        # draw net.
        self.drawRect(WHITE, vec2(0, 0), self.net_size_)


        #net_size = vec2(NET_WIDTH_PIXEL, NET_LONGTH_PIXEL)
        #net_offset = (self.display_size - net_size) // 2
        #pygame.draw.rect(self.display, WHITE, pygame.Rect(net_offset, net_size))
        
        # draw ball.
        #pygame.draw.circle(self.display, RED, self.ball.pos.xy, self.ball.pos.z)
        
        text = font.render("Game : " + str(self.frame_iteration) + "; Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()
        
    def move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
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

        x = self.players[0].pos.x
        y = self.players[0].pos.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
            
        self.head = vec2(x, y)
            
