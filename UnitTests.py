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

class TestLongestRoad(unittest.TestCase):

    def test_longest_path_single_source(self):
        player_list = [RandomPlayer(1), RandomPlayer(2)]
        settings.init()
        deck = Deck()
        deck.initialize_stack()
        board = Board(player_list)
        board.init_board()

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
        deck.initialize_stack()
        board = Board(player_list)
        board.init_board()

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
        deck.initialize_stack()
        board = Board(player_list)
        board.init_board()

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

    def test_play_dev_human(self):
        user_input = [
            '5', '0', '0 0', # Knight
            '5', '1', # Victory Point
            '5', '2', '0 0', '1 0', '0 0', '1 1', # Road Building
            '5', '3', 'w', # Monopoly
            '5', '4', 'o', 'o', '5', '4', 'w', 'l' # Year of Plenty
        ]
        with patch('builtins.input', side_effect=user_input):
            player_list = [Human(1), RandomPlayer(2)]
            settings.init()
            deck = Deck()
            deck.initialize_stack()
            board = Board(player_list)
            board.init_board()
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

    def test_robber_on_spot(self):
        player_list = [RandomPlayer(1), RandomPlayer(2)]
        settings.init()
        deck = Deck()
        deck.initialize_stack()
        board = Board(player_list)
        board.init_board()
        player_list[0].settlements.append((0, 0))
        board.add_settlement(player_list[0], (0, 0))
        board.move_robber((0, 0))
        board.allocate_resources(11, player_list)
        self.assertEqual(player_list[0].resources['w'], 2)
        self.assertEqual(player_list[0].resources['o'], 0)
        self.assertEqual(player_list[0].resources['l'], 4)
        self.assertEqual(player_list[0].resources['b'], 4)
        self.assertEqual(player_list[0].resources['g'], 2)     

    def test_take_from_deck(self):
        deck = Deck()
        deck.initialize_stack()
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

    def test_places_for_road(self):
        player_list = [RandomPlayer(1)]
        settings.init()
        deck = Deck()
        deck.initialize_stack()
        board = Board(player_list)
        board.init_board()
        player_list[0].settlements.append((0, 0))
        board.add_settlement(player_list[0], (0, 0))
        player_list[0].add_road(board, frozenset([(0, 0), (1, 0)]))
        board.build_road((0, 0), (1, 0), player_list[0])
        board.round_num = 2
        board.active_player = player_list[0]
        player_list[0].has_rolled = True
        player_list[0].resources = {'w': 0, 'b': 1, 'l': 1, 'g': 0, 'o': 0}
        legal_moves = player_list[0].get_legal_moves(board, deck, 0)
        self.assertIn(Move(Move.BUY_ROAD, road=frozenset([(2, 0), (1, 0)])), legal_moves)
        self.assertIn(Move(Move.BUY_ROAD, road=frozenset([(0, 0), (1, 1)])), legal_moves)

    def test_correct_possible_trades(self):
        player_list = [RandomPlayer(1), RandomPlayer(2), RandomPlayer(3)]
        settings.init()
        deck = Deck()
        deck.initialize_stack()
        board = Board(player_list)
        board.init_board()
        board.round_num = 2
        board.active_player = player_list[0]
        player_list[0].has_rolled = True
        player_list[0].resources = {'w': 0, 'b': 1, 'l': 0, 'g': 0, 'o': 0}
        player_list[1].resources = {'w': 2, 'b': 3, 'l': 3, 'g': 0, 'o': 0}
        player_list[2].resources = {'w': 1, 'b': 1, 'l': 0, 'g': 1, 'o': 0}
        legal_moves = player_list[0].get_legal_moves(board, deck, 0)
        self.assertNotIn(Move(Move.PROPOSE_TRADE, give_resource=('b', 1), resource=('o', 1)), legal_moves)
        self.assertNotIn(Move(Move.PROPOSE_TRADE, give_resource=('b', 1), resource=('w', 3)), legal_moves)
        self.assertNotIn(Move(Move.PROPOSE_TRADE, give_resource=('b', 1), resource=('b', 1)), legal_moves)
        self.assertIn(Move(Move.PROPOSE_TRADE, give_resource=('b', 1), resource=('l', 3)), legal_moves)
        self.assertIn(Move(Move.PROPOSE_TRADE, give_resource=('b', 1), resource=('w', 2)), legal_moves)
        self.assertIn(Move(Move.PROPOSE_TRADE, give_resource=('b', 1), resource=('w', 1)), legal_moves)

if __name__ == '__main__':
    unittest.main()