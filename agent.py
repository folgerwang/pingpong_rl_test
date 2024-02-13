import torch
import random
import numpy as np
from collections import deque
from game import PingPongGameAI
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
        self.model = Linear_QNet(18, 256, 12) # neural net
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma) # optimiser
        self.target_model = None # this is what we .predict against every step
        self.target_trainer = None # optimiser
        self.target_update_counter = 0 # every 10k steps we update target model
        
    def getState(self, game, index):
        state = [
            # Danger straight
            game.players[0].pad_pos.x,
            game.players[0].pad_pos.y,
            game.players[0].pad_pos.z,
            game.players[0].pad_dir.x,
            game.players[0].pad_dir.y,
            game.players[0].pad_dir.z,
            game.players[1].pad_pos.x,
            game.players[1].pad_pos.y,
            game.players[1].pad_pos.z,
            game.players[1].pad_dir.x,
            game.players[1].pad_dir.y,
            game.players[1].pad_dir.z,
            game.ball.pos.x,
            game.ball.pos.y,
            game.ball.pos.z,
            game.ball.speed.x,
            game.ball.speed.y,
            game.ball.speed.z
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
        state0 = torch.tensor(state, dtype=torch.float)
        prediction = self.model(state0)
        
        return prediction

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
    