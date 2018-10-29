import copy
import random
import settings

from MCTSAI import MCTSAI
from Player import Player
from utils import Card


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


    # A helper function for moving the robber in the case of rolling a 7
    def move_robber(self, board, spot, victim):
        while True:
            if board.robber != (2,0):
                spots.remove(board.robber)
            spot = spots[random.randint(0, len(spots) - 1)]
            invalid = self.make_move(7, board, None, (spot, victim))
            if invalid == 1:
                return


    def choose_victim(self, board, move):
        victim = None

        # Determine the players adjacent to the robber
        possible_players = [p for p in board.players_adjacent_to_hex(move.coord) if p is not self]

        # Get a list of the player numbers
        player_nums = [p.player_num for p in possible_players]

        if len(possible_players) > 0:
            victim = possible_players[random.randint(0, len(possible_players) - 1)]
        return victim


    def choose_robber_position(self):
        spots = [(4, 1), (2, 1), (3, 3), (1, 0), (2, 3), (1, 2), (4, 0), \
        (1, 1), (4, 2), (2, 4), (3, 0), (0, 2), (3, 2), (1, 3), (3, 1), \
        (0, 0), (2, 2), (0, 1)]
        if board.robber != (2,0):
            spots.remove(board.robber)
        return spots[random.randint(0, len(spots) - 1)]


    def choose_card(self, string):
        possible_cards = ['w', 'l', 'g', 'b', 'o']
        return possible_cards[random.randint(0, len(possible_cards) - 1)]


    def decide_move(self, dev_played, board, deck, players, robber):
        if self.random:
            possible_moves = self.get_legal_moves(board, deck, dev_played, robber, 0)

            # Choose a move randomly from the set of possible moves!
            return possible_moves[random.randint(0, len(possible_moves) - 1)]
            
        AI = MCTSAI(board, self.time, self.max_moves, players, deck, dev_played, \
            self.player_num, robber, self.weighted, self.thompson)
        board1 = copy.deepcopy(board)
        move = AI.get_play()
        return move


    def choose_road(self, board):
        possible_roads = {}

        for road_source in list(self.roads.keys()):
            possible_sinks = \
            board.coords[road_source]['available roads']

            for sink in possible_sinks:
                if (road_source, sink) not in possible_roads and \
                (sink, road_source) not in possible_roads:
                    possible_roads[(sink, road_source)] = True

        options = list(possible_roads.keys())
        return options[random.randint(0, len(options) - 1)]
