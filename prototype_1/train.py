from typing import Dict
from collections import defaultdict
from custom_types import MTDTechnique, Behavior

from collections import defaultdict
from custom_types import MTDTechnique, Behavior
from data_manager import DataManager
from prototype_1.environment import SensorEnvironment
from prototype_1.agent import Agent, DeepQNetwork
from time import time
import numpy as np
import random

# Hyperparams
GAMMA = 0.99
BATCH_SIZE = 100
BUFFER_SIZE = 50000
MIN_REPLAY_SIZE = 100
EPSILON_START = 1.0
EPSILON_END = 0.02
TARGET_UPDATE_FREQ = 100
LEARNING_RATE = 0.00001
N_EPISODES = 100000
LOG_FREQ = 100



if __name__ == '__main__':
    start = time()
    # read in all data for a simulated, supervised environment to sample from
    env = SensorEnvironment(DataManager.parse_all_behavior_data())

    agent = Agent(input_dims=env.observation_space_size, n_actions=len(env.actions),
                  batch_size=BATCH_SIZE, lr=LEARNING_RATE, gamma=GAMMA, epsilon=EPSILON_START, eps_end=EPSILON_END)
    episode_returns, eps_history = [], []


    # initialize memory replay buffer (randomly)
    obs = env.reset()
    for _ in range(MIN_REPLAY_SIZE):
        action = random.choice(env.actions)

        new_obs, reward, done = env.step(action)
        transition = (obs[:,:-1], action, reward, new_obs[:,:-1], done)
        agent.replay_buffer.append(transition)

        obs = new_obs
        if done:
            obs = env.reset()


    # main training
    step = 0
    for i in range(N_EPISODES):
        episode_return = 0
        done = False
        obs = env.reset()
        while not done:
            action = agent.choose_action(obs[:,:-1])

            new_obs, reward, done = env.step(action)
            episode_return += reward
            agent.replay_buffer.append((obs[:,:-1], action, reward,
                                   new_obs[:,:-1], done))
            agent.reward_buffer.append(reward)

            agent.learn()
            obs = new_obs

            # update target network
            step += 1
            if step % TARGET_UPDATE_FREQ == 0:
                agent.update_target_network()

            if step % LOG_FREQ == 0:
                print("Episode: ", i, "Step: ", step, ", Avg Reward: ", np.mean(agent.reward_buffer), "epsilon: ", agent.epsilon)


        episode_returns.append(episode_return)

    end = time()
    print("Total training time: ", end - start)
        #print(episode_return)

    #     eps_history.append(agent.epsilon)
    #
    #     avg_episode_return = np.mean(episode_returns[-100:])
    #
    #     print('episode ', i, 'episode_return %.2f' % episode_return,
    #           'average episode_return %.2f' % avg_episode_return,
    #           'epsilon %.2f' % agent.epsilon)
    # x = [i + 1 for i in range(n_games)]
    # filename = 'lunar_lander.png'
    # #plotLearning(x, episode_returns, eps_history, filename)
