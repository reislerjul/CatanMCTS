import unittest
from Player import Player
from Board import Board
from Deck import Deck
from RandomPlayer import RandomPlayer
from MCTSPlayer import MCTSPlayer
from Human import Human
import settings
from utils import Card
from unittest.mock import patch
from utils import Move
import StateToFeatures

# Use this class to check that cycles are run correctly. Print statements will need 
# to be added to the MCTSAI class
class TestMCTS(unittest.TestCase):
    def test_cycles_work(self):
        player_list = [MCTSPlayer(1, 10), RandomPlayer(2), RandomPlayer(3)]
        settings.init()
        deck = Deck()
        board = Board(player_list, False)
        move = board.active_player.decide_move(board, deck, player_list)

class TestStateToVector(unittest.TestCase):
    def test_board_in_vector_mode(self):
        player_list = [RandomPlayer(1), RandomPlayer(2), RandomPlayer(3)]
        settings.init()
        deck = Deck()
        board = Board(player_list, False)
        player_list[0].add_road(board, ((0, 0), (1, 0)))
        board.add_settlement(player_list[2], (2, 0))
        board.active_player = player_list[1]
        board.round_num = 50
        player_list[0].resources = {'w':10, 'b':10, 'l':10, 'g':10, 'o':10}
        player_list[1].resources = {'w':5, 'b':5, 'l':5, 'g':5, 'o':5}
        board_vect = StateToFeatures.board_to_vector(board, deck)

        # Check a couple spots to make sure they're encoded correctly

        # (2, 0) has no resource
        start = 7 * 18
        for i in range(5):
            self.assertEqual(board_vect[start], 0)
            start += 1
        # (2, 0) has no dice value
        for i in range(2, 13):
            self.assertEqual(board_vect[start], 0)
            start += 1
        # (2, 0) should have 0 for dots
        self.assertEqual(board_vect[start], 0)
        start += 1
        # (2, 0) should have 1 for robber
        self.assertEqual(board_vect[start], 1)

        # (0, 2) has grain
        start = 2 * 18
        for i in range(5):
            if i == 4:
                self.assertEqual(board_vect[start], 1)
            else:
                self.assertEqual(board_vect[start], 0)
            start += 1
        # (0, 2) has dice value 9
        for i in range(2, 13):
            if i == 9:
                self.assertEqual(board_vect[start], 1)
            else:
                self.assertEqual(board_vect[start], 0)
            start += 1
        # dots should be 4
        self.assertEqual(board_vect[start], 4)
        start += 1 
        # no robber
        self.assertEqual(board_vect[start], 0)

        self.assertEqual(board_vect[-1], len(deck.cards_left))
        self.assertEqual(board_vect[-2], 0)
        self.assertEqual(board_vect[-3], 50)

        # Since this is from player 2's perspective, so order should be 
        # [player2, player3, player1]
        start = 668
        for i in range(9):
            self.assertEqual(board_vect[start], 0)
            start += 1
        for i in range(len(settings.roads)):
            self.assertEqual(board_vect[start], 0)
            start += 1
        for i in range(len(settings.vertices)):
            self.assertEqual(board_vect[start], 0)
            start += 1
        # player 2 has 5 of each resource
        for i in range(len(settings.resources)):
            self.assertEqual(board_vect[start], 5)
            start += 1
        for i in range(10):
            self.assertEqual(board_vect[start], 0)
            start += 1
        for i in range(4):
            self.assertEqual(board_vect[start], 0)
            start += 1

        # player 3 should be next. they have one settlement at (2, 0)
        for i in range(9):
            self.assertEqual(board_vect[start], 0)
            start += 1
        for i in range(len(settings.roads)):
            self.assertEqual(board_vect[start], 0)
            start += 1      
        for i in range(len(settings.vertices)):
            # corresponds to (2, 0)
            if i == 7:
                self.assertEqual(board_vect[start], 1)
            else:
                self.assertEqual(board_vect[start], 0)
            start += 1
        # the number of dev cards the player has
        self.assertEqual(board_vect[start], 0)
        start += 1
        self.assertEqual(board_vect[start], sum(player_list[2].resources.values()))
        start += 1
        self.assertEqual(board_vect[start], sum(player_list[2].dev_cards.values()))
        start += 1

        # player 1 should be next. They have 1 road and 50 resources (0,0)(1,0)
        for i in range(9):
            if i == 4:
                self.assertEqual(board_vect[start], 1)
            else:
                self.assertEqual(board_vect[start], 0)
            start += 1
        for i in range(len(settings.roads)):
            if i == 0:
                self.assertEqual(board_vect[start], 1)
            else:
                self.assertEqual(board_vect[start], 0)
            start += 1  
        for i in range(len(settings.vertices)):
            self.assertEqual(board_vect[start], 0)
            start += 1
        self.assertEqual(board_vect[start], 0)
        start += 1
        self.assertEqual(board_vect[start], sum(player_list[0].resources.values()))
        start += 1
        self.assertEqual(board_vect[start], sum(player_list[0].dev_cards.values()))
        start += 1                        
        self.assertEqual(len(board_vect), 1101)

