import random
from Player import Player
from NNet import NNetWrapper as nn
import StateToFeatures
import numpy as np
import pickle

class NNetPlayer(Player):
    def __init__(self, player_num):
        super(NNetPlayer, self).__init__(Player.NNET, player_num)

        # TODO: edit this to load the best weights
        self.nnet = nn()
        self.move_to_index = pickle.load(open("AllPossibleActionDict.p", "rb"))
        self.move_array = pickle.load(open("AllPossibleActionVector.p", "rb"))

    def decide_move(self, board, deck, players, nn):
    	canonicalBoard = StateToFeatures.board_to_vector(board, deck)
    	Ps, value = self.nnet.predict(canonicalBoard)
    	valids = StateToFeatures.possible_actions_to_vector(self.get_legal_moves(board, deck), \
            self.player_num, len(players), self.move_to_index)
    	Ps = Ps * valids
    	action = np.argmax(Ps)
    	return StateToFeatures.action_to_move(action, self.move_array, self, len(board.players), deck)

    def to_string(self):
        return "NNet"

