import copy
import random
import settings

from Player import Player
from utils import Card, Move


class RandomPlayer(Player):


    def __init__(self, player_num):
        super(RandomPlayer, self).__init__(Player.RANDOM_AI, player_num)

    def decide_move(self, board, deck, players):
        possible_moves = self.get_legal_moves(board, deck, 0)
        # We should choose a move randomly from the set of possible moves!
        return possible_moves[random.randint(0, len(possible_moves) - 1)]

    def to_string(self):
        return "Random"