class TestBoardInitialization(unittest.TestCase):
    def test_random_ports(self):
        player_list = [RandomPlayer(1)]
        board = Board(player_list, True)
        edge_vertices = []
        num_ports = 0
        for coord in board.coords.keys():
            if len(board.coords[coord].resource_locs) < 3:
                edge_vertices.append(coord)
        self.assertEqual(len(edge_vertices), 30)
        for vertex in edge_vertices:
            if len(board.coords[vertex].ports) != 0:
                num_ports += 1
                self.assertEqual(len(board.coords[vertex].ports), 1)
                port = list(board.coords[vertex].ports)[0]
                num_neighbors_with_ports = 0
                for neighbor in board.coords[vertex].neighbours:
                    if len(board.coords[neighbor].ports) != 0:
                        num_neighbors_with_ports += 1
                        self.assertEqual(port, list(board.coords[neighbor].ports)[0])
                self.assertEqual(num_neighbors_with_ports, 1)
        self.assertEqual(num_ports, 18)

    def test_hexes_created_properly(self):
        player_list = [RandomPlayer(1)]
        board = Board(player_list, False)
        self.assertEqual({2: [(4, 1)], 3: [(2, 1), (3, 3)], 4: [(1, 0), (2, 3)], 5: [(1, 2), (4, 0)],
                    6: [(1, 1), (4, 2)], 7: [], 8: [(2, 4), (3, 0)], 9: [(0, 2), (3, 2)],
                    10: [(1, 3), (3, 1)], 11: [(0, 0), (2, 2)], 12: [(0, 1)]}, 
                    board.hex)
        board = Board(player_list, True)
        self.assertEqual(len(board.hex[2]), 1)
        self.assertEqual(len(board.hex[3]), 2)
        self.assertEqual(len(board.hex[4]), 2)
        self.assertEqual(len(board.hex[5]), 2)
        self.assertEqual(len(board.hex[6]), 2)
        self.assertEqual(len(board.hex[7]), 0)
        self.assertEqual(len(board.hex[8]), 2)
        self.assertEqual(len(board.hex[9]), 2)
        self.assertEqual(len(board.hex[10]), 2)
        self.assertEqual(len(board.hex[11]), 2)
        self.assertEqual(len(board.hex[12]), 1)

    def test_random_board_correct_number_dice_resources_spots(self):
        trials = [True, False]
        for i in range(len(trials)):
            player_list = [RandomPlayer(1)]
            board = Board(player_list, trials[i])
            self.assertIn((0, 0), board.resources)
            self.assertIn((0, 1), board.resources)
            self.assertIn((0, 2), board.resources)
            self.assertIn((1, 0), board.resources)
            self.assertIn((1, 1), board.resources)
            self.assertIn((1, 2), board.resources)
            self.assertIn((1, 3), board.resources)
            self.assertIn((2, 0), board.resources)
            self.assertIn((2, 1), board.resources)
            self.assertIn((2, 2), board.resources)
            self.assertIn((2, 3), board.resources)
            self.assertIn((2, 4), board.resources)
            self.assertIn((3, 0), board.resources)
            self.assertIn((3, 1), board.resources)
            self.assertIn((3, 2), board.resources)
            self.assertIn((3, 3), board.resources)
            self.assertIn((4, 0), board.resources)
            self.assertIn((4, 1), board.resources)
            self.assertIn((4, 2), board.resources)
            board_items = board.resources.values()
            resource_count = {"l": 0, "g": 0, "w": 0, "b": 0, "o": 0, "n": 0}
            number_count = {}
            for element in board_items:
                resource_count[element[0]] += 1
                if (element[1], element[2]) not in number_count:
                    number_count[(element[1], element[2])] = 1
                else:
                    number_count[(element[1], element[2])] += 1
            self.assertEqual(resource_count["l"], 4)
            self.assertEqual(resource_count["g"], 4)
            self.assertEqual(resource_count["w"], 4)
            self.assertEqual(resource_count["b"], 3)
            self.assertEqual(resource_count["o"], 3)
            self.assertEqual(resource_count["n"], 1)
            self.assertEqual(number_count[(2, 1)], 1)
            self.assertEqual(number_count[(-1, 0)], 1)
            self.assertEqual(number_count[(3, 2)], 2)
            self.assertEqual(number_count[(4, 3)], 2)
            self.assertEqual(number_count[(5, 4)], 2)
            self.assertEqual(number_count[(6, 5)], 2)
            self.assertEqual(number_count[(8, 5)], 2)
            self.assertEqual(number_count[(9, 4)], 2)
            self.assertEqual(number_count[(10, 3)], 2)
            self.assertEqual(number_count[(11, 2)], 2)
            self.assertEqual(number_count[(12, 1)], 1)

