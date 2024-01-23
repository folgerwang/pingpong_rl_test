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

TABLE_WIDTH = 940
TABLE_HEIGHT = 540
TABLE_INNER_WIDTH = 900
TABLE_INNER_HEIGHT = 500

NET_WIDTH = 10
NET_HEIGHT = TABLE_HEIGHT

BLOCK_SIZE = 20
SPEED = 20

class PingPongGameAI:
    
    def __init__(self, w=DISPLAY_WIDTH, h=DISPLAY_HEIGHT):
        self.w = w
        self.h = h
        self.players = [None, None]
        self.players[0] = player.PingPongPlayerAI()
        self.players[1] = player.PingPongPlayerAI()
        self.ball = ball.PingPongBall()

        self.players[0].action = player.Action.THROW
        self.players[1].action = player.Action.WAIT
        
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('PingPongGame')
        self.clock = pygame.time.Clock()
        self.reset()
        
    def reset(self):        
        # init game state
        self.direction = Direction.RIGHT

        player_max_area_size = vec2((DISPLAY_WIDTH - TABLE_WIDTH)//2, DISPLAY_HEIGHT)
        player_area_center = vec2(player_max_area_size.x // 2, player_max_area_size.y // 2)

        self.players[0].reset()
        player1_pos = player_area_center
        self.players[0].set_area(player_area_center, player_max_area_size)
        self.players[0].set_player(player1_pos, Direction.RIGHT)
        self.players[0].action = player.Action.THROW

        self.players[1].reset()
        player2_area_center = vec2(DISPLAY_WIDTH - player_area_center.x, DISPLAY_HEIGHT - player_area_center.y)
        player2_pos = player2_area_center
        self.players[1].set_area(player2_area_center, player_max_area_size)
        self.players[1].set_player(player2_pos, Direction.LEFT)
        self.players[1].action = player.Action.WAIT

        self.score = 0
        self.ball.reset()
        self.ball.pos = vec3(0, DISPLAY_HEIGHT//2, 0.5)
        self.ball.speed = vec3(1.0, 0.0, 1.0)
        self.frame_iteration = 0
    
    def _place_ball(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE 
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.ball = vec2(x, y)
        
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
            
        # 4. place new food or just move
        if self.head == self.ball:
            self.score += 1
            game_reward = 10
            self._place_ball()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return game_reward, game_over, self.score
    
    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True

        return False
        
    def _update_ui(self):
        self.display.fill(BLACK)

        # draw players.
        pygame.draw.rect(self.display, YELLOW, self.players[0].getArea(), 10)
        pygame.draw.rect(self.display, YELLOW, self.players[1].getArea(), 10)
        pygame.draw.rect(self.display, GREEN, pygame.Rect(self.players[0].pos.x, self.players[0].pos.y, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(self.display, BLUE2, pygame.Rect(self.players[0].pos.x+4, self.players[0].pos.y+4, BLOCK_SIZE-8, BLOCK_SIZE-8))
        pygame.draw.rect(self.display, GREEN, pygame.Rect(self.players[1].pos.x, self.players[1].pos.y, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(self.display, BLUE2, pygame.Rect(self.players[1].pos.x+4, self.players[1].pos.y+4, BLOCK_SIZE-8, BLOCK_SIZE-8))
        
        # draw table.
        table_offset_x = (self.w - TABLE_WIDTH) // 2
        table_offset_y = (self.h - TABLE_HEIGHT) // 2
        table_inner_offset_x = (self.w - TABLE_INNER_WIDTH) // 2
        table_inner_offset_y = (self.h - TABLE_INNER_HEIGHT) // 2
        pygame.draw.rect(self.display, LIGHT_BLUE, pygame.Rect(table_offset_x, table_offset_y, TABLE_WIDTH, TABLE_HEIGHT))
        pygame.draw.rect(self.display, BLUE1, pygame.Rect(table_inner_offset_x, table_inner_offset_y, TABLE_INNER_WIDTH, TABLE_INNER_HEIGHT))

        # draw net.
        net_offset_x = (self.w - NET_WIDTH) // 2
        net_offset_y = (self.h - NET_HEIGHT) // 2
        pygame.draw.rect(self.display, WHITE, pygame.Rect(net_offset_x, net_offset_y, NET_WIDTH, NET_HEIGHT))
        
        # draw ball.
        pygame.draw.circle(self.display, RED, vec2(self.ball.pos.x, self.ball.pos.y), self.ball.pos.z * 12 + 12)
        
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
            
