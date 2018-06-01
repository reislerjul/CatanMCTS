import datetime
from random import choice
import copy
import settings
from math import log
# A class to represent the Monte Carlo Tree Search AI


class MCTSAI():

	def __init__(self, board, time, max_moves, players, deck, player_num, robber):
		 # class that initialize a MCTSAI, works to figure 
		self.timer = datetime.timedelta(seconds=time)
		self.max_moves = max_moves
		self.wins = {}
		self.plays = {}
		self.player = players[player_num - 1]
		self.player_num = player_num
		self.states = [(players, board, deck, 0, robber)]
		#factor to see how much to explore and expand we should test
		#values of this parameter.
		self.C = 1.0
	def update(self, state):
		self.states.append(state)



    # TODO: wins and plays dictionaries need to be updated
   
	def get_play(self):
		self.max_depth = 0
		state = self.states[-1]
		players, board, deck, dev_played, robber = state
		# TODO: we need a way to represent whether a dev card has been played this turn
		legal = self.player.get_legal_moves(board, deck, dev_played, robber)
		
		if len(legal) == 1:
			return legal[0]

		games = 0
		start = datetime.datetime.utcnow()
		while datetime.datetime.utcnow() - start < self.timer:
		    self.run_simulation()
		    games += 1
		
		move_states = []
		for move in legal:
			state_val = self.get_next_state(move, players, board, deck, self.player_num -1)
			move_states.append((state_val[0], self.h(state_val[1])))
	    
		player_h = players[self.player_num -1].hashable_player()
		# Pick the move with the highest percentage of wins.
		percent_wins, move = max(
		    (self.wins.get((player_h, S), 0) /
		     self.plays.get((player_h, S), 1),
		     p)
		    for p, S in move_states
		)
		return move
	

	def run_simulation(self):
		
		winner = -1
		plays, wins = self.plays, self.wins
		visited_states = set()
		states_copy = self.states[:]
		state = states_copy[-1]	
		players, board, deck, dev_played, robber = state #self.copy_state(state[0], state[1], state[2], state[3], state[4])
		#the current player in the beggining of our simulation step is
		# always ourselves i believe.
		nplayers = len(players)
		player_num = self.player_num - 1
		curr_player_num = self.player_num - 1
		player = players[curr_player_num]
		expand = True
		for t in range(self.max_moves):
			player_h = player.hashable_player()
			move_type = -1
			while move_type != 0:
				legal = self.player.get_legal_moves(board, deck, dev_played, robber)
				
				move_states = [self.get_next_state(p, players, board, 
				                                   deck, curr_player_num) for p in legal]
				
				
				hashed_states = [(p, self.h(D)) for p, D in move_states]
				if all((p,S) in plays for p, S in hashed_states):
					#if we know whether moves are good or not use it
					log_total = log(sum(plays[(player_h, S)] for p, S in
						            hashed_states))
					value, move, state = max(
					    ((wins[(player_h, S)] / plays[(player_h, S)]) +
					     self.C * sqrt(log_total / plays[(player_h, S)]), p, S)
					    for p, S in hashed_states
					)
				else:
					move = choice(legal)
					state = self.get_next_state(move, players, board, deck, curr_player_num)
				states_copy.append(state)
				h_state = self.h(state[1])
				move_type = move[0]
				if robber:
					robber = 0
				if expand and (player_h, h_state) not in self.plays:
						expand = False
						plays[(player_h, h_state)] = 0
						wins[(player_h, h_state)] = 0
						if t > self.max_depth:
							self.max_depth = t
				visited_states.add((player_h, h_state))
			#change it to the next player as the turn is now over.
			if curr_player_num == nplayers - 1:
				curr_player_num =0
				player = players[0]
			else:
				curr_player_num +=1
				player = players[curr_player_num]
			if player.calculate_vp() >= settings.POINTS_TO_WIN:
				winner = player.player_num			
				if winner:
					break	
		
		if winner == -1:
			vps = [player.calculate_vp() for player in players]
			winner = vps.index(max(vps))
		for player, state in visited_states:
			if (player, state) not in plays:
				continue
			plays[(player, state)] += 1
			if player_num == winner:
				wins[(player, state)] += 1	


	def h(self,s):
		''' takes in a state as input and hashes it'''
		p = s[0]
		board = s[1].hashable_board()
		deck = s[2].hashable_deck()
		dev_played = s[3]
		
		robber = s[4]
		if len(p) == 4:
			return (p[0].hashable_player(), p[1].hashable_player(), 
			        p[2].hashable_player(), p[3].hashable_player(), 
			        board, deck, dev_played, robber)
		elif len(p) == 3:
			return (p[0].hashable_player(), p[1].hashable_player(), 
			        p[2].hashable_player(),  
			        board, deck, dev_played, robber)
		

	def copy_state(self,  players, board, deck, dev_played, robber):
		copy_players = copy.deepcopy(players)
		copy_board = copy.deepcopy(board)
		copy_deck = copy.deepcopy(deck)
		return (copy_players, copy_board, copy_deck, dev_played, robber)
		
		
	def get_next_state(self, move, players, board, deck, player_num):
		#helper function that given a legal move gets the next state
		player = players[player_num]
		
		if move[0] == 7:
			player.make_move(move[0], board, deck, (move[1], move[2]))
		elif len(move) > 1:
			player.make_move(move[0], board, deck, move[1])
		if move[0] == 5:
			return (move, (players, board, deck, 1,0))
		return (move, (players, board, deck, 0,0))
	