class TestLongestRoad(unittest.TestCase):
    def test_longest_path_single_source(self):
        player_list = [RandomPlayer(1), RandomPlayer(2)]
        settings.init()
        deck = Deck()
        board = Board(player_list, False)

        # One road
        player_list[0].add_road(board, frozenset([(1, 0), (2, 0)]))
        board.build_road((1, 0), (2, 0), player_list[0])
        path, seen, reach = board.DFS((1, 0), player_list[0])
        self.assertEqual(len(path), 2)
 
        # Branching paths of equal length 
        player_list[0].add_road(board, frozenset([(2, 0), (3, 0)]))
        board.build_road((2, 0), (3, 0), player_list[0])
        player_list[0].add_road(board, frozenset([(2, 0), (3, 1)]))
        board.build_road((2, 0), (3, 1), player_list[0])
        path, seen, reach = board.DFS((1, 0), player_list[0])
        self.assertEqual(len(path), 3)
      
        # Branching paths where one is longer than other
        player_list[0].add_road(board, frozenset([(3, 1), (4, 1)]))
        board.build_road((3, 1), (4, 1), player_list[0])
        path, seen, reach = board.DFS((1, 0), player_list[0])
        self.assertEqual(len(path), 4)

        # A cycle in the paths
        player_list[0].add_road(board, frozenset([(3, 0), (4, 0)]))
        board.build_road((3, 0), (4, 0), player_list[0])
        player_list[0].add_road(board, frozenset([(4, 0), (5, 1)]))
        board.build_road((4, 0), (5, 1), player_list[0])        
        player_list[0].add_road(board, frozenset([(4, 1), (5, 1)]))
        board.build_road((4, 1), (5, 1), player_list[0])
        player_list[0].add_road(board, frozenset([(4, 0), (5, 0)]))
        board.build_road((4, 0), (5, 0), player_list[0])        
        path, seen, reach = board.DFS((1, 0), player_list[0])
        self.assertEqual(len(path), 8)

        # Another player builds a settlement
        path, seen, reach = board.longest_road_single_source((2, 0), player_list[0])
        self.assertEqual(len(path), 8)
        player_list[1].settlements.append((2, 0))
        board.add_settlement(player_list[1], (2, 0))
        path, seen, reach = board.longest_road_single_source((1, 0), player_list[0])
        self.assertEqual(len(path), 2)
        path, seen, reach = board.longest_road_single_source((2, 0), player_list[0])   
        self.assertEqual(len(path), 7)
        path, seen, reach = board.longest_road_single_source((2, 0), player_list[1])
        self.assertEqual(len(path), 1)
        self.assertEqual(reach, {(2, 0)})

    def test_longest_road_building_roads(self):
        player_list = [RandomPlayer(1), RandomPlayer(2)]
        settings.init()
        deck = Deck()
        board = Board(player_list, False)

        player_list[0].add_road(board, frozenset([(2, 0), (3, 0)]))
        board.build_road((2, 0), (3, 0), player_list[0])
        player_list[0].add_road(board, frozenset([(3, 0), (4, 0)]))
        board.build_road((3, 0), (4, 0), player_list[0])
        player_list[0].add_road(board, frozenset([(4, 0), (5, 1)]))
        board.build_road((4, 0), (5, 1), player_list[0])
        player_list[0].add_road(board, frozenset([(5, 1), (4, 1)]))
        board.build_road((5, 1), (4, 1), player_list[0])    
        self.assertEqual(board.longest_road_player, None)
        self.assertEqual(player_list[0].longest_road, 0)
        player_list[0].add_road(board, frozenset([(4, 1), (3, 1)]))
        board.build_road((4, 1), (3, 1), player_list[0]) 
        self.assertEqual(board.longest_road_player, player_list[0])
        self.assertEqual(player_list[0].longest_road, 2)
        self.assertEqual(board.longest_road_size, 5)
        self.assertEqual(board.longest_road_path, 
            ((2, 0), (3, 0), (4, 0), (5, 1), (4, 1), (3, 1)))
        player_list[0].add_road(board, frozenset([(3, 1), (2, 0)]))
        board.build_road((3, 1), (2, 0), player_list[0]) 
        self.assertEqual(board.longest_road_player, player_list[0])
        self.assertEqual(board.longest_road_size, 6)

        # Shouldn't affect longest road
        player_list[1].settlements.append((3, 1))
        board.add_settlement(player_list[1], (3, 1))
        self.assertEqual(board.longest_road_player, player_list[0])
        self.assertEqual(board.longest_road_size, 6)
        self.assertEqual(board.longest_road_path, 
            ((3, 1), (4, 1), (5, 1), (4, 0), (3, 0), (2, 0), (3, 1)))
        player_list[1].settlements.append((6, 1))
        board.add_settlement(player_list[1], (6, 1))        
        self.assertEqual(board.longest_road_player, player_list[0])
        self.assertEqual(board.longest_road_size, 6)
        self.assertEqual(board.longest_road_path, 
            ((3, 1), (4, 1), (5, 1), (4, 0), (3, 0), (2, 0), (3, 1)))

        # Test player builds settlements that take away longest road
        player_list[1].settlements.append((5, 1))
        board.add_settlement(player_list[1], (5, 1))
        self.assertEqual(board.longest_road_player, None)
        self.assertEqual(board.longest_road_size, 4)
        self.assertEqual(board.longest_road_path, ())
        self.assertEqual(player_list[0].longest_road, 0)
        self.assertEqual(player_list[1].longest_road, 0)

        # Player 1 reclaims longest road
        player_list[0].add_road(board, frozenset([(2, 0), (1, 0)]))
        board.build_road((2, 0), (1, 0), player_list[0])         
        player_list[0].add_road(board, frozenset([(1, 0), (0, 0)]))
        board.build_road((1, 0), (0, 0), player_list[0])     
        self.assertEqual(board.longest_road_player, player_list[0])
        self.assertEqual(board.longest_road_size, 5)
        self.assertEqual(player_list[0].longest_road, 2)
        self.assertEqual(player_list[1].longest_road, 0)

    def test_player_takes_longest_road(self):
        player_list = [RandomPlayer(1), RandomPlayer(2)]
        settings.init()
        deck = Deck()
        board = Board(player_list, False)

        # Longest road
        player_list[0].add_road(board, frozenset([(1, 1), (0, 0)]))
        board.build_road((1, 1), (0, 0), player_list[0])            
        player_list[0].add_road(board, frozenset([(0, 0), (1, 0)]))
        board.build_road((0, 0), (1, 0), player_list[0])    
        player_list[0].add_road(board, frozenset([(1, 0), (2, 0)]))
        board.build_road((1, 0), (2, 0), player_list[0])        
        player_list[0].add_road(board, frozenset([(2, 0), (3, 0)]))
        board.build_road((2, 0), (3, 0), player_list[0])
        player_list[0].add_road(board, frozenset([(3, 0), (4, 0)]))
        board.build_road((3, 0), (4, 0), player_list[0])
        player_list[0].add_road(board, frozenset([(4, 0), (5, 0)]))
        board.build_road((4, 0), (5, 0), player_list[0])
        
        # Another long road that is shorter than longest road
        player_list[0].add_road(board, frozenset([(8, 0), (9, 0)]))
        board.build_road((8, 0), (9, 0), player_list[0]) 
        player_list[0].add_road(board, frozenset([(9, 0), (8, 1)]))
        board.build_road((9, 0), (8, 1), player_list[0])   
        player_list[0].add_road(board, frozenset([(8, 1), (9, 1)]))
        board.build_road((8, 1), (9, 1), player_list[0])    
        player_list[0].add_road(board, frozenset([(9, 1), (8, 2)]))
        board.build_road((9, 1), (8, 2), player_list[0])
        player_list[0].add_road(board, frozenset([(8, 2), (9, 2)]))
        board.build_road((8, 2), (9, 2), player_list[0])

        self.assertEqual(board.longest_road_player, player_list[0])
        self.assertEqual(board.longest_road_size, 6)
        self.assertEqual(player_list[0].longest_road, 2)
        self.assertEqual(player_list[1].longest_road, 0)        

        # Player 2 breaks player 1's longest road, but player 1 
        # will still hold longest road from its other road
        player_list[1].settlements.append((2, 0))
        board.add_settlement(player_list[1], (2, 0))        
        self.assertEqual(board.longest_road_player, player_list[0])
        self.assertEqual(board.longest_road_size, 5)
        self.assertEqual(player_list[0].longest_road, 2)
        self.assertEqual(player_list[1].longest_road, 0)        

        # Player 2 will now take longest road 
        player_list[1].add_road(board, frozenset([(2, 0), (3, 1)]))
        board.build_road((2, 0), (3, 1), player_list[1]) 
        player_list[1].add_road(board, frozenset([(3, 1), (2, 1)]))
        board.build_road((3, 1), (2, 1), player_list[1])    
        player_list[1].add_road(board, frozenset([(2, 1), (3, 2)]))
        board.build_road((2, 1), (3, 2), player_list[1])
        player_list[1].add_road(board, frozenset([(3, 2), (2, 2)]))
        board.build_road((3, 2), (2, 2), player_list[1])        
        player_list[1].add_road(board, frozenset([(2, 2), (3, 3)]))
        board.build_road((2, 2), (3, 3), player_list[1])    
        self.assertEqual(board.longest_road_player, player_list[0])
        self.assertEqual(board.longest_road_size, 5)
        self.assertEqual(player_list[0].longest_road, 2)
        self.assertEqual(player_list[1].longest_road, 0)   
        player_list[1].add_road(board, frozenset([(3, 3), (2, 3)]))
        board.build_road((3, 3), (2, 3), player_list[1])          
        self.assertEqual(board.longest_road_player, player_list[1])
        self.assertEqual(board.longest_road_size, 6)
        self.assertEqual(player_list[0].longest_road, 0)
        self.assertEqual(player_list[1].longest_road, 2)   

