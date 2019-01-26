import copy
import random
import settings

from MCTSAI import MCTSAI
from Player import Player
from utils import Card, Move
import sys


class Human(Player):
    def __init__(self, player_num):
        super().__init__(Player.HUMAN, player_num)

    def print_invalid_move(self):
        return True

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
        full_string = "Choose " + string + " card: (w, o, g, b, l)"
        return input(full_string)

    def choose_spot_settlement(self, board):
        legal_settlement = False
        while not legal_settlement:
            # Pick a legal spot
            loc = self.build_settlement(board)
            legal_settlement = self.can_build_settlement(loc, board)
            if not legal_settlement:
                print("Not a legal settlement! Try again.")
        move = Move(Move.BUY_SETTLEMENT, coord=loc)
        return move

    def choose_spot_road(self, board):
        legal_road = False
        while not legal_road:
            loc = self.choose_road(board)
            move = Move(Move.BUY_ROAD, road=loc)
            legal_road = self.can_build_road(move, board)
            if not legal_road:
                print("Not a legal road! Try again.")
        return move

    def decide_move(self, board, deck, players):
            if board.round_num == 0 and len(self.settlements) == 0:
                return self.choose_spot_settlement(board)
            elif board.round_num == 0 and self.total_roads == 0:
                return self.choose_spot_road(board)
            elif board.round_num == 0:
                return Move(Move.END_TURN)
            elif board.round_num == 1 and len(self.settlements) == 1:
                return self.choose_spot_settlement(board)
            elif board.round_num == 1 and self.total_roads == 1:
                return self.choose_spot_road(board)
            elif board.round_num == 1:
                return Move(Move.END_TURN)

            if board.active_player.player_num != self.player_num:
                if self.should_accept_trade(board.pending_trade.give_resource, 
                    board.pending_trade.resource, board, deck, players):
                    return Move(Move.ACCEPT_TRADE)
                return Move(Move.DECLINE_TRADE)

            if not self.has_rolled:
                roll = random.randint(1, 6) + random.randint(1, 6)
                if roll == 7:
                    self.move_robber = True
                return Move(Move.ROLL_DICE, roll=roll, player=self)

            if self.move_robber:
                r,c = map(int, input("Where are you moving the robber? (Input form: row# col#): ").split())
                spot = (r, c)
                victim = self.choose_victim(board, spot)
                return Move(Move.MOVE_ROBBER, coord=spot, player=victim)

            if board.trade_step == 1:
                trade_player_index = self.player_num % len(board.players)
                trade_player = board.players[trade_player_index]
                while trade_player != self:
                    trade_move = trade_player.decide_move(board, deck, board.players)
                    move_made = trade_player.make_move(trade_move, board, deck, board.players)
                    trade_player_index = (trade_player_index + 1) % len(board.players)
                    trade_player = board.players[trade_player_index]
                return Move(Move.ASK_TRADE, player=tuple(board.traders))

            if board.pending_trade:
                return self.choose_trader(board.traders)

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

            move_type = int(input('Select move: '))
            if not ((move_type == Move.PLAY_DEV and self.dev_played > 0) or (move_type == Move.PROPOSE_TRADE and self.trades_tried > 1)):
                # Let's decide on the specific places to move in this
                # function so that we can abstract make_move to work for
                # both AI and human players
                if move_type == Move.END_TURN:
                    return Move(Move.END_TURN)

                elif move_type == Move.BUY_ROAD:
                    return Move(Move.BUY_ROAD, road=self.choose_road(board))

                elif move_type == Move.BUY_SETTLEMENT:
                    return Move(Move.BUY_SETTLEMENT, coord=self.build_settlement(board))

                elif move_type == Move.BUY_CITY:
                    return Move(Move.BUY_CITY, coord=self.build_city(board))

                elif move_type == Move.BUY_DEV:
                    card = deck.peek()
                    return Move(Move.BUY_DEV, card_type=card, player=self.player_num)

                elif move_type == Move.PLAY_DEV:
                    move = Move(Move.PLAY_DEV)
                    dev_card = int(input("Choose dev card to play: (0 for Knight, 2 for Road Building, 3 for Monopoly, 4 for Year of Plenty)"))
                    move.card_type = dev_card
                    if dev_card == Card.KNIGHT:
                        spot = self.choose_robber_position(board, players, deck)
                        victim = self.choose_victim(board, spot)
                        move.coord = spot
                        move.player = victim
                    elif dev_card == Card.ROAD_BUILDING:
                        move.road = self.choose_road(board)
                        move.road2 = self.choose_road(board)
                    elif dev_card == Card.MONOPOLY:
                        card = self.choose_card("Monopoly")
                        move.resource = card
                    elif dev_card == Card.YEAR_OF_PLENTY:
                        move.resource = self.choose_card("Year of Plenty")
                        move.resource2 = self.choose_card("Year of Plenty")
                    elif dev_card == Card.VICTORY_POINT:
                        return -1
                    return move

                elif move_type == Move.TRADE_BANK:
                    return self.trade(board)

                elif move_type == Move.PROPOSE_TRADE:
                    maps = self.trade_other_players()
                    if maps != None:
                        move = Move(Move.PROPOSE_TRADE, give_resource=maps[0], resource=maps[1])
                        return move
                return -1
            else:
                print("You have already played a dev card in this round or have reached maximum allowed trades")
            return -1
            print("The following error was thrown: ", sys.exc_info()[0])
            print("please retry the move")
            return -1

    def choose_road(self, board):
        r0,c0 = map(int, input("Coordinate for road beginning/origin (Input form: row# col#): ").split())
        r1,c1 = map(int, input("Coordinate for road end (Input form: row# col#): ").split())
        print('Building road from ({}, {}) to ({}, {}) ...'.format(r0, c0, r1, c1))
        move = set()
        move.add((r0, c0))
        move.add((r1, c1))
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
        move = input("Which dev card do you want to play (Choose from: Knight, Road Building, Monopoly, Year of Plenty): ")
        print('Playing dev card ...')
        return move

    def trade(self, board):
        numCards = int(input("How many cards do you want to trade?"))
        card = input("Lumber, Ore, Wool, Brick, or Grain? (Input form: l, o, w, b, g)")
        newRes = input("Which resource would you like in exchange? (Input form: l, o, w, b, g)")
        return Move(Move.TRADE_BANK, num_trade=numCards, give_resource=card, resource=newRes)    

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
            return None

    def should_accept_trade(self, receive, give, board, deck, players):
        if self.can_accept_trade(give):
            print("Player " + str(self.player_num))
            accept = input("Accept the following trade? (0 or 1)\nYou'd receive: {}\nYou'd give: {}\n".format(receive, give))
            return int(accept)
        return 0

    def choose_trader(self, traders):
        while True:
            print("Below players are available to trade.")
            for trader in traders:
                print("Player {}".format(trader.player_num))
            choice = int(input("Which player do you want to trade with? Input -1 to cancel the trade."))
            if choice == -1:
                return Move(Move.CHOOSE_TRADER, player=None)
            for trader in traders:
                if trader.player_num == choice:
                    return Move(Move.CHOOSE_TRADER, player=trader)
            print("That player is not available to trade! Choose another player.")

    def to_string(self):
        return "Human"
