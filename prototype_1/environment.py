from typing import Dict, Tuple
from collections import defaultdict
from custom_types import Behavior, MTDTechnique
from scipy import stats
from tabulate import tabulate
import numpy as np
import pandas as pd
import os
import random
from data_manager import DataManager

# define MTD - (target Attack) Mapping
# indices corresponding to sequence
actions = (MTDTechnique.CNC_IP_SHUFFLE, MTDTechnique.ROOTKIT_SANITIZER,
           MTDTechnique.RANSOMWARE_DIRTRAP, MTDTechnique.RANSOMWARE_FILE_EXT_HIDE)

supervisor_map: Dict[int, Tuple[Behavior]] = defaultdict(lambda: -1, {
    #MTDTechnique.NO_MTD: (Behavior.NORMAL,),
    0: (Behavior.CNC_BACKDOOR_JAKORITAR, Behavior.CNC_THETICK),
    1: (Behavior.ROOTKIT_BDVL, Behavior.ROOTKIT_BEURK),
    2: (Behavior.RANSOMWARE_POC,),
    3: (Behavior.RANSOMWARE_POC,)
})




# handles the supervised, online-simulation of episodes
class SensorEnvironment:

    def __init__(self, all_data: Dict[Behavior, pd.DataFrame] = None, monitor=None):
        self.data = all_data
        self.monitor = monitor
        self.current_state: pd.DataFrame = None
        self.observation_space_size: int = len(self.data[Behavior.RANSOMWARE_POC].iloc[0])
        self.actions: int = [i for i in range(len(actions))]

    def sample_random_attack_state(self):
        """i.e. for starting state of an episode"""
        rb = random.choice([b for b in Behavior if b != Behavior.NORMAL])
        return self.data[rb].sample()

    def sample_behaviour(self, b: Behavior):
        return self.data[b].sample()

    def step(self, action: int):

        current_behaviour = self.current_state.iloc[0]["attack"]
        if self.monitor is None:
            if current_behaviour in supervisor_map[action]:
                print("correct mtd chosen according to supervisor")
                new_state = self.sample_behaviour(Behavior.NORMAL)
                reward = self.calculate_reward(True)
                isTerminalState = True
            else:
                print("incorrect mtd chosen according to supervisor")
                new_state = self.sample_behaviour(current_behaviour)
                reward = self.calculate_reward(False)
                isTerminalState = False

        else:
            # would integrate a monitoring component here for a live system
            # new_state = self.monitor.get_current_behavior(),
            # but reward would need to be calculated by autoencoder
            reward = None

        return new_state, reward, isTerminalState

    def reset(self):
        self.current_state = self.sample_random_attack_state()
        self.reward = 0
        self.done = False
        return self.current_state




    # TODO: possibly adapt to distinguish between MTDs that are particularly wasteful in case of wrong deployment
    def calculate_reward(self, success):
        """
        if current_behavior == supervisor_map[action]:
        then return positive
        else return negative

        this method can be exchanged for the online/unsupervised RL system with the autoencoder
        """
        if success:
            return 100
        else:
            return -100