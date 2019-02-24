import copy
import random
import settings
from Game import Game
from utils import Move, Card
from RandomPlayer import RandomPlayer
import StateToFeatures
import numpy as np
import math
EPS = 1e-8

# A class to represent the Monte Carlo Tree Search AI

class State():
    def __init__(self, board, deck):
        self.board = board
        self.deck = deck
        self.winner = 0

class Node():
    def __init__(self, _id, parent_id, active_player_num, state, depth):
        self.value = 0
        self.plays = 0
        self.id = _id
        self.parent_id = parent_id
        self.children = {}
        self.active_player_num = active_player_num
        self.state = state
        self.depth = depth
        self.legal = None

class MCTSNN():

    def __init__(self, board, num_simulations, deck, active_player_num, nnet, move_to_index):
        self.num_simulations = num_simulations
        self.nodes = [Node(0, -1, active_player_num, State(board, deck), 0)]
        self.nodes[0].legal = board.active_player.get_legal_moves(board, deck)
        self.max_depth = 0

        #factor to see how much to explore and expand we should test
        self.C = 1.0
        self.nnet = nnet
        self.Ps = []       # stores initial policy (returned by neural net)
        self.move_to_index = move_to_index
        self.canonicalBoard = StateToFeatures.board_to_vector(self.nodes[0].state.board, \
                self.nodes[0].state.deck)
        if len(self.nodes[0].legal) > 1:
            # For players that are not the active player, we should randomize which dev cards they 
            # have so that the active player has imperfect information
            self.randomize_dev_cards()
            Ps, self.nodes[0].value = self.nnet.predict(self.canonicalBoard)
            self.Ps.append(Ps)

            valids = StateToFeatures.possible_actions_to_vector(self.nodes[0].legal, \
            self.nodes[0].active_player_num, len(self.nodes[0].state.board.players), self.move_to_index)
            self.Ps[0] = self.Ps[0] * valids
            sum_Ps_s = np.sum(self.Ps[0])
            if sum_Ps_s <= 0:
                # if all valid moves were masked make all valid moves equally probable
                print("All valid moves were masked, do workaround.")
                self.Ps[0] = self.Ps[0] + valids
                sum_Ps_s = len(self.nodes[0].legal)
            self.Ps[0] /= sum_Ps_s

    def randomize_dev_cards(self):
        new_deck = copy.deepcopy(self.nodes[0].state.deck)
        new_board = copy.deepcopy(self.nodes[0].state.board)

        num_hidden_devs = [sum(player.dev_cards.values()) for player in new_board.players]
        dev_cards = {Card.KNIGHT: 0,\
                     Card.VICTORY_POINT: 0,\
                     Card.ROAD_BUILDING:0,\
                     Card.MONOPOLY: 0,\
                     Card.YEAR_OF_PLENTY: 0}
        for dev in dev_cards.keys():
            dev_cards[dev] = sum([player.dev_cards[dev] if \
                player.player_num != self.nodes[0].active_player_num else 0 for player in new_board.players])
            new_deck.cards_left += ([dev] * dev_cards[dev])
        for i in range(len(new_board.players)):
            if i + 1 != self.nodes[0].active_player_num:
                new_board.players[i].dev_cards = {Card.KNIGHT: 0, Card.VICTORY_POINT: 0, \
                Card.ROAD_BUILDING:0, Card.MONOPOLY: 0, Card.YEAR_OF_PLENTY: 0}
                for j in range(num_hidden_devs[i]):
                    new_board.players[i].dev_cards[new_deck.take_card(new_deck.peek())] += 1
        self.nodes[0].state.board = new_board
        self.nodes[0].state.deck = new_deck

    def getActionProb(self, temp=1):
        '''
            Returns  a policy vector where the probability of the ith action is
            proportional to Nsa[(s,a)]**(1./temp). temp should always be 0 or 1
        '''
        # If there is only one legal move, we will just set its probability to 
        # 1 rather than running all the cycles
        root = self.nodes[0]
        action_vect = np.zeros(3151)
        if len(root.legal) == 1:
            StateToFeatures.set_value_in_action_vector(action_vect, \
                root.active_player_num, len(root.state.board.players), \
                self.move_to_index, root.legal[0], 1)
            return action_vect            
        for i in range(self.num_simulations):
            self.run_cycle()

        # Used so we can play the best move
        probs = np.zeros(3151)
        if temp == 0:
            max_move = max([(move, self.nodes[root.children[move]].plays, self.nodes[root.children[move]].value)
                for move in root.children.keys()], key=lambda x: x[1] + 0.00001 * x[2])[0]
            StateToFeatures.set_value_in_action_vector(probs, \
                root.active_player_num, len(root.state.board.players), \
                self.move_to_index, max_move, 1)   
            return probs         

        # We want the probability of each move being chosen to be proportional to the number of plays
        for action in root.children.keys():
            StateToFeatures.set_value_in_action_vector(probs, \
                root.active_player_num, len(root.state.board.players), \
                self.move_to_index, action, self.nodes[root.children[action]].plays) 
        sum_probs = np.sum(probs)
        return probs / sum_probs

    def run_cycle(self):
        node, move = self.run_selection()
        if not move:
            leaf_player = node.state.winner
            self.run_backpropogation(node, leaf_player, 1)
        else:
            new_node, value = self.run_expansion(node, move)
            self.run_backpropogation(new_node, new_node.active_player_num, value)

    def choose_action(self, node):
        '''
        Unvectorized code equivalent:
        cur_best = -float('inf')
        best_act = -1
        for a in legal:
            action_index = StateToFeatures.action_to_index(a, \
                node.state.board.active_player.player_num, len(node.state.board.players), \
                self.move_to_index)
            if a in node.children:
                Nsa = self.nodes[node.children[a]].plays
                Qsa = self.nodes[node.children[a]].value
                u = Qsa + \
                self.C * self.Ps[node][action_index] * math.sqrt(node.plays) / \
                (1 + Nsa)
            else:
                u = self.C * self.Ps[node][action_index] * math.sqrt(node.plays + EPS)
            if u > cur_best:
                cur_best = u
                best_act = a
        return best_act
        '''
        '''
        print(node.id)
        print(len(self.Ps))
        print(self.Ps[node.id])

        move_stuff = [(move, self.nodes[node.children[a]].value + \
                self.C * self.Ps[node.id][StateToFeatures.action_to_index(a, \
                node.state.board.active_player.player_num, len(node.state.board.players), \
                self.move_to_index)] * math.sqrt(node.plays) / \
                (1 + self.nodes[node.children[a]].plays)) 
                if move in node.children
                else (move, self.C * self.Ps[node.id][StateToFeatures.action_to_index(a, \
                node.state.board.active_player.player_num, len(node.state.board.players), \
                self.move_to_index)] * math.sqrt(node.plays + EPS))
                for move in node.legal]
        print(move_stuff)
        '''

        return max([(move, self.nodes[node.children[move]].value + \
                self.C * self.Ps[node.id][StateToFeatures.action_to_index(move, \
                node.state.board.active_player.player_num, len(node.state.board.players), \
                self.move_to_index)] * math.sqrt(node.plays) / \
                (1 + self.nodes[node.children[move]].plays)) 
                if move in node.children
                else (move, self.C * self.Ps[node.id][StateToFeatures.action_to_index(move, \
                node.state.board.active_player.player_num, len(node.state.board.players), \
                self.move_to_index)] * math.sqrt(node.plays + EPS))
                for move in node.legal], key=lambda x: x[1])[0]

    def run_selection(self):
        current_node = self.nodes[0]
        action = self.choose_action(current_node)
        while current_node.state.winner == 0 and action in current_node.children:
            current_node = self.nodes[current_node.children[action]]
            action = self.choose_action(current_node)
        if current_node.state.winner == 0:
            return current_node, action
        else:
            return current_node, None

    def run_expansion(self, node, move):
        state_copy = copy.deepcopy(node.state)
        state_copy.board.verbose = False
        state_copy.board.active_player.make_move(move, state_copy.board, state_copy.deck, state_copy.board.players)
        new_node = Node(len(self.nodes), node.id, state_copy.board.active_player.player_num, state_copy, node.depth + 1)
        self.nodes.append(new_node)
        node.children[move] = new_node.id
        canonicalBoard = StateToFeatures.board_to_vector(state_copy.board, state_copy.deck)
        Ps, value = self.nnet.predict(canonicalBoard)
        self.Ps.append(Ps)
        legals = state_copy.board.active_player.get_legal_moves(state_copy.board, state_copy.deck)
        new_node.legal = legals
        valids = StateToFeatures.possible_actions_to_vector(legals, \
            state_copy.board.active_player.player_num, len(state_copy.board.players), self.move_to_index)
        self.Ps[new_node.id] = self.Ps[new_node.id] * valids
        sum_Ps_s = np.sum(self.Ps[new_node.id])
        if sum_Ps_s <= 0:
            # if all valid moves were masked make all valid moves equally probable
            print("All valid moves were masked, do workaround.")
            self.Ps[new_node.id] = self.Ps[new_node.id] + valids
            sum_Ps_s = len(new_node.legal)
        self.Ps[new_node.id] /= sum_Ps_s # renormalize
        if new_node.state.board.active_player.calculate_vp() >= settings.POINTS_TO_WIN:
            new_node.state.winner = new_node.active_player_num
            value = 1
        return new_node, value

    def run_backpropogation(self, leaf_node, leaf_player, value):
        curr_node = leaf_node
        while curr_node.id >= 0:
            node_val = value if leaf_player == curr_node.active_player_num \
            else -value
            self.nodes[curr_node.id].value = (curr_node.plays * curr_node.value + node_val) \
            / (curr_node.plays + 1)
            self.nodes[curr_node.id].plays += 1
            if curr_node.id == 0:
                return
            curr_node = self.nodes[curr_node.parent_id]