class TestPlayDev(unittest.TestCase):
    def test_draw_dev_play_dev_same_turn(self):
        player_list = [RandomPlayer(1)]
        settings.init()
        deck = Deck()
        board = Board(player_list, False)
        board.active_player = player_list[0]
        board.round_num = 2
        player_list[0].resources = {'w':1, 'b':0, 'l':0, 'g':1, 'o':1}
        player_list[0].has_rolled = True

        # After buying a dev card, we cannot play it. 
        move_made = player_list[0].make_move(Move(Move.BUY_DEV, card_type=0, player=1), 
            board, deck, player_list)
        self.assertEqual(move_made, 1)
        self.assertEqual(player_list[0].dev_drawn, 0)
        legal_moves = player_list[0].get_legal_moves(board, deck)
        is_legal = player_list[0].check_legal_move(Move(Move.PLAY_DEV, card_type=0, coord=(0, 0)), board, deck)
        self.assertEqual(is_legal, False)
        self.assertEqual(len(legal_moves), 1)
        self.assertNotEqual(legal_moves[0].move_type, Move.PLAY_DEV)
        self.assertEqual(player_list[0].dev_cards[0], 1)

        # Check that if we have another dev card that is the same as the one drawn, 
        # we can play it
        player_list[0].dev_cards[0] += 1 
        legal_moves = player_list[0].get_legal_moves(board, deck)
        self.assertGreater(len(legal_moves), 1)
        self.assertEqual((legal_moves[1].move_type, legal_moves[1].card_type), (Move.PLAY_DEV, 0))
        is_legal = player_list[0].check_legal_move(Move(Move.PLAY_DEV, card_type=0, coord=(0, 0)), board, deck)
        self.assertEqual(is_legal, True)
        move_made = player_list[0].make_move(Move(Move.PLAY_DEV, card_type=0, coord=(0, 0)), 
            board, deck, player_list)
        self.assertEqual(move_made, 1)
        self.assertEqual(player_list[0].dev_cards[0], 1)
        self.assertEqual(player_list[0].dev_played, 1)

        # Now, end the turn and check that on the next turn, we can play the knight that is left over
        player_list[0].make_move(Move(Move.END_TURN), board, deck, player_list)
        legal_moves = player_list[0].get_legal_moves(board, deck)
        self.assertIn(Move(Move.PLAY_DEV, card_type=0, coord=(1, 0)), legal_moves)
        self.assertNotIn(Move(Move.PLAY_DEV, card_type=0, coord=(0, 0)), legal_moves)
        self.assertEqual(player_list[0].dev_drawn, -1)
        self.assertEqual(player_list[0].dev_played, 0)
        is_legal = player_list[0].check_legal_move(Move(Move.PLAY_DEV, card_type=0, coord=(1, 0)), board, deck)
        self.assertEqual(is_legal, True)
        is_legal = player_list[0].check_legal_move(Move(Move.PLAY_DEV, card_type=0, coord=(0, 0)), board, deck)
        self.assertEqual(is_legal, False)
        move_made = player_list[0].make_move(Move(Move.PLAY_DEV, card_type=0, coord=(1, 0)), 
            board, deck, player_list)
        self.assertEqual(move_made, 1)
        self.assertEqual(player_list[0].dev_played, 1)

    def test_play_dev_human(self):
        user_input = [
            Move.PLAY_DEV, Card.KNIGHT, '0 0', # Knight
            Move.PLAY_DEV, Card.VICTORY_POINT, # Victory Point
            Move.PLAY_DEV, Card.ROAD_BUILDING, '0 0', '1 0', '0 0', '1 1', # Road Building
            Move.PLAY_DEV, Card.MONOPOLY, 'w', # Monopoly
            Move.PLAY_DEV, Card.YEAR_OF_PLENTY, 'o', 'o', '5', '4', 'w', 'l' # Year of Plenty
        ]
        with patch('builtins.input', side_effect=user_input):
            player_list = [Human(1), RandomPlayer(2)]
            settings.init()
            deck = Deck()
            board = Board(player_list, False)
            board.round_num = 2
            board.active_player = player_list[0]
            player_list[0].has_rolled = True
            player_list[0].dev_cards[Card.KNIGHT] = 1
            player_list[0].dev_cards[Card.VICTORY_POINT] = 1
            player_list[0].dev_cards[Card.ROAD_BUILDING] = 1
            player_list[0].dev_cards[Card.MONOPOLY] = 2
            player_list[0].dev_cards[Card.YEAR_OF_PLENTY] = 2

            # Knight
            move = player_list[0].decide_move(board, deck, player_list)
            self.assertEqual(player_list[0].make_move(move, board, deck, player_list), 1)
            self.assertEqual(player_list[0].num_knights_played, 1)
            self.assertEqual(board.robber, (0, 0))
            self.assertEqual(player_list[0].dev_played, 1)

            # Victory Point
            player_list[0].dev_played = 0
            move = player_list[0].decide_move(board, deck, player_list)
            self.assertEqual(move, -1)
            self.assertEqual(player_list[0].dev_played, 0)

            # Road Building
            move = player_list[0].decide_move(board, deck, player_list)
            self.assertEqual(move.road, frozenset([(1, 0), (0, 0)]))
            self.assertEqual(move.road2, frozenset([(0, 0), (1, 1)]))
            move_made = player_list[0].make_move(move, board, deck, player_list)
            self.assertEqual(move_made, -1)
            player_list[0].settlements.append((0, 0))
            move_made = player_list[0].make_move(move, board, deck, player_list)
            self.assertEqual(move_made, 1)
            self.assertEqual(player_list[0].dev_played, 1)

            # Monopoly
            player_list[0].dev_played = 0
            move = player_list[0].decide_move(board, deck, player_list)
            move_made = player_list[0].make_move(move, board, deck, player_list)
            self.assertEqual(move_made, 1)
            self.assertEqual(player_list[0].dev_played, 1)
            self.assertEqual(player_list[0].resources['w'], 4)
            player_list[0].dev_played = 0
            move_made = player_list[0].make_move(move, board, deck, player_list)
            self.assertEqual(move_made, 1)
            self.assertEqual(player_list[0].dev_played, 1)
            self.assertEqual(player_list[0].resources['w'], 4)
            self.assertEqual(player_list[0].resources['o'], 0)
            self.assertEqual(player_list[0].resources['l'], 4)
            self.assertEqual(player_list[0].resources['b'], 4)
            self.assertEqual(player_list[0].resources['g'], 2)

            # Year of Plenty
            player_list[0].dev_played = 0
            move = player_list[0].decide_move(board, deck, player_list)
            move_made = player_list[0].make_move(move, board, deck, player_list)
            self.assertEqual(move_made, 1)
            self.assertEqual(player_list[0].dev_played, 1)
            self.assertEqual(player_list[0].resources['w'], 4)
            self.assertEqual(player_list[0].resources['o'], 2)
            self.assertEqual(player_list[0].resources['l'], 4)
            self.assertEqual(player_list[0].resources['b'], 4)
            self.assertEqual(player_list[0].resources['g'], 2)
            player_list[0].dev_played = 0
            move = player_list[0].decide_move(board, deck, player_list)
            move_made = player_list[0].make_move(move, board, deck, player_list)
            self.assertEqual(move_made, 1)
            self.assertEqual(player_list[0].dev_played, 1)
            self.assertEqual(player_list[0].resources['w'], 5)
            self.assertEqual(player_list[0].resources['o'], 2)
            self.assertEqual(player_list[0].resources['l'], 5)
            self.assertEqual(player_list[0].resources['b'], 4)
            self.assertEqual(player_list[0].resources['g'], 2)  

