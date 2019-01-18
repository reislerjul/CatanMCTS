import copy
import datetime
import random
import settings

from Game import Game
from utils import Move
from RandomPlayer import RandomPlayer

# A class to represent the Monte Carlo Tree Search AI

class State():
    def __init__(self, players, board, deck):
        self.players = players
        self.board = board
        self.deck = deck
        self.winner = 0

class Node():
    def __init__(self, _id, parent_id, active_player_num, curr_player_num, state, depth):
        self.wins = 1
        self.plays = 2
        self.id = _id
        self.parent_id = parent_id
        self.children = {}
        self.active_player_num = active_player_num
        self.curr_player_num = curr_player_num
        self.state = state
        self.depth = depth

class MCTSAI():

    def __init__(self, board, time, players, deck, player_num, weighted, thompson):
        # class that initialize a MCTSAI, works to figure
        self.timer = datetime.timedelta(seconds=time)
        self.nodes = [Node(0, -1, player_num, player_num, State(players, board, deck), 0)]
        self.max_depth = 0
        self.weighted = weighted
        self.thompson = thompson
        #factor to see how much to explore and expand we should test
        #values of this parameter.
        self.C = 1.0


    def thompson_sample(self, node):
        active_player = node.state.players[node.curr_player_num - 1]

        legal = active_player.get_legal_moves(node.state.board,
                                              node.state.deck,
                                              self.weighted)
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
        #print("__________________STARTING AI CALL__________________")
        state = self.nodes[0].state
        players = state.players
        board = state.board
        deck = state.deck

        active_player = self.nodes[0].state.players[self.nodes[0].curr_player_num - 1]
        legal = active_player.get_legal_moves(board,
                                              deck,
                                              self.weighted)

        if len(legal) == 1:
            return legal[0]

        start = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - start < self.timer:
            #print('running cycle')
            self.run_cycle()
        #print('finished running cycles!')

        root = self.nodes[0]


        # Breadth first traversal of the created MCTS tree
        '''
        queue = [root]        
        while len(queue) > 0:
            print("----NODE----")
            curr_node = queue.pop(0)
            print("parent id: " + str(curr_node.parent_id))
            print("node id:" + str(curr_node.id))
            print("active player: " + str(curr_node.active_player_num))
            for move in curr_node.children.items():
                print("**child**")
                print("child id: " + str(move[1]))
                print("move type: " + str(move[0].move_type))
                queue.append(self.nodes[curr_node.children[move[0]]])
        '''

        # This will find the longest path in the tree and print it
        '''
        max_depth = 0
        max_depth_node = None
        for node in self.nodes:
            if node.depth > max_depth:
                max_depth = node.depth
                max_depth_node = node
        path = [max_depth_node]
        while max_depth_node.id > 0:
            max_depth_node = self.nodes[max_depth_node.parent_id]
            path.append(max_depth_node)
        print("_________PRINTING LONGEST PATH_________")
        for node in path[::-1]:
            print("----NODE----")
            print("parent id: " + str(node.parent_id))
            print("node id:" + str(node.id))
            print("depth: " + str(node.depth))
            print("active player: " + str(node.active_player_num))
            print("round num: " + str(node.state.board.round_num))
            print("has rolled dice: " + str(node.state.players[node.active_player_num - 1].has_rolled))
            for move in node.children.items():
                child = self.nodes[node.children[move[0]]]
                if child in path:
                    print("move type to get to child: " + str(move[0].move_type))
        '''

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

        # TODO: fix this part later
        #print('____starting new loop_____')
        while current_node.state.winner == 0 and move in current_node.children:
            current_node = self.nodes[current_node.children[move]]

            #print('active player num')
            #print(current_node.active_player_num)
            #print('round num')
            #print(current_node.state.board.round_num)
            move = self.thompson_sample(current_node)
            #print("move type: " + str(move.move_type))
        #print('after loop move: ' + str(move.move_type))

        if current_node.state.winner == 0:
            return current_node, move
        else:
            return current_node, None

    def run_expansion(self, node, move):
        state_copy = copy.deepcopy(node.state)
        player = state_copy.players[node.active_player_num - 1]
        turn_player = node.active_player_num
        active_player = node.active_player_num
        if move.move_type != Move.END_TURN:
            player.make_move(move, state_copy.board, state_copy.deck, state_copy.players)
            #print("expansion move: " + str(move.move_type))
            #print("active player: " + str(state_copy.board.active_player.player_num))
            if move.move_type == move.ROLL_DICE:
                player.has_rolled = True
            elif move.move_type in {Move.ACCEPT_TRADE, Move.DECLINE_TRADE}:
                turn_player = (node.active_player_num % len(state_copy.players)) + 1
        else:
            # Update the round number. Also, on the second round, the order of play is reverse
            if state_copy.board.round_num != 1:
                turn_player = node.active_player_num + 1
                active_player = node.active_player_num + 1
            else:
                turn_player = node.active_player_num - 1
                active_player = node.active_player_num - 1

            # If the turn player/active player are out of range, its the end of a round
            if turn_player not in range(1, len(state_copy.players) + 1):
                # End of rounds except for first round
                if turn_player < 1 or state_copy.board.round_num > 1:
                    turn_player = 1
                    active_player = 1
                else:
                    turn_player = len(state_copy.players)
                    active_player = len(state_copy.players)
                state_copy.board.round_num += 1
        state_copy.board.active_player = state_copy.players[active_player - 1]
        new_node = Node(len(self.nodes), node.id, active_player, turn_player, 
            state_copy, node.depth + 1)
        self.nodes.append(new_node)
        node.children[move] = new_node.id
        if node.state.players[node.active_player_num - 1].calculate_vp() >= settings.POINTS_TO_WIN:
            node.state.winner = node.active_player_num
        return new_node

    def run_simulation(self, node):
        state_copy = copy.deepcopy(node.state)
        new_players = []
        for p in state_copy.players:
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
            new_player.has_rolled = p.has_rolled
            new_player.dev_played = p.dev_played
            new_player.trades_tried = p.trades_tried
            if p.player_num == state_copy.board.active_player.player_num:
                state_copy.board.active_player = new_player
            if p.player_num == state_copy.board.largest_army_player:
                state_copy.board.largest_army_player = new_player
            if p.player_num == state_copy.board.longest_road_player:
                state_copy.board.longest_road_player = new_player
            new_players.append(new_player)
        state_copy.board.players = new_players
        new_game = Game(state_copy.board, state_copy.deck, new_players, 
            start_player=state_copy.board.active_player.player_num - 1, verbose=False)
        new_game.num_rounds = state_copy.board.round_num
        winner = new_game.play_game()
        return winner

    def run_backpropogation(self, node, winner):
        while node.id > 0:
            self.nodes[node.id].plays += 1
            if winner == node.curr_player_num:
                self.nodes[node.id].wins += 1
            node = self.nodes[node.parent_id]
