import copy
import random
import settings

from Game import Game
from utils import Move
from RandomPlayer import RandomPlayer

# A class to represent the Monte Carlo Tree Search AI

class State():
    def __init__(self, board, deck):
        self.board = board
        self.deck = deck
        self.winner = 0

class Node():
    def __init__(self, _id, parent_id, active_player_num, state, depth):
        self.wins = 1
        self.plays = 2
        self.id = _id
        self.parent_id = parent_id
        self.children = {}
        self.active_player_num = active_player_num
        self.state = state
        self.depth = depth

class MCTSAI():

    def __init__(self, board, num_simulations, deck, active_player_num):
        # class that initialize a MCTSAI, works to figure
        self.num_simulations = num_simulations
        self.nodes = [Node(0, -1, active_player_num, State(board, deck), 0)]
        self.max_depth = 0
        #factor to see how much to explore and expand we should test
        #values of this parameter.
        self.C = 1.0
        self.num_cycles_run = 0
        self.num_moves_from_root = 0
        self.legal = None

    def thompson_sample(self, node):
        if node.id == 0:
            legal = self.legal
        else:
            legal = node.state.board.active_player.get_legal_moves(node.state.board,
                                                  node.state.deck)
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
        board = state.board
        deck = state.deck

        legal = self.nodes[0].state.board.active_player.get_legal_moves(board,
                                              deck)
        self.num_moves_from_root = len(legal)
        if len(legal) == 1:
            return legal[0]
        self.legal = legal

        for i in range(self.num_simulations):
            self.num_cycles_run += 1
            self.run_cycle()
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

        # We want to choose the node that's had the most simulations played, which is plays.
        # If there are several that've had the same simulations, to differentiate, we choose 
        # the one with the most wins. Thus, by multiplying wins by a factor of 0.0001, nodes
        # with equal moves should have the same value to the left of the decimal point, 
        # but nodes with more wins will have larger values to the right. 
        return max([(self.nodes[root.children[move_made]].plays, move_made, 
                     self.nodes[root.children[move_made]].wins)
                    if move_made in root.children
                    else (0, move_made, 0)
                    for move_made in legal],
                   key=lambda x: x[0] + 0.00001 * x[2])[1]

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
            move = self.thompson_sample(current_node)
        if current_node.state.winner == 0:
            return current_node, move
        else:
            return current_node, None

    def run_expansion(self, node, move):
        #print("start of expansion")
        state_copy = copy.deepcopy(node.state)
        state_copy.board.verbose = False
        state_copy.board.active_player.make_move(move, state_copy.board, state_copy.deck, state_copy.board.players)
        new_node = Node(len(self.nodes), node.id, state_copy.board.active_player.player_num, state_copy, node.depth + 1)
        self.nodes.append(new_node)
        node.children[move] = new_node.id
        if new_node.state.board.active_player.calculate_vp() >= settings.POINTS_TO_WIN:
            new_node.state.winner = new_node.active_player_num
        return new_node

    def run_simulation(self, node):
        if node.state.winner != 0:
            return node.state.winner
        state_copy = copy.deepcopy(node.state)
        for p in state_copy.board.players:
            p.random = True
        round_thresh = max(100, state_copy.board.round_num + 10)
        new_game = Game(state_copy.board, state_copy.deck, state_copy.board.players, round_thresh, verbose=False)
        winner = new_game.play_game()
        return winner.player_num

    def run_backpropogation(self, node, winner):
        while node.id > 0:
            self.nodes[node.id].plays += 1
            if winner == node.active_player_num:
                self.nodes[node.id].wins += 1
            node = self.nodes[node.parent_id]