class TestRobber(unittest.TestCase):
    def test_robber_prevents_resource_allocation(self):
        player_list = [RandomPlayer(1), RandomPlayer(2)]
        settings.init()
        deck = Deck()
        board = Board(player_list, False)
        player_list[0].settlements.append((0, 0))
        board.add_settlement(player_list[0], (0, 0))
        board.move_robber((0, 0))
        board.allocate_resources(11)
        self.assertEqual(player_list[0].resources['w'], 2)
        self.assertEqual(player_list[0].resources['o'], 0)
        self.assertEqual(player_list[0].resources['l'], 4)
        self.assertEqual(player_list[0].resources['b'], 4)
        self.assertEqual(player_list[0].resources['g'], 2) 

class TestSevenRolled(unittest.TestCase):
    def test_less_than_seven_cards(self):
        player_list = [RandomPlayer(1), RandomPlayer(2), RandomPlayer(3)]
        for player in player_list:
            player.resources = {'w':0, 'b':0, 'l':3, 'g':2, 'o':0}
        settings.init()
        deck = Deck()
        board = Board(player_list, False)
        board.round_num = 3
        board.active_player = player_list[0]
        move_made = player_list[0].make_move(Move(Move.ROLL_DICE, roll=7), board, deck, player_list)
        self.assertEqual(move_made, 1)
        self.assertEqual(board.seven_roller, None)
        self.assertEqual(board.active_player, player_list[0])
        self.assertEqual(player_list[0].has_rolled, True)
        self.assertEqual(player_list[0].resources, {'w':0, 'b':0, 'l':3, 'g':2, 'o':0})
        self.assertEqual(player_list[1].resources, {'w':0, 'b':0, 'l':3, 'g':2, 'o':0})
        self.assertEqual(player_list[2].resources, {'w':0, 'b':0, 'l':3, 'g':2, 'o':0})
        legal_moves = player_list[0].get_legal_moves(board, deck)
        for move in legal_moves:
            self.assertEqual(move.move_type, Move.MOVE_ROBBER)

    def test_other_player_has_more_than_seven(self):
        player_list = [RandomPlayer(1), RandomPlayer(2), RandomPlayer(3)]
        for player in player_list:
            player.resources = {'w':0, 'b':0, 'l':3, 'g':2, 'o':0}
        settings.init()
        deck = Deck()
        board = Board(player_list, False)
        board.round_num = 3
        board.active_player = player_list[0]
        player_list[1].resources = {'w':5, 'b':5, 'l':3, 'g':2, 'o':1}
        move_made = player_list[0].make_move(Move(Move.ROLL_DICE, roll=7), board, deck, player_list)
        self.assertEqual(move_made, 1)
        self.assertEqual(board.seven_roller, player_list[0])
        self.assertEqual(board.active_player, player_list[1])
        legal_moves = board.active_player.get_legal_moves(board, deck)
        for move in legal_moves:
            self.assertEqual(move.move_type, Move.DISCARD_HALF)
        decided = board.active_player.decide_move(board, deck, player_list)
        self.assertEqual(decided.move_type, Move.DISCARD_HALF)
        move_made = board.active_player.make_move(decided, board, deck, player_list)
        self.assertEqual(move_made, 1)
        self.assertEqual(board.seven_roller, None)
        self.assertEqual(board.active_player, player_list[0])
        self.assertNotEqual(player_list[1].resources, {'w':5, 'b':5, 'l':3, 'g':2, 'o':1})
        self.assertEqual(sum(player_list[1].resources.values()), 8)

    def test_all_players_more_than_seven(self):
        player_list = [RandomPlayer(1), RandomPlayer(2), RandomPlayer(3)]
        for player in player_list:
            player.resources = {'w':5, 'b':5, 'l':3, 'g':2, 'o':1}
        settings.init()
        deck = Deck()
        board = Board(player_list, False)
        board.round_num = 3
        board.active_player = player_list[0]
        move_made = player_list[0].make_move(Move(Move.ROLL_DICE, roll=7), board, deck, player_list)

        # Player 1 now needs to discard half
        self.assertEqual(move_made, 1)
        self.assertEqual(board.seven_roller, player_list[0])
        self.assertEqual(board.active_player, player_list[0])
        decided = board.active_player.decide_move(board, deck, player_list)
        self.assertEqual(decided.move_type, Move.DISCARD_HALF)
        move_made = board.active_player.make_move(decided, board, deck, player_list)
        self.assertEqual(move_made, 1)
        self.assertEqual(board.seven_roller, player_list[0])
        self.assertEqual(board.active_player, player_list[1])

        # Player 2 needs to discard half
        decided = board.active_player.decide_move(board, deck, player_list)
        self.assertEqual(decided.move_type, Move.DISCARD_HALF)
        move_made = board.active_player.make_move(decided, board, deck, player_list)
        self.assertEqual(move_made, 1)
        self.assertEqual(board.seven_roller, player_list[0])
        self.assertEqual(board.active_player, player_list[2])

        # Player 3 needs to discard half
        decided = board.active_player.decide_move(board, deck, player_list)
        self.assertEqual(decided.move_type, Move.DISCARD_HALF)
        move_made = board.active_player.make_move(decided, board, deck, player_list)
        self.assertEqual(move_made, 1)
        self.assertEqual(board.seven_roller, None)
        self.assertEqual(board.active_player, player_list[0])    

        for player in player_list: 
            self.assertEqual(sum(player.resources.values()), 8)

        # Make sure were at player 1 and they now need to move the robber
        legal_moves = board.active_player.get_legal_moves(board, deck)
        for move in legal_moves:
            self.assertEqual(move.move_type, Move.MOVE_ROBBER)

