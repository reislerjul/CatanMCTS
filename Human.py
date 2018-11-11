import copy
import random
import settings

from MCTSAI import MCTSAI
from Player import Player
from utils import Card, Move


class Human(Player):


    def __init__(self, player_num):
        super().__init__(Player.HUMAN, player_num)


    def print_invalid_move(self):
        return True


    def choose_spot(self, board, idx):
        legal_settlement = False
        legal_road = False

        while not legal_settlement:

            # Pick a legal spot
            loc = self.build_settlement(board)

            legal_settlement = self.can_build_settlement(loc, board)

        # Add the settlement to the board and update player fields
        super().add_settlement(board, loc, idx)

        # Choose where to play a road
        while not legal_road:

            move = self.build_road(board)
            legal_road = self.can_build_road(move, board)

        # build the road
        super().add_road(board, move)


    # A helper function for moving the robber in the case of rolling a 7
    def move_robber(self, board, spot, victim, deck, players):
        while True:
            move = Move(Move.MOVE_ROBBER, coord=spot, player=victim)
            invalid = self.make_move(move, board, deck, players)
            if invalid == 1:
                return


    def choose_victim(self, board, move):
        victim = None

        # Determine the players adjacent to the robber
        possible_players = [p for p in board.players_adjacent_to_hex(move) if p is not self]

        # Get a list of the player numbers
        player_nums = [p.player_num for p in possible_players]

        if len(possible_players) > 0:

            # Keep prompting the person until they enter a valid victim
            while True:
                num = int(input("Who do you want to steal from? (give player number)"))

                if num in player_nums:
                    victim = possible_players[player_nums.index(num)]
                    break
                else:
                    print("Invalid victim. Please enter a valid player to steal from.")

        return victim


    # Three arguments aren't used, but we have them here because they're used for MCTSPlayer
    def choose_robber_position(self, board, players, deck):
        r,c = map(int, input("Where are you moving the robber? (Input form: row# col#): ").split())
        return (r, c)


    def choose_card(self, string):
        full_string = "Choose " + string + " card"
        return input(full_string)


    def decide_move(self, dev_played, board, deck, players, robber, trades_tried):
        self.printResources()
        print('Moves available:')
        print('Enter {} for ending/passing your turn'.format(Move.END_TURN))
        print('Enter {} to build a road'.format(Move.BUY_ROAD))
        print('Enter {} to build a settlement'.format(Move.BUY_SETTLEMENT))
        print('Enter {} to build a city'.format(Move.BUY_CITY))
        print('Enter {} to draw a dev card'.format(Move.BUY_DEV))
        print('Enter {} to play a dev card'.format(Move.PLAY_DEV))
        print('Enter {} to make a trade with bank'.format(Move.TRADE_BANK))
        print('Enter {} to propose a trade with other players'.format(Move.PROPOSE_TRADE))
        if robber:
            r,c = map(int, input("Where are you moving the robber? (Input form: row# col#): ").split())
            spot = (r, c)
            victim = self.choose_victim(board, spot)
            self.move_robber(board, spot, victim, deck, players)
        move_type = int(input('Select move: '))
        if not ((move_type == Move.PLAY_DEV and dev_played > 0) or (move_type == Move.PROPOSE_TRADE and trades_tried > 1)):

            # Let's decide on the specific places to move in this
            # function so that we can abstract make_move to work for
            # both AI and human players
            if move_type == Move.END_TURN:
                return Move(Move.END_TURN)

            elif move_type == Move.BUY_ROAD:
                return Move(Move.BUY_ROAD, self.build_road(board))

            elif move_type == Move.BUY_SETTLEMENT:
                return Move(Move.BUY_SETTLEMENT, self.build_settlement(board))

            elif move_type == Move.BUY_CITY:
                return Move(Move.BUY_CITY, self.build_city(board))

            elif move_type == Move.BUY_DEV:
                return Move(Move.BUY_DEV)

            elif move_type == Move.PLAY_DEV:
                return Move(Move.PLAY_DEV, self.playDevCard(board))

            elif move_type == Move.TRADE_BANK:
                return Move(Move.TRADE_BANK, self.trade(board))

            elif move_type == Move.PROPOSE_TRADE:
                maps = self.trade_other_players()
                move = Move(Move.PROPOSE_TRADE, give_resource=maps[0], resource=maps[1])
                return move
            return move_type
        else:
            print("You have already played a dev card in this round or have reached maximum allowed trades")

    def choose_road(self, board, deck, players):
        r0,c0 = map(int, input("Coordinate for road beginning/origin (Input form: row# col#): ").split())
        r1,c1 = map(int, input("Coordinate for road end (Input form: row# col#): ").split())
        print('Building road from ({}, {}) to ({}, {}) ...'.format(r0, c0, r1, c1))
        move = ((r0, c0), (r1, c1))
        return move     # List of tuples: two coordinates


    def build_settlement(self, board):
        r,c = map(int, input("Coordinate for settlement (Input form: row# col#): ").split())
        print('Building settlement at ({}, {}) ...'.format(r, c))

        move = (r, c)
        return move     # Tuple: one coordinate


    def build_city(self, board):
        r,c = map(int, input("Coordinate for city (Input form: row# col#): ").split())
        print('Building city at ({}, {}) ...'.format(r, c))

        move = (r, c)
        return move     # Tuple: one coordinate


    def playDevCard(self, board):
        move = input("Which dev card do you want to play (Choose from form: Knight, Road Building, Monopoly, Year of Plenty): ")
        print('Playing dev card ...')
        return move



    def trade(self, board):
        numCards = input("How many cards do you want to trade?")
        card = input("Lumber, Ore, Wool, Brick, or Grain? (Input form: l, o, w, b, g)")
        oldRes = (numCards, card)
        newRes = input("Which resource would you like in exchange? (Input form: l, o, w, b, g)")
        move = (oldRes, newRes)
        return move     # Tuple of tuple: Trade of multiple cards for one card


    def trade_other_players(self):
        while True:
            losses = input("What do you want to trade? (Input form: Num-Card) (Ex: 1-w)")
            gains = input("What should others trade to you? (Input form: Num-Card) (Ex: 1-w)")
            loss_array = losses.split()
            for element in loss_array:
                loss_map = (element[2], element[0])
            gain_array = gains.split()
            for element in gain_array:
                gain_map = (element[2], element[0])
            if self.can_accept_trade(loss_map):
                return (loss_map, gain_map)
            print("You don't have the resources for that trade! Try again.")


    def should_accept_trade(self, receive, give, board, deck, players):
        options = [0]
        if self.can_accept_trade(give):
            accept = input("Accept the following trade? (0 or 1)\nYou'd receive: {}\nYou'd give: {}\n".format(receive, give))
            return int(accept)
        return 0


    def choose_trader(self, traders):
        while True:
            print("Below players are available to trade.")
            for trader in traders:
                print("Player {}".format(trader.player_num))
            choice = int(input("Which player do you want to trade with? "))
            for trader in traders:
                if trader.player_num == choice:
                    return trader
            print("That player is not available to trade! Choose another player.")

