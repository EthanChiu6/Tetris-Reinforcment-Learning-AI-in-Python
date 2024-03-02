import torch
import random
import numpy as np
from collections import deque
from game import tetrisAI, block
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 10000
BATCH_SIZE = 512
LR = 0.001

class Agent:
    
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 #randomness parameter
        self.gamma = 0.95 #discount rate
        self.memory = deque(maxlen=MAX_MEMORY) #if memory exceeded will automatically call popleft()
        self.model = Linear_QNet(4, 32, 2) #adjusted input and output based on tetris
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
    
    def get_state(self, game):
        state = game.get_state()
        
        return np.array(state, dtype = int)
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) #popleft if max memory is reached, double bracket --> stored as a single tuple
    
    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) #list of tuples
        else:
            mini_sample = self.memory
            
        for state, action, reward, next_state, done in mini_sample:
            self.trainer.train_step(state, action, reward, next_state, done)
            
    
    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)
    
    def get_action(self, state):
        # Random moves: tradeoff exploration / exploitation in deep learning
        self.epsilon = 100 - self.n_games
        final_move = [0, 0]

        if random.randint(0, 200) < self.epsilon:
            # Random exploration
            move_type = random.randint(0, 1)
            if move_type == 0:
                final_move[0] = random.randint(-1, 1)  # Move left, right, or stay
            else:
                final_move[1] = random.randint(0, 1)   # Rotate 0 or 1 time
        else:
            # Exploitation using model prediction
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()

            # Convert move to x and rotation
            if move == 0:
                final_move[0] = -1  # Move left
            elif move == 1:
                final_move[0] = 1   # Move right
            elif move == 2:
                final_move[1] = 1   # Rotate

        return final_move
                

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = tetrisAI(300, 660)
    while True:
        # get old state
        state_old = agent.get_state(game)
        
        # get move
        final_move = agent.get_action(state_old)
        
        # perform move and get new state
        if agent.n_games <= 1500:
            reward, done, score = game.play_step(final_move[0], final_move[1], 500)
        else:
            reward, done, score = game.play_step(final_move[0], final_move[1], 50)
        state_new = agent.get_state(game)
        
        # train short memory 
        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        
        # remember
        agent.remember(state_old, final_move, reward, state_new, done)
        
        
        if done:
            # train long memory / replay memory (experienced replay), plot result
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()
            
            if score > record:
                record = score
                agent.model.save()
                    
            print('Game', agent.n_games, 'Score', score, 'Record:', record)
            
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores) 
        

if __name__ == '__main__':
    train()