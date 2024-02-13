import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np
from pygame import Vector2 as vec2
from pygame import Vector3 as vec3
import game

GRAVITY_RATE = -9.8
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

    def solveQuadratic(self, a, b, c, delta_t):
        d = b**2 - 4*a*c
        solution = None
        if d < 0:
            solution = None
        elif d == 0:
            t = (-b + np.sqrt(d)) / (2 * a)
            if (t > 0 and t < delta_t):
                solution = t
        else:
            t0 = (-b + np.sqrt(d)) / (2 * a)
            t1 = (-b - np.sqrt(d)) / (2 * a)
            if (t0 > 0 and t0 < delta_t):
                solution = t0
            if (t1 > 0 and t1 < delta_t):
                if not solution or solution and t1 < solution: 
                    solution = t1
        return solution
        
    def getTargetPosAndSpeed(self, delta_t):
        target_pos_xy = self.pos.xy + self.speed.xy * delta_t
        target_pos_z = self.pos.z + (self.speed.z + 0.5 * GRAVITY_RATE * delta_t) * delta_t
        target_speed_xy = self.speed.xy + self.speed.xy * AIR_FRACTION * delta_t
        target_speed_z = self.speed.z + GRAVITY_RATE * delta_t
        return target_pos_xy, target_pos_z, target_speed_xy, target_speed_z
    
    def insideTable(self, collision_xy, table_center, table_size):
        return (collision_xy.x > table_center.x - table_size.x / 2 and collision_xy.x < table_center.x + table_size.x / 2 and
                collision_xy.y > table_center.y - table_size.y / 2 and collision_xy.y < table_center.y + table_size.y / 2)
    
    def insideNet(self, collision_y, collision_z, net_center, net_size, table_height, net_height):
        return (collision_y > net_center.y - net_size.y / 2 and collision_y < net_center.y + net_size.y / 2 and
                collision_z > table_height and collision_z < table_height + net_height)
    
    def boucingOnTable(self, table_center, table_size, table_height, remaining_t) :
        solution = self.solveQuadratic(GRAVITY_RATE / 2, self.speed.z, self.pos.z - table_height, remaining_t)
        if solution:
            collision_pos_xy, collision_pos_z, collision_speed_xy, collision_speed_z = self.getTargetPosAndSpeed(solution)
            if self.insideTable(collision_pos_xy, table_center, table_size):
                self.pos = vec3(collision_pos_xy.x, collision_pos_xy.y, collision_pos_z)
                self.speed = vec3(collision_speed_xy.x, collision_speed_xy.y, -collision_speed_z)
                return remaining_t - solution
            
        return remaining_t
    
    def boucingOnNet(self, net_center, net_size, table_height, net_height, remaining_t) :
        solution = (net_center.x - self.pos.x) / self.speed.x
        collision_pos_xy, collision_pos_z, collision_speed_xy, collision_speed_z = self.getTargetPosAndSpeed(solution)
        if self.insideNet(collision_pos_xy.y, collision_pos_z, net_center, net_size, table_height, net_height):
            self.pos = vec3(collision_pos_xy.x, collision_pos_xy.y, collision_pos_z)
            self.speed = vec3(-collision_speed_xy.x, collision_speed_xy.y, collision_speed_z)
            return remaining_t - solution
            
        return remaining_t
    
    def bouncingOnGround(self, remaining_t):
        solution = self.solveQuadratic(GRAVITY_RATE / 2, self.speed.z, self.pos.z, remaining_t)
        if solution:
            collision_pos_xy, collision_pos_z, collision_speed_xy, collision_speed_z = self.getTargetPosAndSpeed(solution)
            self.pos = vec3(collision_pos_xy.x, collision_pos_xy.y, collision_pos_z)
            self.speed = vec3(collision_speed_xy.x, collision_speed_xy.y, -collision_speed_z)
            return remaining_t - solution
            
        return remaining_t
    

    def playStep(self, delta_t, table_center, table_size, table_height, net_center, net_size, net_height):
        remaining_t = delta_t
        target_pos_xy, target_pos_z, target_speed_xy, target_speed_z = self.getTargetPosAndSpeed(remaining_t)

        while remaining_t > 0 :
            collided = False
            # ball is above the table, so first check if collision with net
            if self.pos.z > table_height :
                if (target_pos_xy.x < net_center.x and self.pos.x > net_center.x or
                    target_pos_xy.x > net_center.x and self.pos.x < net_center.x): # ball is possible collision with net
                    updated_remaining_t = self.boucingOnNet(net_center, net_size, table_height, net_height, remaining_t)
                    if updated_remaining_t != remaining_t:
                        print("bouncing on net")
                        remaining_t = updated_remaining_t
                        target_pos_xy, target_pos_z, target_speed_xy, target_speed_z = self.getTargetPosAndSpeed(remaining_t)
                        collided = True

            # ball is passing through the table, possible collision with table
            if (target_pos_z < table_height and self.pos.z > table_height):
                updated_remaining_t = self.boucingOnTable(table_center, table_size, table_height, remaining_t)
                if updated_remaining_t != remaining_t:
                    print("bouncing on table")
                    remaining_t = updated_remaining_t
                    target_pos_xy, target_pos_z, target_speed_xy, target_speed_z = self.getTargetPosAndSpeed(remaining_t)
                    collided = True

            # ball came from bottom up, possible collision with table
            if (target_pos_z > table_height and self.pos.z < table_height):
                updated_remaining_t = self.boucingOnTable(table_center, table_size, table_height, remaining_t)
                if updated_remaining_t != remaining_t:
                    print("bouncing on to table")
                    remaining_t = updated_remaining_t
                    target_pos_xy, target_pos_z, target_speed_xy, target_speed_z = self.getTargetPosAndSpeed(remaining_t)
                    collided = True

            # ball is passing through the ground, will collision with ground
            if target_pos_z < 0:
                updated_remaining_t = self.bouncingOnGround(remaining_t)
                if updated_remaining_t != remaining_t:
                    print("bouncing on ground")
                    remaining_t = updated_remaining_t
                    target_pos_xy, target_pos_z, target_speed_xy, target_speed_z = self.getTargetPosAndSpeed(remaining_t)
                    collided = True

            if not collided :
                remaining_t = 0

        self.pos = vec3(target_pos_xy.x, target_pos_xy.y, target_pos_z)
        self.speed = vec3(target_speed_xy.x, target_speed_xy.y, target_speed_z)


    def isCollision(self, pt=None):
        pass
        
    def move(self, action):
        pass
            
