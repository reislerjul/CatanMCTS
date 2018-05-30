import datetime
from random import choice
import copy
import settings

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
		self.states = []
		self.C = 1.0
	def update(self, state):
		self.states.append(state)



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
		plays, wins = self.plays, self.wins
		visited_states = set()
		states_copy = self.states[:]
		state = states_copy[-1]	
		# this is a place holder, really should be a way to access whose turn it is or which player it is
		player = self.player
		expand = True
		for t in xrange(self.max_moves):
			legal = self.player.get_legal_moves(states_copy)
			move_states = [get_next_state(p, self.player, self.board, 
			                              self.deck) for p in legal]
			if all(plays.get((player, S)) for p, S in moves_states):
				#if we know whether moves are good or not use it
				log_total = log(sum(plays[(player, S)] for p, S in
				                    moves_states))
				value, move, state = max(
			            ((wins[(player, S)] / plays[(player, S)]) +
			             self.C * sqrt(log_total / plays[(player, S)]), p, S)
			            for p, S in moves_states
			        )				
			else:
				move, state = choice(legal)
			states_copy.append(state)
			if expand and (player, state) not in self.plays:
					expand = False
					plays[(player, state)] = 0
					wins[(player, state)] = 0
					if t > self.max_depth:
						self.max_depth = t
			visited_states.add((player, state))
			player = self.player
			if player.calculate_vp() >= settings.POINTS_TO_WIN:
				winner = player.player_num			
			if winner:
				break	
		for player, state in visited_states:
			if (player, state) not in plays:
				continue
			plays[(player, state)] += 1
			if player == winner:
				wins[(player, state)] += 1		
		
	def get_next_state(move, player, board, deck):
		#helper function that given a legal move gets the next state
		copy_player = copy.deepcopy(player)
		copy_board = copy.deepcopy(board)
		copy_deck = copy.deepcopy(deck)
		copy_player.make_move(self, move[0], copy_board, copy_deck, move[1])
		return (move, (copy_player, copy_board, copy_deck))
	