class TestDevCardDeck(unittest.TestCase):
    def test_take_from_deck(self):
        deck = Deck()
        num_knights = 0
        num_vp = 0
        num_rb = 0
        num_mon = 0
        num_yop = 0
        num_other = 0
        for i in range(25):
            card = deck.take_card(deck.peek())
            if card == Card.KNIGHT:
                num_knights += 1
            elif card == Card.VICTORY_POINT:
                num_vp += 1
            elif card == Card.ROAD_BUILDING:
                num_rb += 1
            elif card == Card.MONOPOLY:
                num_mon += 1
            elif card == Card.YEAR_OF_PLENTY:
                num_yop += 1
            else:
                num_other += 1
        self.assertEqual(num_knights, 14)
        self.assertEqual(num_vp, 5)
        self.assertEqual(num_rb, 2)
        self.assertEqual(num_mon, 2)
        self.assertEqual(num_yop, 2)
        self.assertEqual(num_other, 0)
        self.assertEqual(deck.take_card(deck.peek()), -1)

class TestCanBuildRoads(unittest.TestCase):
    def test_places_for_road(self):
        player_list = [RandomPlayer(1)]
        settings.init()
        deck = Deck()
        board = Board(player_list, False)
        player_list[0].settlements.append((0, 0))
        board.add_settlement(player_list[0], (0, 0))
        player_list[0].add_road(board, frozenset([(0, 0), (1, 0)]))
        board.build_road((0, 0), (1, 0), player_list[0])
        board.round_num = 2
        board.active_player = player_list[0]
        player_list[0].has_rolled = True
        player_list[0].resources = {'w': 0, 'b': 1, 'l': 1, 'g': 0, 'o': 0}
        legal_moves = player_list[0].get_legal_moves(board, deck)
        self.assertIn(Move(Move.BUY_ROAD, road=frozenset([(2, 0), (1, 0)])), legal_moves)
        self.assertIn(Move(Move.BUY_ROAD, road=frozenset([(0, 0), (1, 1)])), legal_moves)

