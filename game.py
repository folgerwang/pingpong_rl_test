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

FIELD_WIDTH_FEET = 16 # 16 feet
FIELD_HEIGHT_FEET = FIELD_WIDTH_FEET * DISPLAY_ASPECT # 9 feet

TABLE_LONGTH_FEET = 9 # 9 feet
TABLE_WIDTH_FEET = 5 # 5 feet
TABLE_HEIGHT_FEET = 2.5 # 2.5 feet

FOOT_TO_METER = 0.3048

FIELD_WIDTH = FIELD_WIDTH_FEET * FOOT_TO_METER
FIELD_HEIGHT = FIELD_HEIGHT_FEET * FOOT_TO_METER

TABLE_LONGTH = TABLE_LONGTH_FEET * FOOT_TO_METER
TABLE_WIDTH = TABLE_WIDTH_FEET * FOOT_TO_METER
TABLE_HEIGHT = TABLE_HEIGHT_FEET * FOOT_TO_METER

#TABLE_LONGTH_PIXEL = int(TABLE_LONGTH * METER_TO_PIXEL)
#TABLE_WIDTH_PIXEL = int(TABLE_WIDTH * METER_TO_PIXEL)
#TABLE_HEIGHT_PIXEL = int(TABLE_HEIGHT * METER_TO_PIXEL)

#NET_WIDTH_PIXEL = 10
#NET_LONGTH_PIXEL = TABLE_WIDTH_PIXEL

BLOCK_SIZE = 20
SPEED = 20

class PingPongGameAI:
    
    def __init__(self, w=DISPLAY_WIDTH, h=DISPLAY_HEIGHT):
        self.display_size = vec2(w, h)
        self.to_display_scale = vec2(w/FIELD_WIDTH, h/FIELD_HEIGHT)
        self.players = [None, None]
        self.players[0] = player.PingPongPlayerAI()
        self.players[1] = player.PingPongPlayerAI()
        self.ball = ball.PingPongBall()

        self.players[0].action = player.Action.THROW
        self.players[1].action = player.Action.WAIT
        
        # init display
        self.display = pygame.display.set_mode(self.display_size)
        pygame.display.set_caption('PingPongGame')
        self.clock = pygame.time.Clock()
        self.reset()
    
    def to_display(self, pos):
        return pos * self.to_display_scale

    def get_table_size_pixel(self):
        return vec2(TABLE_LONGTH, TABLE_WIDTH) * METER_TO_PIXEL
        
    def reset(self):        
        # init game state
        self.direction = Direction.RIGHT

        player_max_area_size = vec2((FIELD_WIDTH - TABLE_LONGTH)/2, FIELD_HEIGHT)
        player_area_center = vec2(player_max_area_size.x / 2, player_max_area_size.y / 2)

        self.players[0].reset()
        player1_pos = player_area_center - vec2(FIELD_WIDTH / 2, FIELD_HEIGHT / 2)
        self.players[0].set_area(player_area_center, player_max_area_size)
        self.players[0].set_player(player1_pos, Direction.RIGHT)
        self.players[0].action = player.Action.THROW

        self.players[1].reset()
        player2_area_center = vec2(FIELD_WIDTH - player_area_center.x, FIELD_HEIGHT)
        player2_pos = player2_area_center - vec2(FIELD_WIDTH / 2, FIELD_HEIGHT / 2)
        self.players[1].set_area(player2_area_center, player_max_area_size)
        self.players[1].set_player(player2_pos, Direction.LEFT)
        self.players[1].action = player.Action.WAIT

        self.score = 0
        self.ball.reset()
        self.ball.pos = vec3((DISPLAY_WIDTH - (TABLE_LONGTH_PIXEL - 40))//2, DISPLAY_HEIGHT//2, 50.0)
        self.ball.speed = vec3(10.0, 0.0, 10.0)
        self.frame_iteration = 0
    
    def play_step(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. throw up ball.
        self.ball.play_step(1.0/30.0)

        # 2. move
        self._move(action) # update the head
        
        # 3. check if game over
        game_reward = 0
        game_over = False
#        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
#           game_over = True
#          game_reward = -10
#            return game_reward, game_over, self.score
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return game_reward, game_over, self.score
    
    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.display_size.x - BLOCK_SIZE or pt.x < 0 or pt.y > self.display_size.y - BLOCK_SIZE or pt.y < 0:
            return True

        return False
        
    def _update_ui(self):
        self.display.fill(BLACK)

        # draw players.
        pygame.draw.rect(self.display, YELLOW, self.players[0].getArea(), 10)
        pygame.draw.rect(self.display, YELLOW, self.players[1].getArea(), 10)
        pygame.draw.rect(self.display, GREEN, pygame.Rect(self.players[0].pos.xy, vec2(BLOCK_SIZE)))
        pygame.draw.rect(self.display, BLUE2, pygame.Rect(self.players[0].pos.xy+vec2(4), vec2(BLOCK_SIZE)-vec2(8)))
        pygame.draw.rect(self.display, GREEN, pygame.Rect(self.players[1].pos.xy, vec2(BLOCK_SIZE)))
        pygame.draw.rect(self.display, BLUE2, pygame.Rect(self.players[1].pos.xy+vec2(4), vec2(BLOCK_SIZE)-vec2(8)))
        
        # draw table.
        table_size_pixel = self.get_table_size_pixel()
        table_offset = (self.display_size - table_size_pixel) // 2
        table_inner_offset = (self.display_size - (table_size_pixel - vec2(40))) // 2
        pygame.draw.rect(self.display, LIGHT_BLUE, pygame.Rect(table_offset, table_size_pixel))
        pygame.draw.rect(self.display, BLUE1, pygame.Rect(table_inner_offset, table_size_pixel - vec2(40)))

        # draw net.
        net_size = vec2(NET_WIDTH_PIXEL, NET_LONGTH_PIXEL)
        net_offset = (self.display_size - net_size) // 2
        pygame.draw.rect(self.display, WHITE, pygame.Rect(net_offset, net_size))
        
        # draw ball.
        pygame.draw.circle(self.display, RED, self.ball.pos.xy, self.ball.pos.z)
        
        text = font.render("Game : " + str(self.frame_iteration) + "; Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()
        
    def _move(self, action):
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
            
