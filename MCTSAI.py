import datetime
from random import choice
import copy

# A class to represent the Monte Carlo Tree Search AI
class MCSTAI():

	def __init__(self, board, time, max_moves, player, deck):
		self.timer = datetime.timedelta(seconds=time)
		self.max_moves = max_moves
		self.wins = {}
		self.plays = {}
		self.player = player
		self.board = board
		self.deck = deck


	def update(self):
		pass



    # TODO: wins and plays dictionaries need to be updated
	def get_play(self):
		self.max_depth = 0
		state = self.states[-1]

		# TODO: we need a way to represent whether a dev card has been played this turn
		legal = self.player.get_legal_moves(self.board, self.deck, dev_played)

		if len(legal) == 1:
            return legal[0]

        games = 0
		start = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - start < self.timer:
            self.run_simulation()
            games += 1

        move_states = []
        for move in legal:
        	copy_player = copy.deepcopy(player)
        	copy_board = copy.deepcopy(board)
        	copy_deck = copy.deepcopy(deck)
        	copy_player.make_move(self, move[0], copy_board, copy_deck, move[1])
        	move_states.append((move, (copy_player, copy_board, copy_deck)))


        # Pick the move with the highest percentage of wins.
        percent_wins, move = max(
            (self.wins.get((player, S), 0) /
             self.plays.get((player, S), 1),
             p)
            for p, S in moves_states
        )

        return move


	def run_simulation(self):
		pass


