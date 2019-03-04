import random
from MCTSNN import MCTSNN
from Player import Player
import pickle
import StateToFeatures
import numpy as np

class MCTSNNPlayer(Player):
    def __init__(self, player_num, num_simulations):
        super(MCTSNNPlayer, self).__init__(Player.MCTSNN_AI, player_num)
        self.num_simulations = num_simulations
        self.move_to_index = pickle.load(open("AllPossibleActionDict.p", "rb"))
        self.move_array = pickle.load(open("AllPossibleActionVector.p", "rb"))
        self.avg_cycles_per_move = [1, 1]
        self.avg_legal_moves = [1, 1]

    def decide_move(self, board, deck, players, nn):
        if self.random:
            possible_moves = self.get_legal_moves(board, deck)
            # We should choose a move randomly from the set of possible moves!
            return possible_moves[random.randint(0, len(possible_moves) - 1)]
        AI = MCTSNN(board, self.num_simulations, deck, self.player_num, nn, self.move_to_index)
        action = np.argmax(AI.getActionProb(temp=0))
        move = StateToFeatures.action_to_move(action, self.move_array, self, len(board.players), deck)
        return move

    # We put this in a helper function to use it for training
    def getActionProb(self, AI):
        return AI.getActionProb()

    def to_string(self):
        return "MCTSNN"