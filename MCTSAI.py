import datetime
from random import choice
import copy
import random
import settings
from math import log
# A class to represent the Monte Carlo Tree Search AI

class State():
    def __init__(self, players, board, deck, dev_played, robber):
        self.players = players
        self.board = board
        self.deck = deck
        self.dev_played = dev_played
        self.robber = robber

class Node():
    def __init__(self, id, parent_id, player_num, prev_player, state, depth):
        self.wins = 1
        self.plays = len(state.players)
        self.id = id
        self.parent_id = parent_id
        self.children = {}
        self.active_player = player_num
        self.prev_player = prev_player
        self.state = state
        self.depth = depth

class MCTSAI():

    def __init__(self, board, time, max_moves, players, deck, dev_played, player_num, robber, weighted, thompson):
        # class that initialize a MCTSAI, works to figure 
        self.timer = datetime.timedelta(seconds=time)
        self.max_moves = max_moves
        self.nodes = [Node(0, -1, player_num, 0, State(players, board, deck, dev_played, robber), 0)]
        self.max_depth = 0
        self.max_id = 0
        self.weighted = weighted
        self.thompson = thompson
        #factor to see how much to explore and expand we should test
        #values of this parameter.
        self.C = 1.0

    # TODO: wins and plays dictionaries need to be updated
   
    def thompson_sample(self, node):
        active_player = node.players[node.active_player - 1]
        legal = active_player.get_legal_moves(node.state.board, node.state.deck, node.state.dev_played, node.state.robber, self.weighted)
        # Pick a move with thompson sampling
        max_sample = 0
        for move_made in legal:
            if move_made in node.children:
                games_won = node.children[move_made].wins
                games_played = node.children[move_made].plays
            else:
                games_won = 1
                games_played = len(players)
            sample = np.random.beta(games_won, games_played - games_won)
            if sample > max_sample:
                max_sample = sample
                move = move_made
        return move
   
    def get_play(self):
        state = self.nodes[0].state
        players = state.players
        board = state.board
        deck = state.deck
        dev_plaeyd = state.dev_played
        robber = state.robber
        # TODO: we need a way to represent whether a dev card has been played this turn
        legal = self.player.get_legal_moves(board, deck, dev_played, robber, self.weighted)
        
        if len(legal) == 1:
            return legal[0]

        start = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - start < self.timer:
            self.run_cycle()
        
        root = self.nodes[0]
        if self.thompson:
            move = self.thompson_sample(root)
        else:
            # Pick the move with the highest percentage of wins.
            max_winrate = -1
            for move_made in legal:
                if move_made in root.children:
                    games_won = root.children[move_made].wins
                    games_played = root.children[move_made].plays
                else:
                    games_won = 1
                    games_played = len(players)
                winrate = float(games_won) / games_played
                if winrate > max_winrate:
                    max_winrate = winrate
                    move = move_made
        return move
    
    def run_cycle(self):
        node, move = self.run_selection()
        new_node = self.run_expansion(node, move)
        winner = self.run_simulation(new_node)
        self.run_backpropogation(new_node, winner)
    
    def run_selection(self):
        current_node = self.nodes[0]
        move = self.thompson_sample(current_node)
        while move in current_node.children:
            current_node = current_node.children[move]
            if current_node.active_player > 0:
                move = self.thompson_sample(current_node)
            elif current_node.active_player == -1:
                roll = random.randint(1, 6) + random.randint(1, 6)
                next_player = current_node.prev_player
                if next_player > len(current_node.state.players):
                    next_player = 1
                move = (roll, next_player)
            else:
                random.shuffle(current_node.state.deck.stack)
                card = current_node.state.deck.stack[0]
                move = (card, current_node.prev_player)
        return current_node, move
    
    def run_expansion(self, node, move):
        state_copy = copy.deepcopy(node.state)
        if node.active_player == -1:
            state_copy.board.allocate_resources(move[0], state_copy.players)
            self.max_id += 1
            new_node = Node(node.max_id, node.id, move[1], node.active_player, state_copy, node.depth+1)
            self.nodes.append(new_node)
            return new_node
        elif node.active_player == -2:
            dev_card = {0:'Knight', 1:'Victory Point'\
                2:'Road Building', 3:'Monopoly', 4:'Year of Plenty'}
            state_copy.players[move[1]-1].dev_cards[dev_card[move[0]]] += 1
            state_copy.deck.remove_card_type(move[0])
            self.max_id += 1
            new_node = Node(self.max_id, node.id, move[1], node.active_player, state_copy, node.depth+1)
            self.nodes.append(new_node)
            return new_node
        else:
            player = state_copy.players[node.active_player-1]
            if move[0] == 7:
                player.make_move(move[0], state_copy.board, state_copy.deck, (move[1], move[2]))
                self.max_id += 1
                new_node = Node(self.max_id, node.id, node.active_player, node.active_player, state_copy, node.depth+1)
                self.nodes.append(new_node)
                return new_node
            elif len(move) > 1:
                player.make_move(move[0], state_copy.board, state_copy.deck, move[1])
                self.max_id += 1
                new_node = Node(self.max_id, node.id, node.active_player, node.active_player, state_copy, node.depth+1)
                self.nodes.append(new_node)
                return new_node
            if move[0] == 0:
                self.max_id += 1
                new_node = Node(self.max_id, node.id, -1, node.active_player, state_copy, node.depth+1)
                self.nodes.append(new_node)
                return new_node
            if move[0] == 5:
                self.max_id += 1
                new_node = Node(self.max_id, node.id, -2, node.active_player, state_copy, node.depth+1)
                self.nodes.append(new_nodes)
                return new_node

    def run_simulation(self, node):
        state_copy = copy.deepcopy(node.state)
        new_game = game(state_copy.board, state_copy.deck, state_copy.players)
        winner = game.play_game()
        return winner
    def run_backpropogation(self, node, winner):
        node.plays += 1
        if winner == node.prev_player:
            node.wins += 1
        if node.parent_id == 1:
            return
        else:
            new_node = self.nodes[node.parent_id]
            run_backpropogation(new_node, winner)
     

    def get_next_state(self, move, players, board, deck, player_num):
        #helper function that given a legal move gets the next state
        player = players[player_num - 1]
        
        if move[0] == 7:
            player.make_move(move[0], board, deck, (move[1], move[2]))
        elif len(move) > 1:
            player.make_move(move[0], board, deck, move[1])
        if move[0] == 5:
            return (move, (players, board, deck, 1,0))
        return (move, (players, board, deck, 0,0))
    