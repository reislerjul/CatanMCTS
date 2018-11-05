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
    def move_robber(self, board, spot, victim, deck, players):
        while True:
            if board.robber != (2,0):
                spots.remove(board.robber)
            spot = spots[random.randint(0, len(spots) - 1)]
            move = Move(Move.MOVE_ROBBER, coord-spot, player=victim)
            invalid = self.make_move(move, board, deck, players)
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


    # This is only called when we play a dev card and are choosing a robber position
    # TODO: test that this works correctly
    def choose_robber_position(self, board, players, deck):
        move = decide_move(1, board, deck, players, 1)
        return move


    # TODO: think about how to change this so that for year of plenty and monopoly
    # we can use MCTS
    def choose_card(self, string):
        possible_cards = ['w', 'l', 'g', 'b', 'o']
        return possible_cards[random.randint(0, len(possible_cards) - 1)]


    def decide_move(self, dev_played, board, deck, players, robber, trades_tried, give=None, recieve=None):
        if self.random:
            possible_moves = self.get_legal_moves(board, deck, dev_played, robber, 0, trades_tried)
            # Choose a move randomly from the set of possible moves!
            return possible_moves[random.randint(0, len(possible_moves) - 1)]

        AI = MCTSAI(board, self.time, self.max_moves, players, deck, dev_played, \
            self.player_num, robber, self.weighted, self.thompson, trades_tried, give, recieve)
        board1 = copy.deepcopy(board)
        move = AI.get_play()
        return move


    # This is only called during road builder
    # TODO: test that this works
    def choose_road(self, board, deck, players):
        move = self.decide_move(1, board, deck, players, 2)
        return move


    def should_accept_trade(self, receive, give, board, deck, players):
        if self.can_accept_trade(give):
            move = self.decide_move(0, board, deck, players, 3, 0, give, receive)
            if move.move_type == Move.END_TURN:
                return 0
            return 1
        return 0


    def choose_trader(self, traders):
        return traders[random.randint(0, len(traders) - 1)]
