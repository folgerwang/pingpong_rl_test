import torch
import random
import numpy as np
from collections import deque
from game import PingPongGameAI, Direction
from model import Linear_QNet, QTrainer
from pygame import Vector2 as vec2
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(11, 256, 3) # neural net
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma) # optimiser
        self.target_model = None # this is what we .predict against every step
        self.target_trainer = None # optimiser
        self.target_update_counter = 0 # every 10k steps we update target model
        
    def getState(self, game, index):
        BLOCK_SIZE = 10
        head = game.players[index].pos
        point_l = vec2(head.x - BLOCK_SIZE, head.y)
        point_r = vec2(head.x + BLOCK_SIZE, head.y)
        point_u = vec2(head.x, head.y - BLOCK_SIZE)
        point_d = vec2(head.x, head.y + BLOCK_SIZE)

        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and game.isCollision(point_r)) or
            (dir_l and game.isCollision(point_l)) or
            (dir_u and game.isCollision(point_u)) or
            (dir_d and game.isCollision(point_d)),
        
            # Danger right
            (dir_u and game.isCollision(point_r)) or
            (dir_d and game.isCollision(point_l)) or
            (dir_l and game.isCollision(point_u)) or
            (dir_r and game.isCollision(point_d)),

            # Danger left
            (dir_d and game.isCollision(point_r)) or
            (dir_u and game.isCollision(point_l)) or
            (dir_r and game.isCollision(point_u)) or
            (dir_l and game.isCollision(point_d)),

            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # Food location
            game.ball.pos.x < head.x,  # food left
            game.ball.pos.x > head.x,  # food right
            game.ball.pos.y < head.y,  # food up
            game.ball.pos.y > head.y  # food down
        ]

        return np.array(state, dtype=int)
    

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def trainLongMemory(self):
        if len(self.memory) > BATCH_SIZE:
            # sample a random batch from memory
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory
        
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.trainStep(states, actions, rewards, next_states, dones)

    def trainShortMemory(self, state, action, reward, next_state, done):
        self.trainer.trainStep(state, action, reward, next_state, done)

    def getAction(self, state):
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        
        return final_move

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = PingPongGameAI()
    while True:
        # get old state
        
        state_old = agent.getState(game, 0)
        
        # get move
        final_move = agent.getAction(state_old)
        
        # perform move and get new state
        reward, done, score = game.playStep(final_move)
        state_new = agent.getState(game, 0)
        
        # train short memory
        agent.trainShortMemory(state_old, final_move, reward, state_new, done)
        
        # remember
        agent.remember(state_old, final_move, reward, state_new, done)
        
        if done:
            # train long memory, plot result
            game.reset()
            agent.n_games += 1
            agent.trainLongMemory()
            
            if score > record:
                record = score
                #agent.model.save()
            
            print('Game', agent.n_games, 'Score', score, 'Record:', record)
            
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

if __name__ == '__main__':
    train()
    