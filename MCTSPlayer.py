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
        AI = MCTSAI(board, self.time, players, deck, 
            board.active_player.player_num, 
            self.player_num, self.weighted, self.thompson)
        move = AI.get_play()
        return move

    def to_string(self):
        return "MCTS"