class TestTradeBetweenPlayers(unittest.TestCase):
    def test_correct_possible_trades(self):
        player_list = [RandomPlayer(1), RandomPlayer(2), RandomPlayer(3)]
        settings.init()
        deck = Deck()
        board = Board(player_list, False)
        board.round_num = 2
        board.active_player = player_list[0]
        player_list[0].has_rolled = True
        player_list[0].resources = {'w': 0, 'b': 1, 'l': 0, 'g': 0, 'o': 0}
        player_list[1].resources = {'w': 2, 'b': 3, 'l': 3, 'g': 0, 'o': 0}
        player_list[2].resources = {'w': 1, 'b': 1, 'l': 0, 'g': 1, 'o': 0}
        legal_moves = player_list[0].get_legal_moves(board, deck)
        self.assertNotIn(Move(Move.PROPOSE_TRADE, give_resource=('b', 1), resource=('o', 1), 
            player=player_list[0].player_num), legal_moves)
        self.assertNotIn(Move(Move.PROPOSE_TRADE, give_resource=('b', 1), resource=('w', 3), 
            player=player_list[0].player_num), legal_moves)
        self.assertNotIn(Move(Move.PROPOSE_TRADE, give_resource=('b', 1), resource=('b', 1), 
            player=player_list[0].player_num), legal_moves)
        self.assertIn(Move(Move.PROPOSE_TRADE, give_resource=('b', 1), resource=('l', 3), 
            player=player_list[0].player_num), legal_moves)
        self.assertIn(Move(Move.PROPOSE_TRADE, give_resource=('b', 1), resource=('w', 2), 
            player=player_list[0].player_num), legal_moves)
        self.assertIn(Move(Move.PROPOSE_TRADE, give_resource=('b', 1), resource=('w', 1), 
            player=player_list[0].player_num), legal_moves)

