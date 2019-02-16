import copy
import random
import settings

from MCTSAI import MCTSAI
from Player import Player
from utils import Card, Move


class MCTSPlayer(Player):


    def __init__(self, player_num, num_simulations):
        super(MCTSPlayer, self).__init__(Player.MCTS_AI, player_num)
        self.num_simulations = num_simulations

        # These are used for bookkeeping. avg_legal_moves keeps track 
        # of the amount of legal moves considered from the state at 
        # which we call the MCTS algorithm. If the size of the legal
        # move set is greater than 1, we run cycles. In this case, we 
        # keep track of the number of cycles run and the number of legal
        # moves. We don't count cases where no cycles are run and there is 
        # only one possible move.
        self.avg_cycles_per_move = [0, 0]
        self.avg_legal_moves = [0, 0]

    def decide_move(self, board, deck, players):
        if self.random:
            possible_moves = self.get_legal_moves(board, deck)
            # We should choose a move randomly from the set of possible moves!
            return possible_moves[random.randint(0, len(possible_moves) - 1)]
        AI = MCTSAI(board, self.num_simulations, deck, self.player_num)
        move = AI.get_play()
        if AI.num_moves_from_root > 1:
            self.avg_legal_moves[0] += 1
            self.avg_legal_moves[1] += AI.num_moves_from_root
            self.avg_cycles_per_move[0] += 1
            self.avg_cycles_per_move[1] += AI.num_cycles_run
        return move

    def to_string(self):
        return "MCTS"