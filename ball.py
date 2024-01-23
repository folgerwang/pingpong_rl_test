import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np
from pygame import Vector2 as vec2
from pygame import Vector3 as vec3
import game

GRAVITY = -9.8
AIR_FRACTION = -0.001

class PingPongBall:
    
    def __init__(self):
        self.pos = vec3(0, 0, 0)
        self.speed = vec3(0, 0, 0)
        self.reset()

    def reset(self):
        pass

    def set(self, pos, speed):        
        self.pos = pos
        self.speed = speed
    
    def play_step(self, delta_t):
        new_pos_x = self.pos.x + self.speed.x * delta_t
        new_pos_y = self.pos.y + self.speed.y * delta_t
        new_pos_z = self.pos.z + (self.speed.z + 0.5 * GRAVITY * delta_t) * delta_t
        self.pos = vec3(new_pos_x, new_pos_y, new_pos_z)
        new_speed_z = self.speed.z + GRAVITY * delta_t
        new_speed_x = self.speed.x + self.speed.x * AIR_FRACTION * delta_t
        new_speed_y = self.speed.y + self.speed.y * AIR_FRACTION * delta_t
        self.speed = vec3(new_speed_x, new_speed_y, new_speed_z)

        print(self.pos)
        print(self.speed)
        pass
    
    def is_collision(self, pt=None):
        pass
        
    def _move(self, action):
        pass
            
