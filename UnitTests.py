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
            '5',
            '0',
            '0 0'
        ]
        with patch('builtins.input', side_effect=user_input):
            player_list = [Human(1)]
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
            player_list[0].dev_cards[Card.YEAR_OF_PLENTY] = 1
            move = player_list[0].decide_move(board, deck, player_list)
            self.assertEqual(player_list[0].make_move(move, board, deck, player_list), 1)

if __name__ == '__main__':
    unittest.main()