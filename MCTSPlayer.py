import copy
import random
import settings

from MCTSAI import MCTSAI
from Player import Player
from utils import Card, Move


class MCTSPlayer(Player):


    def __init__(self, player_num, time, weighted, thompson):
        super().__init__(Player.MCTS_AI, player_num)
        self.time = time
        self.weighted = weighted
        self.thompson = thompson

    def decide_move(self, board, deck, players):
        AI = MCTSAI(board, self.time, players, deck, \
            self.player_num, self.weighted, self.thompson)
        #board1 = copy.deepcopy(board)
        move = AI.get_play()
        #print('move decided')
        return move

    def to_string(self):
        return "MCTS"