import copy
import datetime
import random
import settings

from Game import Game
from utils import Move
from RandomPlayer import RandomPlayer

# A class to represent the Monte Carlo Tree Search AI

class State():
    def __init__(self, players, board, deck, dev_played, robber, trades_tried):
        self.players = players
        self.board = board
        self.deck = deck
        self.dev_played = dev_played
        self.robber = robber
        self.winner = 0
        self.trades_tried = trades_tried

# Add give and receive to represent nodes where trades are occuring 
class Node():
    def __init__(self, _id, parent_id, player_num, prev_player, state, depth, give=None, receive=None):
        self.wins = 1
        self.plays = 2
        self.id = _id
        self.parent_id = parent_id
        self.children = {}
        self.active_player_num = player_num
        self.prev_player_num = prev_player
        self.state = state
        self.depth = depth
        self.give = give
        self.receive = receive

class MCTSAI():

    def __init__(self, board, time, max_moves, players, deck, dev_played, player_num, robber, weighted, thompson, \
        trades_tried, give, receive):
        # class that initialize a MCTSAI, works to figure
        self.timer = datetime.timedelta(seconds=time)
        self.max_moves = max_moves
        self.nodes = [Node(0, -1, player_num, 0, State(players, board, deck, dev_played, robber, trades_tried), 0, give, receive)]
        self.max_depth = 0
        self.weighted = weighted
        self.thompson = thompson
        #factor to see how much to explore and expand we should test
        #values of this parameter.
        self.C = 1.0


    def thompson_sample(self, node):
        active_player = node.state.players[node.active_player_num - 1]

        # TODO: why are there cases where robber is 3 and give/receive are none?
        legal = active_player.get_legal_moves(node.state.board,
                                              node.state.deck,
                                              node.state.dev_played,
                                              node.state.robber,
                                              self.weighted,
                                              node.state.trades_tried, 
                                              node.give, 
                                              node.receive)
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

        # TODO: it seems like AI always accepts trade if they can; can we print out the rate of 
        # accepting the trade vs. not accepting?
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
        trades_tried = state.trades_tried
        robber = state.robber

        active_player = self.nodes[0].state.players[self.nodes[0].active_player_num - 1]
        legal = active_player.get_legal_moves(board,
                                              deck,
                                              dev_played,
                                              robber,
                                              self.weighted,
                                              trades_tried,
                                              self.nodes[0].give,
                                              self.nodes[0].receive)

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

        if not move:
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
                move = Move(Move.ROLL_DICE, roll=roll, player=current_node.state.board.players[next_player - 1])
            elif current_node.active_player_num == -2:
                card = current_node.state.deck.peek()
                move = Move(Move.DRAW_DEV, card_type=card, player=current_node.state.board.players[current_node.prev_player_num - 1])
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
                player.make_move(move, state_copy.board, state_copy.deck, state_copy.players)
            next_player = node.active_player_num
            if move.move_type == Move.END_TURN:
                next_player = -1
            if move.move_type == Move.BUY_DEV:
                next_player = -2
            if move.move_type in [Move.ACCEPT_TRADE, Move.DECLINE_TRADE]:
                next_player = node.active_player_num % len(state_copy.players) + 1
            new_node = Node(len(self.nodes), node.id, next_player, node.active_player_num, state_copy, node.depth+1)
            self.nodes.append(new_node)
            node.children[move] = new_node.id
            if node.state.players[node.active_player_num - 1].calculate_vp() >= settings.POINTS_TO_WIN:
                node.state.winner = node.active_player_num
            return new_node

        # TODO: should we have another case for trades?

    def run_simulation(self, node):
        state_copy = copy.deepcopy(node.state)
        new_players = []
        for p in state_copy.players:
            if isinstance(p, RandomPlayer):
                new_players.append(p)
            else:
                new_player = RandomPlayer(p.player_num)
                new_player.resources = p.resources
                new_player.dev_cards = p.dev_cards
                new_player.num_knights_played = p.num_knights_played
                new_player.longest_road = p.longest_road
                new_player.largest_army = p.largest_army
                new_player.ports = p.ports
                new_player.cities = p.cities
                new_player.settlements = p.settlements
                new_player.roads = p.roads
                new_player.total_roads = p.total_roads
                new_player.random = True
                new_players.append(new_player)
        new_game = Game(state_copy.board, state_copy.deck, new_players, verbose=False)
        winner = new_game.play_game()
        return winner

    def run_backpropogation(self, node, winner):
        while node.id > 0:
            self.nodes[node.id].plays += 1
            if winner == node.prev_player_num:
                self.nodes[node.id].wins += 1
            node = self.nodes[node.parent_id]
