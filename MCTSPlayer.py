import copy
import random
import settings

from MCTSAI import MCTSAI
from Player import Player
from utils import Card, Move


class MCTSPlayer(Player):


    def __init__(self, player_num, time, max_moves, weighted, thompson):
        super().__init__(Player.MCTS_AI, player_num)
        self.time = time
        self.max_moves = max_moves
        self.weighted = weighted
        self.thompson = thompson


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


    def decide_move(self, dev_played, board, deck, players, robber, trades_tried, give=None, recieve=None):
        AI = MCTSAI(board, self.time, self.max_moves, players, deck, dev_played, \
            self.player_num, robber, self.weighted, self.thompson, trades_tried, give, recieve)
        board1 = copy.deepcopy(board)
        move = AI.get_play()
        return move


    def choose_trader(self, traders):
        return traders[random.randint(0, len(traders) - 1)]


    def to_string(self):
        return "MCTS"