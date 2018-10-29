import copy
import datetime
import random
import settings

from Game import Game
from utils import Move

# A class to represent the Monte Carlo Tree Search AI

class State():
    def __init__(self, players, board, deck, dev_played, robber):
        self.players = players
        self.board = board
        self.deck = deck
        self.dev_played = dev_played
        self.robber = robber
        self.winner = 0

class Node():
    def __init__(self, _id, parent_id, player_num, prev_player, state, depth):
        self.wins = 1
        self.plays = 2
        self.id = _id
        self.parent_id = parent_id
        self.children = {}
        self.active_player_num = player_num
        self.prev_player_num = prev_player
        self.state = state
        self.depth = depth

class MCTSAI():

    def __init__(self, board, time, max_moves, players, deck, dev_played, player_num, robber, weighted, thompson):
        # class that initialize a MCTSAI, works to figure 
        self.timer = datetime.timedelta(seconds=time)
        self.max_moves = max_moves
        self.nodes = [Node(0, -1, player_num, 0, State(players, board, deck, dev_played, robber), 0)]
        self.max_depth = 0
        self.weighted = weighted
        self.thompson = thompson
        #factor to see how much to explore and expand we should test
        #values of this parameter.
        self.C = 1.0

    # TODO: wins and plays dictionaries need to be updated
   
    def thompson_sample(self, node):
        active_player = node.state.players[node.active_player_num - 1]
        legal = active_player.get_legal_moves(node.state.board, node.state.deck, node.state.dev_played, node.state.robber, self.weighted)
        # Pick a move with thompson sampling
        '''
        max_sample = 0
        for move_made in legal:
            if move_made in node.children:
                games_won = self.nodes[node.children[move_made]].wins
                games_played = self.nodes[node.children[move_made]].plays
            else:
                games_won = 1
                games_played = 2# len(node.state.players)
            sample = random.betavariate(games_won, games_played - games_won)
            if sample > max_sample:
                max_sample = sample
                move = move_made
        return move
        '''
        return max([(self.nodes[node.children[move_made]].wins, self.nodes[node.children[move_made]].plays, move_made)
                    if move_made in node.children
                    else (1, 2, move_made)
                    for move_made in legal],
                    key=lambda x: random.betavariate(x[0], x[1] - x[0]))[2]
   
    def get_play(self):
        state = self.nodes[0].state
        players = state.players
        board = state.board
        deck = state.deck
        dev_played = state.dev_played
        robber = state.robber
        # TODO: we need a way to represent whether a dev card has been played this turn
        active_player = self.nodes[0].state.players[self.nodes[0].active_player_num - 1]
        legal = active_player.get_legal_moves(board, deck, dev_played, robber, self.weighted)
        
        if len(legal) == 1:
            return legal[0]

        start = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - start < self.timer:
            self.run_cycle()
        
        root = self.nodes[0]
        # Pick the move with the most wins.
        '''
        max_winrate = -1
        for move_made in legal:
            if move_made in root.children:
                games_won = self.nodes[root.children[move_made]].wins
                games_played = self.nodes[root.children[move_made]].plays
            else:
                games_won = 1
                games_played = 2
            winrate = float(games_won) / games_played
            print(games_won, games_played)
            if winrate > max_winrate:
                max_winrate = winrate
                move = move_made
        return move
        '''
        return max([(self.nodes[root.children[move_made]].plays, move_made)
                    if move_made in root.children
                    else (2, move_made)
                    for move_made in legal],
                   key=lambda x: x[0] + random.uniform(0, 1))[1]
    
    def run_cycle(self):
        node, move = self.run_selection()
        if move.move_type == Move.END_TURN:
            # winner has already been found
            winner = node.state.winner
            self.run_backpropogation(node, winner)
        else:
            new_node = self.run_expansion(node, move)
            winner = self.run_simulation(new_node)
            self.run_backpropogation(new_node, winner)

    def run_selection(self):
        current_node = self.nodes[0]
        move = self.thompson_sample(current_node)
        while current_node.state.winner == 0 and move in current_node.children:
            current_node = self.nodes[current_node.children[move]]
            if current_node.active_player_num > 0:
                move = self.thompson_sample(current_node)
            elif current_node.active_player_num == -1:
                roll = random.randint(1, 6) + random.randint(1, 6)
                next_player = current_node.prev_player_num
                if next_player > len(current_node.state.players):
                    next_player = 1
                move = Move(Move.ROLL_DICE, roll=roll, player=next_player)
            else:
                card = current_node.state.deck.peek()
                move = Move(Move.DRAW_DEV, card_type=card, player=current_node.state.board.players[current_node.prev_player_num])
        if current_node.state.winner == 0:
            return current_node, move
        else:
            return current_node, None
    
    def run_expansion(self, node, move):
        state_copy = copy.deepcopy(node.state)
        if node.active_player_num == -1:
            # roll dice
            state_copy.board.allocate_resources(move.roll, state_copy.players)
            new_node = Node(len(self.nodes), node.id, move.player.player_num, node.active_player_num, state_copy, node.depth+1)
            self.nodes.append(new_node)
            return new_node
        elif node.active_player_num == -2:
            # draw dev card
            state_copy.players[move.player.player_num-1].dev_cards[move.card_type] += 1
            state_copy.deck.remove_card_type(move.card_type)
            new_node = Node(len(self.nodes), node.id, move.player.player_num, node.active_player_num, state_copy, node.depth+1)
            self.nodes.append(new_node)
            node.children[move] = new_node.id
            if node.state.players[node.active_player_num - 1].calculate_vp() >= settings.POINTS_TO_WIN:
                node.state.winner = node.active_player_num
            return new_node
        else:
            # player move
            player = state_copy.players[node.active_player_num-1]
            if move.move_type != Move.END_TURN:
                player.make_move(move, state_copy.board, state_copy.deck)
            next_player = node.active_player_num
            if move.move_type == Move.END_TURN:
                next_player = -1
            if move.move_type == Move.BUY_DEV:
                next_player = -2
            new_node = Node(len(self.nodes), node.id, next_player, node.active_player_num, state_copy, node.depth+1)
            self.nodes.append(new_node)
            node.children[move] = new_node.id
            if node.state.players[node.active_player_num - 1].calculate_vp() >= settings.POINTS_TO_WIN:
                node.state.winner = node.active_player_num
            return new_node

    def run_simulation(self, node):
        state_copy = copy.deepcopy(node.state)
        for p in state_copy.players:
            p.random = True
        new_game = Game(state_copy.board, state_copy.deck, state_copy.players, verbose=False)
        winner = new_game.play_game()
        return winner
    
    def run_backpropogation(self, node, winner):
        while node.id > 0:
            self.nodes[node.id].plays += 1
            if winner == node.prev_player_num:
                self.nodes[node.id].wins += 1
            node = self.nodes[node.parent_id]
