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