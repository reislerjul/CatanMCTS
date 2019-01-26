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


if __name__ == '__main__':
    unittest.main()