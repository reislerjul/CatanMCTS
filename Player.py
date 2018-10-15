import copy
import random
import settings

from MCTSAI import MCTSAI
from Deck import Card

class Move():
    END_TURN = 0
    BUY_ROAD = 1
    BUY_SETTLEMENT = 2
    BUY_CITY = 3
    BUY_DEV = 4
    PLAY_DEV = 5
    TRADE_BANK = 6
    MOVE_ROBBER = 7

    def __init__(self,\
                 move_type,\
                 card_type=None,\
                 road=None,\
                 coord=None,\
                 player=None,\
                 num_trade=None,\
                 give_resource=None,\
                 resource=None):
        self.move_type = move_type
        if card_type:
            self.card_type = card_type
        if road:
            self.road = road
        if coord:
            self.coord = coord
        if player:
            self.player = player
        if num_trade:
            self.num_trade = num_trade
        if give_resource:
            self.give_resource = give_resource
        if resource:
            self.resource = resource

# The player class. Each player should keep track of their roads, cities,
# settlements, dev cards, whether they're on a port, number of victory
# points, and resource cards.
class Player():
    HUMAN = 0
    RANDOM_AI = 1

    # TODO: Complete this constructor. player_type should be 0 if the player is
    # human, 1 if the player is the random AI, and 2 if the player is the
    # MCTS AI with random choice of moves and 3 is MCTS AI with weighted choice
    def __init__(self, player_type, player_num):
        self.player_num = player_num
        self.resources = {'w':0, 'b':0, 'l':0, 'g':0, 'o':0}
        self.dev_cards = {Card.KNIGHT: 0,\
                          Card.VICTORY_POINT: 0,\
                          Card.ROAD_BUILDING:0,\
                          Card.MONOPOLY: 0,\
                          Card.YEAR_OF_PLENTY: 0} #{type: #cards}
        self.num_knights_played = 0
        self.longest_road = 0
        self.largest_army = 0
        self.player_type = player_type
        self.ports = []         # {}
        self.cities = []        # [(0,0), (1,1)...]
        self.settlements = []   #[(0,0), (1,1)...]
        self.roads = {}         # {(0,0):(1,1), (1,1):(0,0)...}
        self.total_roads = 0

    # When in debug mode, use this function to print out the player's fields in a
    # readable way.
    def printResources(self):
        print("\nPlayer {}".format(self.player_num))
        print('Resources: {}'.format(self.resources))
        print("     w: {}".format(self.resources['w']))
        print("     l: {}".format(self.resources['l']))
        print("     b: {}".format(self.resources['b']))
        print("     o: {}".format(self.resources['o']))
        print("     g: {}".format(self.resources['g']))

        total_resources = sum(self.resrouces.values())
        print("Total Resources: {}".format(total_resources))

        print("Total Roads: {}".format(self.total_roads))
        print('Dev Cards: {}'.format(self.dev_cards))
        print("     Knights: {}".format(self.dev_cards[Card.KNIGHT]))
        print("     Victory Point: {}".format(self.dev_cards[Card.VICTORY_POINT]))
        print("     Road Building: {}".format(self.dev_cards[Card.ROAD_BUILDING]))
        print("     Monopoly: {}".format(self.dev_cards[Card.MONOPOLY]))
        print("     Year of Plenty: {}".format(self.dev_cards[Card.YEAR_OF_PLENTY]))
        print("Longest Road Points: {}".format(self.longest_road))
        print("Largest Army Points: {}".format(self.largest_army))

        print('Number of Victory Points: {}'.format(self.calculate_vp()))
        print('Knights Played: {}'.format(self.num_knights_played))
        print('Roads: {}'.format(self.roads))
        print('Settlements: {}'.format(self.settlements))
        print('Cities: {}'.format(self.cities))
        print("Ports: {}".format(self.ports))
        return 0


    # A helper function used to get a list of all the legal moves. If weighted, we
    # weight better moves so we have a higher chance of choosing them.
    def get_legal_moves(self, board, deck, dev_played, robber, weighted):
            # Determine moves we can play and add them to the list.

            # We can always end our turn
            possible_moves = [Move(Move.END_TURN)]

            # Can we buy dev card?
            if self.resources['g'] > 0 and self.resources['w'] > 0 \
            and self.resources['o'] > 0 and deck.cards_left > 0:
                if weighted:
                    for i in range(10):
                        possible_moves.append(Move(Move.BUY_DEV))
                else:
                    possible_moves.append(Move(Move.BUY_DEV))

            # Can we play a dev card?
            if dev_played == 0:
                for card in self.dev_cards.keys():
                    if self.dev_cards[card] > 0:
                        if card == Card.KNIGHT:
                            possible_moves = []
                            spots = [(4, 1), (2, 1), (3, 3), (1, 0), (2, 3), (1, 2), (4, 0), \
                                     (1, 1), (4, 2), (2, 4), (3, 0), (0, 2), (3, 2), (1, 3), \
                                     (3, 1), (0, 0), (2, 2), (0, 1)]
                            for spot in spots:
                                possible_players = [p for p in board.players_adjacent_to_hex(spot) if self is not p]

                                # Get a list of the player numbers
                                player_nums = [player.player_num for player in possible_players]

                                if len(player_nums) > 0:
                                    for p in player_nums:
                                        if weighted:
                                            for i in range(10):
                                                possible_moves.append(Move(Move.PLAY_DEV, card_type=card, coord=spot, player=p))
                                        else:
                                            possible_moves.append(Move(Move.PLAY_DEV, card_type=card, coord=spot, player=p))
                                else:
                                    if weighted:
                                        for i in range(10):
                                            possible_moves.append(Move(Move.PLAY_DEV, card_type=card, coord=spot))
                                    else:
                                        possible_moves.append(Move(Move.PLAY_DEV, card_type=card, coord=spot))
                        elif card == Card.ROAD_BUILDING:
                            # Get the set of possible places we can build a road
                            possible_roads = {}

                            for road_source in list(self.roads.keys()):
                                possible_sinks = board.coords[road_source].available_roads

                                for sink in possible_sinks:
                                    if (road_source, sink) not in possible_roads and \
                                            (sink, road_source) not in possible_roads:
                                        possible_roads[(sink, road_source)] = True

                            # We now have the possible roads, so lets add those moves!
                            for road in possible_roads:
                                if weighted:
                                    for i in range(10):
                                        possible_moves.append(Move(Move.PLAY_DEV, card_type=card, road=road))
                                else:
                                    possible_moves.append(Move(Move.PLAY_DEV, card_type=card, road=road))
                        elif card == Card.MONOPOLY:
                            for r in board.resource_list:
                                if weighted:
                                    for i in range(10):
                                        possible_moves.append(Move(Move.PLAY_DEV, card_type=card, resource=r))
                                else:
                                    possible_moves.append(Move(Move.PLAY_DEV, card_type=card, resource=r))
                        elif card == Card.YEAR_OF_PLENTY:
                            if weighted:
                                for i in range(10):
                                    possible_moves.append(Move(Move.PLAY_DEV, card_type=card))
                            else:
                                possible_moves.append(Move(Move.PLAY_DEV, card_type=card))

            # Can we build a city?
            if self.resources['g'] >= 2 and self.resources['o'] >= 3 and \
            len(self.cities) < 4:
                for settlement in self.settlements:

                    if weighted:
                        for i in range(1000):
                            possible_moves.append(Move(Move.BUY_CITY, coord=settlement))
                    else:
                        possible_moves.append(Move(Move.BUY_CITY, coord=settlement))

            # Can we build a road?
            if self.resources['b'] > 0 and self.resources['l'] > 0 and self.total_roads < 15:
                # Get the set of possible places we can build a road
                possible_roads = {}

                for road_source in list(self.roads.keys()):
                    possible_sinks = board.coords[road_source].available_roads

                    for sink in possible_sinks:
                        if (road_source, sink) not in possible_roads and \
                                (sink, road_source) not in possible_roads:
                            possible_roads[(sink, road_source)] = True

                # We now have the possible roads, so lets add those moves!
                for road in possible_roads:
                    possible_moves.append(Move(Move.BUY_ROAD, road=road))

            # Can we build a settlement?
            if self.resources['w'] > 0 and self.resources['l'] > 0 and \
            self.resources['b'] > 0 and self.resources['g'] > 0 and \
            len(self.settlements) < 5:

                # Check the possible places for us to build a settlement
                for source in list(self.roads.keys()):
                    if (self.can_build_settlement(source, board)):

                        if weighted:
                            for i in range(1000):
                                possible_moves.append(Move(Move.BUY_SETTLEMENT, coord=source))
                        else:
                            possible_moves.append(Move(Move.BUY_SETTLEMENT, coord=source))

            # Should we trade in resources? Try cases for the 5 different resources
            if (self.resources['w'] >= 2 and '2 w' in self.ports) or \
            (self.resources['w'] >= 3 and '3' in self.ports) or (self.resources['w'] >= 4):
                if (self.resources['w'] >= 2 and '2 w' in self.ports):
                    numTrade = '2'
                elif (self.resources['w'] >= 3 and '3' in self.ports):
                    numTrade = '3'
                else:
                    numTrade = '4'
                possible_moves.append(Move(Move.TRADE_BANK, num_trade=numTrade, give_resource='w', resource='o'))
                possible_moves.append(Move(Move.TRADE_BANK, num_trade=numTrade, give_resource='w', resource='l'))
                possible_moves.append(Move(Move.TRADE_BANK, num_trade=numTrade, give_resource='w', resource='g'))
                possible_moves.append(Move(Move.TRADE_BANK, num_trade=numTrade, give_resource='w', resource='b'))

            if (self.resources['o'] >= 2 and '2 o' in self.ports) or \
            (self.resources['o'] >= 3 and '3' in self.ports) or (self.resources['o'] >= 4):
                if (self.resources['o'] >= 2 and '2 o' in self.ports):
                    numTrade = '2'
                elif (self.resources['o'] >= 3 and '3' in self.ports):
                    numTrade = '3'
                else:
                    numTrade = '4'
                possible_moves.append(Move(Move.TRADE_BANK, num_trade=numTrade, give_resource='o', resource='w'))
                possible_moves.append(Move(Move.TRADE_BANK, num_trade=numTrade, give_resource='o', resource='l'))
                possible_moves.append(Move(Move.TRADE_BANK, num_trade=numTrade, give_resource='o', resource='g'))
                possible_moves.append(Move(Move.TRADE_BANK, num_trade=numTrade, give_resource='o', resource='b'))

            if (self.resources['l'] >= 2 and '2 l' in self.ports) or \
            (self.resources['l'] >= 3 and '3' in self.ports) or (self.resources['l'] >= 4):
                if (self.resources['l'] >= 2 and '2 l' in self.ports):
                    numTrade = '2'
                elif (self.resources['l'] >= 3 and '3' in self.ports):
                    numTrade = '3'
                else:
                    numTrade = '4'
                possible_moves.append(Move(Move.TRADE_BANK, num_trade=numTrade, give_resource='l', resource='w'))
                possible_moves.append(Move(Move.TRADE_BANK, num_trade=numTrade, give_resource='l', resource='o'))
                possible_moves.append(Move(Move.TRADE_BANK, num_trade=numTrade, give_resource='l', resource='g'))
                possible_moves.append(Move(Move.TRADE_BANK, num_trade=numTrade, give_resource='l', resource='b'))

            if (self.resources['b'] >= 2 and '2 b' in self.ports) or \
            (self.resources['b'] >= 3 and '3' in self.ports) or (self.resources['b'] >= 4):
                if (self.resources['b'] >= 2 and '2 b' in self.ports):
                    numTrade = '2'
                elif (self.resources['b'] >= 3 and '3' in self.ports):
                    numTrade = '3'
                else:
                    numTrade = '4'
                possible_moves.append(Move(Move.TRADE_BANK, num_trade=numTrade, give_resource='b', resource='w'))
                possible_moves.append(Move(Move.TRADE_BANK, num_trade=numTrade, give_resource='b', resource='o'))
                possible_moves.append(Move(Move.TRADE_BANK, num_trade=numTrade, give_resource='b', resource='g'))
                possible_moves.append(Move(Move.TRADE_BANK, num_trade=numTrade, give_resource='b', resource='l'))

            if (self.resources['g'] >= 2 and '2 g' in self.ports) or \
            (self.resources['g'] >= 3 and '3' in self.ports) or (self.resources['g'] >= 4):
                if (self.resources['g'] >= 2 and '2 g' in self.ports):
                    numTrade = '2'
                elif (self.resources['g'] >= 3 and '3' in self.ports):
                    numTrade = '3'
                else:
                    numTrade = '4'
                possible_moves.append(Move(Move.TRADE_BANK, num_trade=numTrade, give_resource='g', resource='w'))
                possible_moves.append(Move(Move.TRADE_BANK, num_trade=numTrade, give_resource='g', resource='o'))
                possible_moves.append(Move(Move.TRADE_BANK, num_trade=numTrade, give_resource='g', resource='b'))
                possible_moves.append(Move(Move.TRADE_BANK, num_trade=numTrade, give_resource='g', resource='l'))

            if robber:
                possible_moves = []
                spots = [(4, 1), (2, 1), (3, 3), (1, 0), (2, 3), (1, 2), (4, 0), \
                         (1, 1), (4, 2), (2, 4), (3, 0), (0, 2), (3, 2), (1, 3), \
                         (3, 1), (0, 0), (2, 2), (0, 1)]
                for spot in spots:
                    possible_players = [p for p in board.players_adjacent_to_hex(spot) if self is not p]

                    # Get a list of the player numbers
                    player_nums = [player.player_num for player in possible_players]

                    if len(player_nums) > 0:
                        for p in player_nums:
                            possible_moves.append(Move(Move.MOVE_ROBBER, coord=spot, player=p))
                    else:
                        possible_moves.append(Move(Move.MOVE_ROBBER, coord=spot))
            return possible_moves

    # A getter function to return the player's hand of dev cards
    def get_dev_cards(self):
        return self.dev_cards

    # Allows the game to access the number of victory points that a player has
    def calculate_vp(self):
        return self.dev_cards[Card.VICTORY_POINT] + 2 * len(self.cities) + \
        len(self.settlements) + self.longest_road + self.largest_army

    # A function that allows the players to choose their
    # settlement and road placement at the beginning of the game
    def choose_spot2(self, board, n_val):
        p_settlements = [((3,1),(8,3)), ((10,2), (8,1)), ((2,3),(5,4)), ((4,2), (6,3)),]
        p_roads = [([(3,1), (2,1)], [(8,3),(9,2)]),
                          ([(10,2),(11,1)], [(8,1),(7,1)]),
                          ([(5,4),(6,4)], [(2,3),(3,3)]),
                          ([(4,2),(3,2)], [(6,3),(5,3)])]
        self.settlements.append(p_settlements[n_val][0])
        self.settlements.append(p_settlements[n_val][1])
        for i, spot in enumerate(self.settlements):
            state= board.coords[spot]
            for p in state.ports:
                self.ports.append(p)
            if i == 1:
                board.add_settlement(self, spot, True)
            if i == 0:
                board.add_settlement(self, spot)
        road1 = p_roads[n_val][0]
        road2 = p_roads[n_val][1]
        self.roads[road1[0]] = [road1[1]]
        self.roads[road1[1]] = [road1[0]]
        self.roads[road2[0]] = [road2[1]]
        self.roads[road2[1]] = [road2[0]]
        board.build_road(road1[0], road1[1], self)
        board.build_road(road2[0], road2[1], self)

    def choose_spot(self, board, idx):
        legal_settlement = False
        legal_road = False

        while not legal_settlement:

            # Pick a legal spot
            if self.player_type == Player.HUMAN:
                loc = self.build_settlement(board)

            # This may yield coordinates that are not valid
            elif self.player_type == Player.RANDOM_AI or self.player_type == 2 or self.player_type == 3 or\
                 self.player_type == 4 or self.player_type == 5:
                loc = (random.randint(0, 11), random.randint(0, 5))

            legal_settlement = self.can_build_settlement(loc, board)

        # Add the settlement to the board and update player fields
        self.settlements.append(loc)
        state = board.coords[loc]
        for p in state.ports:
            self.ports.append(p)
        if idx == 2:
            board.add_settlement(self, loc, True)
        else:
            board.add_settlement(self, loc)

        # Choose where to play a road
        while not legal_road:

            if self.player_type == Player.HUMAN:
                move = self.build_road(board)
            # do it randomly for now for the MCTSAI
            elif self.player_type == Player.RANDOM_AI or self.player_type == 2 or self.player_type == 3 or\
                 self.player_type == 4 or self.player_type == 5:

                # Choose from set of roads coming from settlement; any should work
                possible_sinks = state.available_roads
                sink = possible_sinks[random.randint(0, len(possible_sinks) - 1)]
                move = (loc, sink)

            legal_road = self.can_build_road(move, board)

        # build the road
        self.roads[move[0]] = [move[1]]
        self.roads[move[1]] = [move[0]]
        print(self.roads)
        board.build_road(move[0], move[1], self)

    # TODO: this function should check that the move made is a legal move.
    # Consider making one of these for each move type.
    # If it is not, the board should not be updated and the player should
    # choose a different move. Return True if the move is legal and False
    # otherwise. A few things to check for:
    # Roads: built next to another road or settlement belonging to player,
    # does not overlap with already created road
    # Settlements: built next to road belonging to player, is at least
    # 2 spaces away from any other settlement
    # Cities: Placed over settlement belonging to player, not placed over
    # another city
    # Drawing dev card: there is at least one dev card in the deck
    # Moving robber: robber is moved to a valid space
    # Playing dev card: card is not a victory point or an already used knight,
    # a max of 1 dev card is used per turn, dev card is not used the turn its
    # drawn
    # Trading with bank: player has the required resources to make the trade
    # based on the ports that the player has
    # General: Make sure the player can only play the move if they have the
    # required resources
    def check_legal_move(self, move, board, deck):
        if move.move_type == Move.BUY_ROAD and move.coord in board.coords.keys() and self.total_roads < 15:
            # Resources available to make a road
            if self.resources['b'] >= 1 and self.resources['l'] >=1:
                state_o = board.coords[move[0]]
                # Does not overlap with already created road
                if move[1] in state_o.available_roads:
                    # Next to another road or settlement
                    if (move[0] in self.roads.keys()) or (move[1] in self.roads.keys()) or \
                    (move[0] in self.settlements) or (move[1] in self.settlements):
                            return True

        if move.move_type == Move.BUY_SETTLEMENT and move.coord in board.coords.keys() and len(self.settlements) < 5:
            # Resources available to make a settlement
            if self.resources['b'] >= 1 and self.resources['l'] >=1 and \
               self.resources['g'] >= 1 and self.resources['w'] >=1:
               state = board.coords[move]
               # Does not overlap with already created settlement
               if state.player == 0:
                    next_list = list(state.roads.keys()) + state.available_roads
                    # Next to another road
                    if (move in self.roads.keys()):
                        # Two spaces away from another settlement
                        for next in next_list:
                            next_state = board.coords[next]
                            if next_state['player'] != 0:
                                return False
                        return True

        # Have a settlement at that spot
        if move.move_type == Move.BUY_CITY and move.coord in self.settlements and len(self.cities) < 4:
            # Resources available to make a city
            if self.resources['o'] >= 3 and self.resources['g'] >=2:
                return True

        if move.move_type == Move.BUY_DEV:
            # Resources available to draw a dev card and enough dev cards in deck
            if self.resources['o'] >= 1 and self.resources['g'] >=1 \
                and self.resources['w'] >=1 and deck.cards_left > 0:
                return True

        if move.move_type == Move.PLAY_DEV:
            # Dev card available and not a victory point card

            if move.card_type in self.dev_cards.keys() and self.dev_cards[move.card_type] > 0:
                if move.card_type == Card.KNIGHT:
                    spots = {(4, 1), (2, 1), (3, 3), (1, 0), (2, 3), (1, 2), (4, 0), \
                             (1, 1), (4, 2), (2, 4), (3, 0), (0, 2), (3, 2), (1, 3), \
                             (3, 1), (0, 0), (2, 2), (0, 1)}
                    if move.coord in spots:
                        return True
                elif move.card_type == Card.VICTORY_POINT:
                    return False
                elif move.card_type == Card.ROAD_BUILDING:
                    state_o = board.coords[move.road[0]]
                    # Does not overlap with already created road
                    if move.road[1] in state_o.available_roads:
                        # Next to another road or settlement
                        if (move.road[0] in self.roads) \
                                or (move.road[1] in self.roads) \
                                or (move.road[0] in self.settlements) \
                                or (move.road[1] in self.settlements):
                            return True
                elif move.card_type == Card.MONOPOLY:
                    if move.resource in board.resource_list:
                        return True
                elif move.card_type == Card.YEAR_OF_PLENTY:
                    return True

        if move.move_type == Move.TRADE_BANK:
            old_res = move.give_resource
            if move.num_trade == 4 and self.resources[old_res] >= 4:
                return True
            elif move.num_trade == 3 and self.resources[old_res] >= 3 \
                    and ('3' in self.ports):
                return True
            elif move.num_trade == 2 and self.resources[old_res] >= 2 \
                    and ('2 {}'.format(old_res) in self.ports):
                return True

        if move.move_type == Move.MOVE_ROBBER:
            spots = {(4, 1), (2, 1), (3, 3), (1, 0), (2, 3), (1, 2), (4, 0), \
                     (1, 1), (4, 2), (2, 4), (3, 0), (0, 2), (3, 2), (1, 3), \
                     (3, 1), (0, 0), (2, 2), (0, 1)}
            if move.coord in spots:
                return True

        if move.move_type == Move.END_TURN:
            return True

        return False


    # TODO: this should represent a single move within a turn. Return
    # 0 if we are passing our turn, 1 if the move is a valid move,
    # -1 if the move is not legal
    def make_move(self, move, board, deck):

        # Play corresponds to the information that the board may
        # need when a dev card is played
        play = None
        if not self.check_legal_move(move, board, deck):
            if self.player_type == Player.HUMAN:
                print("Illegal move!")
            return -1

        # This is a legal move so if we're in debug mode, we should
        # print the move out!
        '''if settings.DEBUG:
            print("Printing the move:")
            print("Move type: " + str(move_type))
            print("Move: " + str(move))
        '''
        # End turn
        if move.move_type == Move.END_TURN:
            return 0

        # Build a road
        elif move.move_type == Move.BUY_ROAD:
            self.total_roads += 1
            self.resources['b'] -= 1
            self.resources['l'] -= 1
            if move.road[0] in list(self.roads.keys()):
                self.roads[move.road[0]].append(move.road[1])
            else:
                self.roads[move.road[0]] = [move.road[1]]
            if move.road[1] in list(self.roads.keys()):
                self.roads[move.road[1]].append(move.road[0])
            else:
                self.roads[move.road[1]] = [move.road[0]]

        # Build a settlement
        elif move.move_type == Move.BUY_SETTLEMENT:
            self.resources['b'] -= 1
            self.resources['l'] -= 1
            self.resources['g'] -= 1
            self.resources['w'] -= 1
            self.settlements.append(move.coord)
            state = board.coords[move.coord]
            for port in state.ports:
                self.ports.append(port)

        # Build a city
        elif move.move_type == Move.BUY_CITY:
            self.resources['o'] -= 3
            self.resources['g'] -= 2
            self.cities.append(move)
            self.settlements.remove(move)

        # Draw a dev card
        elif move.move_type == Move.BUY_DEV:
            self.drawDevCard(deck)
            self.resources['w'] -= 1
            self.resources['g'] -= 1
            self.resources['o'] -= 1

        # Play a dev card
        elif move.move_type == Move.PLAY_DEV:
            self.dev_cards[move.card_type] -= 1
            play = self.dev_card_handler(move.card_type, board)

            # If the dev card is road building, we've covered this in
            # the dev card handler, so we can just return
            if move.card_type == Move.ROAD_BUILDING:
                return 1

        # Trade with bank
        elif move.move_type == Move.TRADE:
            self.trade_resources(move.give_resource, move.resource)

        # Move robber.
        if move.move_type == Move.MOVE_ROBBER:
            board.update_board(self, move)
        else:
            # Apply the changes to the board
            board.update_board(self, move)
        return 1

    # A helper function for moving the robber in the case of rolling a 7
    def move_robber(self, board, spot, victim):
        while True:
            # TODO mctsai should not be picking random here
            if self.player_type == Player.RANDOM_AI \
                    or self.player_type == 2 \
                    or self.player_type == 3 \
                    or self.player_type == 4 \
                    or self.player_type == 5:
                if board.robber != (2,0):
                    spots.remove(board.robber)
                spot = spots[random.randint(0, len(spots) - 1)]
            invalid = self.make_move(7, board, None, (spot, victim))
            if invalid == 1:
                return


    # A helper function to move the robber and steal from
    # a player
    # TODO mctsai should not be picking random here
    def choose_victim(self, board, move):

        victim = None

        # Determine the players adjacent to the robber
        possible_players = [p for p in board.players_adjacent_to_hex(move.coord) if p is not self]

        # Get a list of the player numbers
        player_nums = [p.player_num for p in possible_players]

        if len(possible_players) > 0:

            # Keep prompting the person until they enter a valid victim
            while True:

                if self.player_type == Player.HUMAN:
                    num = int(input("Who do you want to steal from? (give player number)"))

                    if num in player_nums:
                        victim = possible_players[player_nums.index(num)]
                        break
                    else:
                        print("Invalid victim. Please enter a valid player to steal from.")
                else:
                    victim = possible_players[random.randint(0, len(possible_players) - 1)]
                    break
        return victim

    # A helper function to make sure that possible roads exist for the player. If
    # they don't, we have to pass from road building
    def possible_roads_build(self, board):
        # Get the set of possible places we can build a road
        possible_roads = {}

        for road_source in list(self.roads.keys()):
            possible_sinks = board.coords[road_source]['available roads']

            for sink in possible_sinks:
                if (road_source, sink) not in possible_roads and \
                (sink, road_source) not in possible_roads:
                    possible_roads[(sink, road_source)] = True

        if len(possible_roads.keys()) > 0:
            return True
        else:
            return False



    # A helper function to handle playing dev cards
    def dev_card_handler(self, card_type, board):

        # Handle the knight
        if card_type == 'Knight':
            self.num_knights_played += 1
            if self.player_type == Player.HUMAN:
                r,c = map(int, input("Where are you moving the robber? (Input form: row# col#): ").split())
                spot = (r, c)
            elif self.player_type == Player.RANDOM_AI or self.player_type == 2 or self.player_type == 3 or\
                 self.player_type == 4 or self.player_type == 5:
                spots = [(4, 1), (2, 1), (3, 3), (1, 0), (2, 3), (1, 2), (4, 0), \
                (1, 1), (4, 2), (2, 4), (3, 0), (0, 2), (3, 2), (1, 3), (3, 1), \
                (0, 0), (2, 2), (0, 1)]
                if board.robber != (2,0):
                    spots.remove(board.robber)
                spot = spots[random.randint(0, len(spots) - 1)]
            victim = self.choose_victim(board, spot)
            return (spot, victim)

        # Handle road builder; give the player resources for 2 roads then call
        # make_move for building roads until they place 2 valid roads
        if card_type == "Road Building":

            # Take care of cases where too many roads are already built
            if self.total_roads == 15:
                return None
            elif self.total_roads == 14:
                if not self.possible_roads_build(board):
                    return None
                self.resources['l'] += 1
                self.resources['b'] += 1
                roads_played = 0
                while roads_played < 1:
                    if self.player_type == Player.HUMAN:
                        move = self.build_road(board)
                    else:
                        move = self.choose_road(board)
                    if self.make_move(1, board, None, move) == 1:
                        roads_played += 1
                return None
            else:
                roads_played = 0
                while roads_played < 2:
                    if not self.possible_roads_build(board):
                        return None
                    self.resources['l'] += 1
                    self.resources['b'] += 1
                    if self.player_type == Player.HUMAN:
                        move = self.build_road(board)
                    elif self.player_type == Player.RANDOM_AI or self.player_type == 2 or self.player_type == 3 or\
                         self.player_type == 4 or self.player_type == 5:
                        move = self.choose_road(board)
                    if self.make_move(1, board, None, move) == 1:
                        roads_played += 1
                return None

        # year of plenty; choose 2 cards to receive
        possible_cards = ['w', 'l', 'g', 'b', 'o']
        if card_type == "Year of Plenty":
            if self.player_type == Player.HUMAN:
                card1 = input("Choose first card")
                card2 = input("Choose second card")
            else:
                card1 = possible_cards[random.randint(0, len(possible_cards)-1)]
                card2 = possible_cards[random.randint(0, len(possible_cards)-1)]
            self.resources[card1] += 1
            self.resources[card2] += 1
            return None

        # monopoly: choose a card and steal it from all other players
        if card_type == "Monopoly":
            if self.player_type == Player.HUMAN:
                card_choice = input("Choose card to monopoly!")
            else:
                card_choice = possible_cards[random.randint(0, len(possible_cards)-1)]
            return card_choice




    # A helper function for the random AI to randomly decide on an available
    # road to play.
    def choose_road(self, board):
        possible_roads = {}

        for road_source in list(self.roads.keys()):
            possible_sinks = \
            board.coords[road_source]['available roads']

            for sink in possible_sinks:
                if (road_source, sink) not in possible_roads and \
                (sink, road_source) not in possible_roads:
                    possible_roads[(sink, road_source)] = True

        options = list(possible_roads.keys())
        return options[random.randint(0, len(options) - 1)]


    # A helper function to decrement the resources correctly if the trade
    # with bank option is chosen.
    def trade_resources(self, old_res, new_res):
        if '2 ' + old_res[1] in self.ports:
            self.resources[old_res[1]] -= 2
        elif '3' in self.ports:
            self.resources[old_res[1]] -= 3
        else:
            self.resources[old_res[1]] -= 4
        self.resources[new_res] += 1
        return


    # TODO: this function will be used to choose the move. it should
    # be different depending on whether the player is a random AI,
    # human, or MCTS AI
    def decide_move(self, dev_played, board, deck, players, robber):

        if self.player_type == Player.HUMAN:
            self.printResources()
            print('Moves available:')
            print('Enter 0 for ending/passing your turn')
            print('Enter 1 to build a road ')
            print('Enter 2 to build a settlement ')
            print('Enter 3 to build a city ')
            print('Enter 4 to draw a dev card ')
            print('Enter 5 to play a dev card ')
            print('Enter 6 to make a trade ')
            if robber:
                r,c = map(int, input("Where are you moving the robber? (Input form: row# col#): ").split())
                spot = (r, c)
                victim = self.choose_victim(board, spot)
                self.move_robber(board, spot, victim)
            move_type = int(input('Select move: '))
            if not (move_type == 5 and dev_played > 0):

                # Let's decide on the specific places to move in this
                # function so that we can abstract make_move to work for
                # both AI and human players
                if move_type == 0:
                    return [0]

                elif move_type == 1:
                    move = self.build_road(board)
                    return [1, move]

                elif move_type == 2:
                    move = self.build_settlement(board)
                    return [2, move]

                elif move_type == 3:
                    move = self.build_city(board)
                    return [3, move]

                elif move_type == 4:
                    return [4]

                elif move_type == 5:
                    move = self.playDevCard(board)
                    return [5, move]

                elif move_type == 6:
                    move = self.trade(board)
                    return [6, move]


                return move_type
            else:
                print("You have already played a dev card in this round")

        # Case of random AI player. Here, we should create a list of
        # possible moves and choose a move from the list with a
        # uniform distribution. We will need to handle separately
        # moving the robber to a specific spot

        elif self.player_type == Player.RANDOM_AI:
            possible_moves = self.get_legal_moves(board, deck, dev_played, robber, 0)
            # Choose a move randomly from the set of possible moves!
            return list(possible_moves[random.randint(0, len(possible_moves) - 1)])

        elif self.player_type == 2:
            AI = MCTSAI(board, 5, 20, players, deck, dev_played, self.player_num, robber, 0, False)
            board1 = copy.deepcopy(board)
            move = AI.get_play()
            return move

        elif self.player_type == 3:
            AI = MCTSAI(board, 5, 20, players, deck, dev_played, self.player_num, robber, 1, False)
            board1= copy.deepcopy(board)
            move = AI.get_play()
            return move

        elif self.player_type == 4:
            AI = MCTSAI(board, 5, 20, players, deck, dev_played, self.player_num, robber, 0, True)
            board1= copy.deepcopy(board)
            move = AI.get_play()
            return move

        elif self.player_type == 5:
            AI = MCTSAI(board, 5, 20, players, deck, dev_played, self.player_num, robber, 1, True)
            board1= copy.deepcopy(board)
            move = AI.get_play()
            return move


    # A helper function to check if we can build a settlement at a specific
    # location
    def can_build_settlement(self, coords, board):

        # Check that the coordinates are valid
        if coords not in board.coords:
            return False

        state = board.coords[coords]

        # Does not overlap with already created settlement
        if state['player'] == 0:
            next_list = list(state['roads'].keys()) + state['available roads']

            # Two spaces away from another settlement
            for next in next_list:
                next_state = board.coords[next]
                if next_state['player'] != 0:
                    return False
            return True
        if self.player_type == Player.HUMAN:
            print('Cannot build settlement here...')
        return False


    # A helper function to check if we can build a road at a specific
    # location
    def can_build_road(self, move, board):
        if move[0] in board.coords.keys():
            state_o = board.coords[move[0]]

            # Does not overlap with already created road
            if move[1] in state_o['available roads']:

                # Next to another road or settlement
                if (move[0] in self.roads.keys()) or (move[1] in self.roads.keys()) or \
                (move[0] in self.settlements) or (move[1] in self.settlements):
                    return True
        if self.player_type == Player.HUMAN:
            print('Cannot build road here...')
        return False


    # TODO:
    # function in which the player can have a turn. This should be handled
    # differently depending on whether the player is real or is an AI.
    # If the player is real, the make_move function should prompt the player
    # to enter moves from the command line, check if they are legal, and update
    # the board state if they are legal. The function returns when the player
    # has entered a command to end their turn. For an AI, we should first code
    # a basis random AI. This AI will consider the set of legal moves that they
    # can make and choose one at random. This will occur until they randomly
    # choose to end their turn. If a player makes a move that causes their
    # victory points to be greater than or equal to 10, the function should
    # immediately return 1. Otherwise, return 0 when the turn is over.
    # Don't update dev cards till end of turn
    # note i added players here because the MCTSAI needs info to make decisions
    # for what the other players might have.
    def make_turn(self, board, deck, players, robber):

        # This should indicate whether a dev card has already been
        # played during this turn. If so, we can't play another one.
        dev_played = 0

        while True:

            move = self.decide_move(dev_played, board, deck, players, robber)
            # move is list
            move_type = move[0]
            #robber should only be the first move
            robber = 0
            move_instructs = None
            if move_type == 7:
                move_instructs = (move[1], move[2])
            elif len(move) > 1:
                move_instructs = move[1]

            move_made = self.make_move(move_type, board, deck, move_instructs)
            if move_made == 1:
                if move == 5:
                    dev_played += 1

                # Did the move cause us to win?
                if self.calculate_vp() >= settings.POINTS_TO_WIN:
                    return 1

            if move_made == 0:
                break


    ######################### HELPER FUNCTIONS FOR HUMAN PLAYERS #############################

    def build_road(self, board):
        r0,c0 = map(int, input("Coordinate for road beginning/origin (Input form: row# col#): ").split())
        r1,c1 = map(int, input("Coordinate for road end (Input form: row# col#): ").split())
        print('Building road from (', r0, ', ', c0, ') to (', r1, ', ', c1, ') ...')
        move = ((r0, c0), (r1, c1))
        return move     # List of tuples: two coordinates


    def build_settlement(self, board):
        r,c = map(int, input("Coordinate for settlement (Input form: row# col#): ").split())
        print('Building settlement at (', r, ', ', c, ') ...')

        move = (r, c)
        return move     # Tuple: one coordinate


    def build_city(self, board):
        r,c = map(int, input("Coordinate for city (Input form: row# col#): ").split())
        print('Building city at (', r, ', ', c, ') ...')

        move = (r, c)
        return move     # Tuple: one coordinate

    # Returns 1 if the move is valid, -1 if the dev card stack is empty
    def drawDevCard(self, deck):
        move = deck.take_card(self)
        return move

    ##################################### WRITE DEV CARD CODE #####################################
    def playDevCard(self, board):
        move = input("Which dev card do you want to play (Choose from form: Knight, Road Building, Monopoly, Year of Plenty): ")
        print('Playing dev card ...')
        return move
    ##################################### WRITE DEV CARD CODE #####################################


    def trade(self, board):
        numCards = input("How many cards do you want to trade?")
        card = input("Lumber, Ore, Wool, Brick, or Grain? (Input form: l, o, w, b, g)")
        oldRes = (numCards, card)
        newRes = input("Which resource would you like in exchange? (Input form: l, o, w, b, g)")
        move = (oldRes, newRes)
        return move     # Tuple of tuple: Trade of multiple cards for one card

    def hashable_player(self):


        res = sorted(self.resources.items())
        dev = sorted(self.dev_cards.items())
        hash_res = tuple([(k, v) for k, v in res])
        hash_dev_cards = tuple([(k, v) for k, v in dev])
        hash_cities = tuple([(k, v) for k, v in sorted(self.cities)])
        player_tuple = (self.player_num, hash_res, hash_dev_cards, tuple(sorted(self.ports)), \
            self.num_knights_played, self.longest_road, self.largest_army, \
            self.player_type, tuple(sorted(self.ports)), tuple(sorted(self.cities)), tuple(sorted(self.settlements)), \
            hash_cities, self.total_roads)
        return player_tuple




