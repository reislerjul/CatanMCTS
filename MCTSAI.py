import datetime
from random import choice
import copy
import settings

# A class to represent the Monte Carlo Tree Search AI


class MCTSAI():

	def __init__(self, board, time, max_moves, players, deck, player_num, robber):
		 # class that initialize a MCTSAI, works to figure 
		self.timer = datetime.timedelta(seconds=time)
		self.max_moves = max_moves
		self.wins = {}
		self.plays = {}
		self.player = players[player_num]
		self.player_num = player_num
		
		self.states = [(players, board, deck, 0, robber)]
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
			copy_players = copy.deepcopy(players)
			copy_board = copy.deepcopy(board)
			copy_deck = copy.deepcopy(deck)
			copy_player.make_move(self, move[0], copy_board, copy_deck, move[1])
			move_states.append((move, (copy_player, copy_board, copy_deck)))
	    
	    
		# Pick the move with the highest percentage of wins.
		percent_wins, move = max(
		    (self.wins.get((player, S), 0) /
		     self.plays.get((player, S), 1),
		     p)
		    for p, S in move_states
		)
	    
		return move
	
	def run_simulation(self):
		
		
		plays, wins = self.plays, self.wins
		visited_states = set()
		states_copy = self.states[:]
		state = states_copy[-1]	
		players, board, deck, dev_played, robber = state
		#the current player in the beggining of our simulation step is
		# always ourselves i believe.
		nplayers = len(players)
		curr_player_num = self.player_num 
		player = players[curr_player_num]
		expand = True
		for t in xrange(self.max_moves):
			move_type = -1
			while move_type != 0:
				legal = self.player.get_legal_moves(board, deck, dev_played, robber)
				move_states = [self.get_next_state(p, players, board, 
				                                   deck, curr_player_num) for p in legal]
				
				if all(plays.get((player, S)) for p, S in move_states):
					#if we know whether moves are good or not use it
					log_total = log(sum(plays[(player, S)] for p, S in
						            move_states))
					value, move, state = max(
					    ((wins[(player, S)] / plays[(player, S)]) +
					     self.C * sqrt(log_total / plays[(player, S)]), p, S)
					    for p, S in move_states
					)
				else:
					move = choice(legal)
					state = self.get_next_state(move, players, board, deck, curr_player_num)
				states_copy.append()
				move_type = move[0]
				if expand and (player, state) not in self.plays:
						expand = False
						plays[(player, state)] = 0
						wins[(player, state)] = 0
						if t > self.max_depth:
							self.max_depth = t
				visited_states.add((player, state))
			#change it to the next player as the turn is now over.
			if curr_player_num == nplayers - 1:
				curr_player_num =0
				player = players[0]
			else:
				curr_player_num +=1
				player = players[cur_player_num]
			if player.calculate_vp() >= settings.POINTS_TO_WIN:
				winner = player.player_num			
			if winner:
				break	
		if winner == 0:
			vps = [player.calculate_vp() for player in players]
			winner = vps.index(max(vps))
		for player, state in visited_states:
			if (player, state) not in plays:
				continue
			plays[(player, state)] += 1
			if player == winner:
				wins[(player, state)] += 1		
		
	def get_next_state(self, move, players, board, deck, player_num):
		#helper function that given a legal move gets the next state
		copy_players = copy.deepcopy(players)
		copy_board = copy.deepcopy(board)
		copy_deck = copy.deepcopy(deck)
		copy_player = copy_players[player_num]
		print(move)
		if move[0] == 7:
			copy_player.make_move(move[0], copy_board, copy_deck, (move[1], move[2]))
		elif len(move) > 1:
			copy_player.make_move(move[0], copy_board, copy_deck, move[1])
		return (move, (copy_players, copy_board, copy_deck, 0))
	