class TestTradeWithBank(unittest.TestCase):
    def test_trade_bank(self):
        player_list = [RandomPlayer(1)]
        settings.init()
        deck = Deck()
        board = Board(player_list, False)
        board.active_player = player_list[0]
        board.round_num = 2
        player_list[0].resources = {'w':2, 'b':2, 'l':3, 'g':3, 'o':3}
        player_list[0].has_rolled = True

        # Cannot trade
        legal_moves = player_list[0].get_legal_moves(board, deck)
        for move in legal_moves:
            self.assertNotEqual(move.move_type, Move.TRADE_BANK)

        # Can only trade w 
        player_list[0].ports.append('2 w')
        legal_moves = player_list[0].get_legal_moves(board, deck)
        for move in legal_moves:
            if move.move_type == Move.TRADE_BANK:
                self.assertEqual(player_list[0].check_legal_move(move, board, deck), True)
                self.assertEqual(move.give_resource, 'w')
        self.assertIn(Move(Move.TRADE_BANK, give_resource='w', resource='b'), legal_moves)
        self.assertIn(Move(Move.TRADE_BANK, give_resource='w', resource='l'), legal_moves)
        self.assertIn(Move(Move.TRADE_BANK, give_resource='w', resource='g'), legal_moves)
        self.assertIn(Move(Move.TRADE_BANK, give_resource='w', resource='o'), legal_moves)
        self.assertNotIn(Move(Move.TRADE_BANK, give_resource='w', resource='w'), legal_moves)

        # can trade things with 2, 3, and 4
        trades_l = 0
        trades_g = 0
        trades_o = 0
        player_list[0].ports = ['3', '2 l']
        player_list[0].resources = {'w':0, 'b':0, 'l':2, 'g':3, 'o':4}
        legal_moves = player_list[0].get_legal_moves(board, deck)
        for move in legal_moves:
            if move.move_type == Move.TRADE_BANK:
                self.assertEqual(player_list[0].check_legal_move(move, board, deck), True)
                self.assertIn(move.give_resource, ['l', 'g', 'o'])
                if move.give_resource == 'l':
                    trades_l += 1
                    self.assertIn(move.resource, ['w', 'b', 'g', 'o'])
                elif move.give_resource == 'g':
                    trades_g += 1
                    self.assertIn(move.resource, ['w', 'b', 'l', 'o'])
                elif move.give_resource == 'o':
                    trades_o += 1
                    self.assertIn(move.resource, ['w', 'b', 'l', 'g'])
        self.assertEqual(trades_l, 4)
        self.assertEqual(trades_o, 4)
        self.assertEqual(trades_g, 4)
        player_list[0].make_move(Move(Move.TRADE_BANK, give_resource='l', resource='w'), 
            board, deck, player_list)
        self.assertEqual(player_list[0].resources['w'], 1)
        self.assertEqual(player_list[0].resources['l'], 0)
        player_list[0].make_move(Move(Move.TRADE_BANK, give_resource='g', resource='w'), 
            board, deck, player_list)
        self.assertEqual(player_list[0].resources['w'], 2)
        self.assertEqual(player_list[0].resources['g'], 0)
        player_list[0].make_move(Move(Move.TRADE_BANK, give_resource='o', resource='w'), 
            board, deck, player_list)        
        self.assertEqual(player_list[0].resources['w'], 3)
        self.assertEqual(player_list[0].resources['o'], 1)

        # Test trading 4
        player_list[0].ports = ['2 b']
        player_list[0].trades_tried = 0
        player_list[0].resources = {'w':0, 'b':0, 'l':2, 'g':3, 'o':5} 
        trades = 0  
        legal_moves = player_list[0].get_legal_moves(board, deck)
        for move in legal_moves:
            if move.move_type == Move.TRADE_BANK:
                self.assertEqual(player_list[0].check_legal_move(move, board, deck), True)
                self.assertEqual(move.give_resource, 'o')      
                trades += 1
        self.assertEqual(trades, 4)
        player_list[0].make_move(Move(Move.TRADE_BANK, give_resource='o', resource='w'), 
            board, deck, player_list)            
        self.assertEqual(player_list[0].resources['w'], 1)
        self.assertEqual(player_list[0].resources['o'], 1)   
        self.assertEqual(player_list[0].check_legal_move(Move(Move.TRADE_BANK, 
            give_resource='b', resource='w'), board, deck), False)              

if __name__ == '__main__':
    unittest.main()