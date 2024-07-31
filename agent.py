import torch
import random
import numpy as np
from collections import deque
from agariomodel import AgarGame
import matplotlib
import os
import asyncio
from nn_model import QTrainer, Linear_QNet
import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def plot(scores, mean_scores):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training')
    plt.xlabel('Number of Games')
    plt.ylabel('Score/Mean Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    plt.show(block=False)
    plt.pause(.1)

MAX_MEMORY = 100000
BATCH_SIZE = 1000
LEARNING_RATE = 0.001


class Agent:
    def __init__(self) -> None:
        self.n_games = 0
        self.epsilon = 0  # randomness
        self.gamma = 0.2  # discount_rate < 1
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = torch.load("./onefoodxy.pth")
        self.trainer = QTrainer(self.model, LEARNING_RATE, self.gamma)

    def get_state(self, game: AgarGame):
        position = game.pos
        wall_right, wall_left, wall_up, wall_down = 0,0,0,0
        if position[0] >= game.w - 30:
            wall_right = 1

        if position[0] == 30:
            wall_left = 1

        if position[1] == game.h - 30:
            wall_down = 1

        if position[1] == 30:
            wall_up = 1
        
        d_to_food = ((game.pos[0] - game.food[0])**2 + (game.pos[1] - game.food[1])**2)**0.5
        state = [round(game.pos[0]/game.w,3), round(game.pos[1]/game.h, 3), round(game.food[1]/game.h, 3), round(game.food[0]/game.w, 3), wall_right, wall_left, wall_up, wall_down, d_to_food/800]  #
        game.state = state
        state = np.array(state, dtype=float)
        return state

    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            sample = random.sample(self.memory, BATCH_SIZE)
        else:
            sample = self.memory
        states, actions, rewards, next_states, game_overs = zip(*sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)

    def train_short_memory(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def get_action(self, state):
        # random: tradeoff between exploration / exploitation
        self.epsilon = 0 #Return to 40 - ngames
        final_move = [0,0,0,0]
        if random.randint(0, 100) < self.epsilon:
            move = random.randint(0, 3)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

def train():
    scores = []
    mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = AgarGame()
    while True:
        # get old_state
        old_state = agent.get_state(game)

        # get move
        final_move = agent.get_action(old_state)

        # Perform move and get new state
        reward, game_over, score, = game.play_step(final_move)
        new_state = agent.get_state(game)

        # train short memory
        agent.train_short_memory(old_state, final_move, reward, new_state, game_over)

        # remember
        agent.remember(old_state, final_move, reward, new_state, game_over)

        if game_over:
            # train_long_memory, plot results
            game.reset()
            game.n += 1
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print(f"Game: {agent.n_games} Score: {score} Record: {record}")
            scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            mean_scores.append(mean_score)
            plot(scores, mean_scores)


train()
