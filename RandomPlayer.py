import copy
import random
import settings

from Player import Player
from utils import Card, Move


class RandomPlayer(Player):


    def __init__(self, player_num):
        super().__init__(Player.RANDOM_AI, player_num)


    def choose_spot(self, board, idx):
        legal_settlement = False
        legal_road = False

        while not legal_settlement:

            # This may yield coordinates that are not valid
            loc = (random.randint(0, 11), random.randint(0, 5))

            legal_settlement = self.can_build_settlement(loc, board)

        # Add the settlement to the board and update player fields
        super().add_settlement(board, loc, idx)

        # Choose where to play a road
        while not legal_road:

            # Choose from set of roads coming from settlement; any should work
            possible_sinks = state.available_roads
            sink = possible_sinks[random.randint(0, len(possible_sinks) - 1)]
            move = (loc, sink)

            legal_road = self.can_build_road(move, board)

        # build the road
        super().add_road(board, move)


    def decide_move(self, dev_played, board, deck, players, robber, trades_tried):
        possible_moves = self.get_legal_moves(board, deck, dev_played, robber, 0, trades_tried)
        #print(possible_moves[0].move_type)
        # We should choose a move randomly from the set of possible moves!
        return possible_moves[random.randint(0, len(possible_moves) - 1)]


    def choose_trader(self, traders):
        return traders[random.randint(0, len(traders) - 1)]


    def to_string(self):
        return "Random"