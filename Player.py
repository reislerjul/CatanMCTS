import copy
import random
import settings
from utils import Card, Move

# The player class. Each player should keep track of their roads, cities,
# settlements, dev cards, whether they're on a port, number of victory
# points, and resource cards.
class Player(object):
    HUMAN = 0
    RANDOM_AI = 1
    MCTS_AI = 2
    MCTSNN_AI = 3
    NNET = 4

    # TODO: Complete this constructor. player_type should be 0 if the player is
    # human, 1 if the player is the random AI, and 2 if the player is the
    # MCTS AI with random choice of moves and 3 is MCTS AI with weighted choice
    def __init__(self, player_type, player_num):
        self.player_num = player_num

        # Have the players start with the resources to build the first two roads/
        # settlements
        self.resources = {'w':2, 'b':4, 'l':4, 'g':2, 'o':0}
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
        self.roads = {}         # {(0,0):[(1,1)],(1,1):[(0,0)], ...}
        self.total_roads = 0
        self.has_rolled = False
        self.move_robber = False
        self.dev_played = 0
        self.trades_tried = 0
        self.dev_drawn = -1
        self.random = False

        # This stuff on bottom is used for bookkeeping
        self.num_yop_played = 0
        self.num_monopoly_played = 0
        self.num_road_builder_played = 0
        self.devs_bought = 0
        self.trades_proposed = 0
        self.trades_proposed_successfully = 0
        self.trades_accepted = 0 
        self.bank_trades = 0
        self.num_dots_initial_spots = 0

        # Keep track of the total rounds the player has had and the total number of moves. 
        # This doesn't include invalid moves 
        self.avg_moves_round = [0, 0]


    ############################## FUNCTIONS OVERRIDEN BY CHILD CLASSES ##############################

    # Should we write whether a move is invalid to the terminal?
    # Note: this is overriden for human players
    def print_invalid_move(self):
        return False

    def decide_move(self, board, deck, players, nn):
        return

    def trade_other_players(self):
        return

    def to_string(self):
        return "Player"

    ############################ FUNCTIONS NOT OVERRIDEN BY CHILD CLASSES ############################

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

        total_resources = sum(self.resources.values())
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

    # We use this when the game starts to make sure that the first road attaches to the first
    # settlement and the second road attaches to the second settlement
    def find_possible_road_spots(self, board):
        possible_roads = []

        # Find the settlement with no roads coming from it
        correct_source = None
        for element in self.settlements:
            if element not in self.roads:
                correct_source = element
        assert(correct_source != None)

        possible_sinks = board.coords[correct_source].available_roads
        for sink in possible_sinks:
            possible_roads.append(Move(Move.BUY_ROAD, road=frozenset([correct_source, sink])))
        return possible_roads

    # A helper function used to get a list of all the legal moves. If weighted, we
    # weight better moves so we have a higher chance of choosing them.
    # give_resource and get_resource should be None or maps of resources to their quanities
    def get_legal_moves(self, board, deck):

            # Determine moves we can play and add them to the list.
            if board.round_num in [0, 1]:
                if len(self.settlements) == board.round_num:
                    legal_settlements = []
                    for loc in board.coords:
                        if self.can_build_settlement(loc, board):
                            legal_settlements.append(Move(Move.BUY_SETTLEMENT, coord=loc))
                    return legal_settlements
                elif board.round_num == self.total_roads:
                    return self.find_possible_road_spots(board)
                else:
                    return [Move(Move.END_TURN)]

            # We are trying to decide whether to accept a trade. The two options are
            # aceept a trade or don't accept a trade
            if board.pending_trade:
                #print("trading active player: " + str(board.active_player.player_num) + 
                #    ", turn player: " + str(self.player_num))
                if board.pending_trade.player == self.player_num:
                    moves = [Move(Move.CHOOSE_TRADER, player=p.player_num) for p in board.traders]
                    if len(moves) < len(board.players):
                        moves.append(Move(Move.CHOOSE_TRADER, player=None))
                    return moves
                if self.can_accept_trade(board.pending_trade.resource):
                    return [Move(Move.DECLINE_TRADE), Move(Move.ACCEPT_TRADE)]
                return [Move(Move.DECLINE_TRADE)]

            if board.seven_roller:
                possible_moves = []
                resource_list = self.resources['w'] * ['w'] + self.resources['o'] * ['o'] + \
                self.resources['l'] * ['l'] + self.resources['b'] * ['b'] + \
                self.resources['g'] * ['g']
                total_resources = len(resource_list)
                discard = total_resources // 2
                combo = ()
                for i in range(discard):
                    res = resource_list.pop(random.randint(0, len(resource_list) - 1))
                    combo = combo + tuple(res)
                return [Move(Move.DISCARD_HALF, resource=combo)]

            # Can we play a dev card?
            possible_moves = []
            if self.dev_played == 0:
                for card in self.dev_cards.keys():
                    if self.dev_cards[card] - (1 if self.dev_drawn == card else 0) > 0:
                        if card == Card.KNIGHT:
                            possible_moves = []
                            spots = [(4, 1), (2, 1), (3, 3), (1, 0), (2, 3), (1, 2), (4, 0), \
                                     (1, 1), (4, 2), (2, 4), (3, 0), (0, 2), (3, 2), (1, 3), \
                                     (3, 1), (0, 0), (2, 2), (0, 1), (2, 0)]
                            spots.remove(board.robber)
                            for spot in spots:
                                possible_players = [p for p in board.players_adjacent_to_hex(spot) if self.player_num != p.player_num]

                                if possible_players != []:
                                    for p in possible_players:
                                        possible_moves.append(Move(Move.PLAY_DEV, card_type=card, coord=spot, player=p.player_num))
                                else:
                                    possible_moves.append(Move(Move.PLAY_DEV, card_type=card, coord=spot))
                        elif card == Card.ROAD_BUILDING:
                            if self.total_roads < 15:
                                # Get the set of possible places we can build a road
                                possible_roads = set()
                                for road_source in self.roads:
                                    possible_sinks = board.coords[road_source].available_roads
                                    for sink in possible_sinks:
                                        if frozenset([road_source, sink]) not in possible_roads:
                                            possible_roads.add(frozenset([road_source, sink]))
                                if self.total_roads == 14:
                                    # We now have the possible single roads, so lets add those moves!
                                    for road in possible_roads:
                                        possible_moves.append(Move(Move.PLAY_DEV,
                                                                   card_type=card,
                                                                   road=road))
                                else:
                                    # check for additional possible roads
                                    possible_road_pairs = set()
                                    for road in possible_roads:
                                        for road_source in set(self.roads.keys()) | road:
                                            possible_sinks = board.coords[road_source].available_roads
                                            for sink in possible_sinks:
                                                if road == frozenset([road_source, sink]):
                                                    continue
                                                roads = frozenset([road, frozenset([road_source, sink])])
                                                if roads not in possible_road_pairs:
                                                    possible_road_pairs.add(roads)
                                                    possible_moves.append(Move(Move.PLAY_DEV,
                                                                       card_type=card,
                                                                       road=road,
                                                                       road2=frozenset([road_source, sink])))
                        elif card == Card.MONOPOLY:
                            for r in board.resource_list:
                                possible_moves.append(Move(Move.PLAY_DEV, card_type=card, resource=r))
                        elif card == Card.YEAR_OF_PLENTY:
                            for i in range(len(board.resource_list)):
                                for j in range(i, len(board.resource_list)):
                                    possible_moves.append(Move(Move.PLAY_DEV, card_type=card, \
                                        resource=board.resource_list[i], resource2=board.resource_list[j]))

            # We need to roll at the beginning of the turn
            if not self.has_rolled:
                roll = random.randint(1, 6) + random.randint(1, 6)
                return possible_moves + [Move(Move.ROLL_DICE, roll=roll, player=self.player_num)]

            if self.move_robber:
                possible_moves = []
                spots = [(4, 1), (2, 1), (3, 3), (1, 0), (2, 3), (1, 2), (4, 0), \
                         (1, 1), (4, 2), (2, 4), (3, 0), (0, 2), (3, 2), (1, 3), \
                         (3, 1), (0, 0), (2, 2), (0, 1)]
                for spot in spots:
                    possible_players = [p for p in board.players_adjacent_to_hex(spot) if self.player_num != p.player_num]

                    if possible_players != []:
                        for p in possible_players:
                            possible_moves.append(Move(Move.MOVE_ROBBER, coord=spot, player=p.player_num))
                    else:
                        possible_moves.append(Move(Move.MOVE_ROBBER, coord=spot))
                return possible_moves

            # We can always end our turn
            possible_moves.append(Move(Move.END_TURN))
            
            # Can we buy dev card?
            card = deck.peek()
            if (self.resources['g'] > 0
                and self.resources['w'] > 0
                and self.resources['o'] > 0
                and card != -1):
                possible_moves.append(Move(Move.BUY_DEV, card_type=card, player=self.player_num))
            

            # Can we ask for a trade?
            if self.trades_tried < 2:
                # For MCTSPlayer and RandomPlayer, this should be a bit different than the real game.
                # we will assume that the trades they want to try are in the form of 1 type of resource
                # for another type of resource instead of trading multiple types for 1
                # Also, it is reasonable for players to know which cards are out in the game, so only ask 
                # for cards that other players have
                resources_out = {'w': 0, 'g': 0, 'b': 0, 'l': 0, 'o': 0}
                for player in board.players:
                    if player.player_num != self.player_num:
                        for element in resources_out.keys():
                            resources_out[element] = max(player.resources[element], resources_out[element])
                resource_list = self.resources.items()
                for resource in resource_list:
                    trade_for = ['g', 'w', 'o', 'b', 'l']
                    trade_for.remove(resource[0])
                    for i in range(1, min(resource[1] + 1, 4)):
                        loss = (resource[0], i)
                        for element in trade_for:
                            for j in range(1, min(resources_out[element] + 1, 4)):
                                gain = (element, j)
                                possible_moves.append(Move(Move.PROPOSE_TRADE, give_resource=loss, resource=gain, player=self.player_num))

            # Can we build a city?
            if self.resources['g'] >= 2 and self.resources['o'] >= 3 and \
            len(self.cities) < 4:
                for settlement in self.settlements:
                    possible_moves.append(Move(Move.BUY_CITY, coord=settlement))

            # Can we build a road?
            if self.resources['b'] > 0 and self.resources['l'] > 0 and self.total_roads < 15:
                # Get the set of possible places we can build a road
                possible_roads = set()

                for road_source in self.roads:
                    possible_sinks = board.coords[road_source].available_roads

                    for sink in possible_sinks:
                        if frozenset([road_source, sink]) not in possible_roads:
                            possible_roads.add(frozenset([road_source, sink]))

                # We now have the possible roads, so lets add those moves!
                for road in possible_roads:
                    possible_moves.append(Move(Move.BUY_ROAD, road=road))

            # Can we build a settlement?
            if self.resources['w'] > 0 and self.resources['l'] > 0 and \
            self.resources['b'] > 0 and self.resources['g'] > 0 and \
            len(self.settlements) < 5:
                # Check the possible places for us to build a settlement
                for source in self.roads:
                    if self.can_build_settlement(source, board):
                        possible_moves.append(Move(Move.BUY_SETTLEMENT, coord=source))

            # Should we trade in resources? Try cases for the 5 different resources
            for give in board.resource_list:
                if (self.resources[give] >= 4) or \
                (self.resources[give] >= 3 and '3' in self.ports) or \
                (self.resources[give] >= 2 and '2 ' + give in self.ports):
                    for receive in board.resource_list:
                        if give != receive:
                            possible_moves.append(Move(Move.TRADE_BANK, give_resource=give, resource=receive))
            if len(possible_moves) == 0:
                print("no possible moves")
            return possible_moves

    # Allows the game to access the number of victory points that a player has
    def calculate_vp(self):
        return (self.dev_cards[Card.VICTORY_POINT]
              + 2 * len(self.cities)
              + len(self.settlements)
              + self.longest_road
              + self.largest_army)

    def add_road(self, board, road):
        coords = list(road)
        if coords[0] in self.roads:
            self.roads[coords[0]].append(coords[1])
        else:
            self.roads[coords[0]] = [coords[1]]
        if coords[1] in self.roads:
            self.roads[coords[1]].append(coords[0])
        else:
            self.roads[coords[1]] = [coords[0]]
        self.total_roads += 1

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
        if board.pending_trade:
            if move.move_type == Move.CHOOSE_TRADER and board.pending_trade.player == self.player_num:
                return True
            if board.pending_trade.player == self.player_num:
                return False
            if move.move_type == Move.ACCEPT_TRADE:
                return self.can_accept_trade(board.pending_trade.resource)
            return (move.move_type == Move.DECLINE_TRADE)

        if board.seven_roller:
            if move.move_type == Move.DISCARD_HALF:
                total_resources = sum(self.resources[r] for r in self.resources.keys())
                if total_resources > 7:
                    combo_dict = {}
                    for resource in move.resource:
                        if resource not in combo_dict:
                            combo_dict[resource] = 1
                        else:
                            combo_dict[resource] += 1
                    for resource in combo_dict.keys():
                        if combo_dict[resource] > self.resources[resource]:
                            return False
                    return True
            return False

        if (not self.has_rolled and (move.move_type != move.ROLL_DICE and 
            move.move_type != move.PLAY_DEV)) and board.round_num > 1:
            #print('shouldnt be here')
            return False

        if move.move_type == Move.ROLL_DICE:
            return not self.has_rolled
        if move.move_type == Move.BUY_ROAD:
            road_coords = list(move.road)
            if (road_coords[0] in board.coords
                and road_coords[1] in board.coords
                and self.total_roads < 15):
                # Resources available to make a road
                if self.resources['b'] >= 1 and self.resources['l'] >= 1:
                    state_o = board.coords[road_coords[0]]
                    # Does not overlap with already created road
                    if road_coords[1] in state_o.available_roads:
                        # Next to another road or settlement
                        if move.road & (set(self.roads.keys()) | set(self.settlements)):
                            return True
            return False

        if move.move_type == Move.BUY_SETTLEMENT and len(self.settlements) < 5:
            # Resources available to make a settlement
            #print('in check legal move for settlements')
            #print('round number: ' + str(board.round_num))
            #print(self.resources)
            if (self.resources['b'] >= 1
                and self.resources['l'] >=1
                and self.resources['g'] >= 1
                and self.resources['w'] >=1):
                #print('have resources')
                if move.coord not in board.coords:
                    return False
                state = board.coords[move.coord]

               # Does not overlap with already created settlement
                if state.player == None:
                    #print('doesnt overlap with already created')
                    next_list = list(state.roads.keys()) + state.available_roads
                    # Two spaces away from another settlement
                    for n in next_list:
                        next_state = board.coords[n]
                        if next_state.player != None:
                            #print('not two away')
                            return False

                    # Next to another road. only needed when its not round 0 or 1
                    if (move.coord in self.roads
                        or board.round_num == 0
                        or board.round_num == 1):
                        return True
            return False

        # Have a settlement at that spot
        if move.move_type == Move.BUY_CITY \
                and move.coord in self.settlements \
                and len(self.cities) < 4:
            # Resources available to make a city
            return (self.resources['o'] >= 3 and self.resources['g'] >= 2)

        if move.move_type == Move.BUY_DEV:
            # Resources available to draw a dev card and enough dev cards in deck
            return (self.resources['o'] >= 1 \
                    and self.resources['g'] >= 1 \
                    and self.resources['w'] >= 1 \
                    and move.card_type != -1)

        if move.move_type == Move.PLAY_DEV:
            # Dev card available and not a victory point card
            if move.card_type in self.dev_cards.keys() \
                    and self.dev_cards[move.card_type] - \
                    (1 if move.card_type == self.dev_drawn else 0) > 0 \
                    and self.dev_played == 0:
                if move.card_type == Card.KNIGHT:
                    spots = {(4, 1), (2, 1), (3, 3), (1, 0), (2, 3), (1, 2), (4, 0),
                             (1, 1), (4, 2), (2, 4), (3, 0), (0, 2), (3, 2), (1, 3),
                             (3, 1), (0, 0), (2, 2), (0, 1), (2, 0)}
                    spots.remove(board.robber)
                    return move.coord in spots
                elif move.card_type == Card.VICTORY_POINT:
                    return False
                elif move.card_type == Card.ROAD_BUILDING:
                    road_coords = list(move.road)
                    if (road_coords[0] in board.coords
                        and road_coords[1] in board.coords
                        and self.total_roads < 15):

                        state_o = board.coords[road_coords[0]]
                        # check overlap with already created road
                        if road_coords[1] not in state_o.available_roads:
                            return False
                        if move.road2:
                            # build 2 roads
                            road2_coords = list(move.road2)
                            if (road2_coords[0] not in board.coords
                                or road2_coords[1] not in board.coords
                                or self.total_roads > 13):
                                return False
                                
                            state_o = board.coords[road2_coords[0]]
                            # check overlap with already created road
                            if road2_coords[1] not in state_o.available_roads:
                                return False

                            if move.road & move.road2:
                                # roads are connected
                                coord_set = move.road | move.road2
                                # check if next to another road or settlement
                                return coord_set & (set(self.roads.keys()) | set(self.settlements))
                            else:
                                # both roads must be next to another road or settlement
                                return (move.road & (set(self.roads.keys()) | set(self.settlements))
                                        and  move.road2 & (set(self.roads.keys()) | set(self.settlements)))
                        else:
                            # only build 1 road
                            state_o = board.coords[road_coords[0]]
                            # Does not overlap with already created road
                            if road_coords[1] in state_o.available_roads:
                                # Next to another road or settlement
                                if move.road & (set(self.roads.keys()) | set(self.settlements)):
                                    return True
                    return False
                elif move.card_type == Card.MONOPOLY:
                    return move.resource in board.resource_list
                elif move.card_type == Card.YEAR_OF_PLENTY:
                    if move.resource not in board.resource_list:
                        return False
                    if move.resource2 and move.resource2 not in board.resource_list:
                        return False
                    return True

        if move.move_type == Move.TRADE_BANK:
            old_res = move.give_resource
            num_trade = 4
            if '2 ' + old_res in self.ports:
                num_trade = 2
            elif '3' in self.ports:
                num_trade = 3            
            if self.resources[old_res] >= num_trade:
                return True
            return False
        if move.move_type == Move.MOVE_ROBBER:
            spots = {(4, 1), (2, 1), (3, 3), (1, 0), (2, 3), (1, 2), (4, 0), \
                     (1, 1), (4, 2), (2, 4), (3, 0), (0, 2), (3, 2), (1, 3), \
                     (3, 1), (0, 0), (2, 2), (0, 1)}
            if move.coord in spots:
                return True
            return False

        # For propose trade, we check elsewhere that these are legal moves
        return (move.move_type == Move.END_TURN or move.move_type == Move.PROPOSE_TRADE)

    # This represents a single move within a turn. Return
    # 1 if the move is a valid move, -1 if the move is not legal
    def make_move(self, move, board, deck, players):
        #print("move type: " + str(move.move_type))
        # Play corresponds to the information that the board may
        # need when a dev card is played
        #print("trying to make move: " + str(move.move_type))

        #print('move: ' + str(move.move_type) + ', round: ' + str(board.round_num) + 
        #    ', player: ' + str(self.player_num) + ', has rolled: ' + str(self.has_rolled) + 
        #    ', active player: ' + str(board.active_player.player_num))
        # Only check for legal move if a human is playing
        if self.player_type == Player.HUMAN and not self.random and not self.check_legal_move(move, board, deck):
            #print(move.move_type)
            #print("card: " + str(move.card_type))
            #print("round: " + str(board.round_num))
            #print(self.resources)
            #print(len(self.settlements))
            print("illegal move. move type: " + str(move.move_type) + ". active player: " + str(self.player_num))
            if self.player_type == Player.HUMAN:
                print("Illegal move!")
            return -1

        #print("Move. move type: " + str(move.move_type) + ". active player: " + str(self.player_num))
        # This is a legal move so if we're in debug mode, we should
        # print the move out!
        '''if settings.DEBUG:
            print("Printing the move:")
            print("Move type: " + str(move_type))
            print("Move: " + str(move))
        '''
        #print("active player: " + str(self.player_num) + ", move type: " + str(move.move_type))
        if settings.DEBUG:
            print("")
            print("printing move:")
            print(str(move))

        self.avg_moves_round[1] += 1
        if move.move_type == Move.ROLL_DICE:
            self.has_rolled = True
            if move.roll == 7:
                self.move_robber = True

        elif move.move_type == Move.ACCEPT_TRADE:
            self.trades_accepted += 1

        elif move.move_type == Move.CHOOSE_TRADER:
            #print("choosing traders")
            chosen = players[move.player - 1] if move.player != None else None

            if chosen != None:
                self.trades_proposed_successfully += 1
                loss = board.pending_trade.give_resource
                chosen.resources[loss[0]] += int(loss[1])
                self.resources[loss[0]] -= int(loss[1])

                gain = board.pending_trade.resource
                chosen.resources[gain[0]] -= int(gain[1])
                self.resources[gain[0]] += int(gain[1])

        elif move.move_type == Move.DISCARD_HALF:
            for resource in move.resource:
                self.resources[resource] -= 1

        # For now, all players should randomly choose the
        # player to trade with from the list of players
        # that'll accept the trade
        elif move.move_type == Move.PROPOSE_TRADE:
            self.trades_tried += 1
            self.trades_proposed += 1

        # Build a road
        elif move.move_type == Move.BUY_ROAD:
            self.resources['b'] -= 1
            self.resources['l'] -= 1
            self.add_road(board, move.road)

        # Build a settlement
        elif move.move_type == Move.BUY_SETTLEMENT:
            #print('printing surrounding resources: ')
            #print(board.resources[move.coord])
            #print('done printing surrounding resources')

            # after playing a second settlement, players
            # get the resources surrounding that settlement
            if board.round_num == 0:
                hexes = board.coords[move.coord].resource_locs
                for loc in hexes:
                    self.num_dots_initial_spots += board.resources[loc][2]
            if board.round_num == 1:
                resources = board.coords[move.coord].resource_locs
                for hex_loc in resources:
                    self.num_dots_initial_spots += board.resources[hex_loc][2]
                    vals = board.resources[hex_loc]
                    if vals[0] in self.resources:
                        self.resources[vals[0]] += 1
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
            self.cities.append(move.coord)
            self.settlements.remove(move.coord)

        # Draw a dev card
        elif move.move_type == Move.BUY_DEV:
            card = deck.take_card(move.card_type)
            self.dev_drawn = card
            if card != -1:
                self.devs_bought += 1
                self.resources['w'] -= 1
                self.resources['g'] -= 1
                self.resources['o'] -= 1
                self.dev_cards[card] += 1

        # Play a dev card
        elif move.move_type == Move.PLAY_DEV:
            self.dev_played += 1
            self.dev_cards[move.card_type] -= 1
            self.dev_card_handler(board, deck, players, move)

        # Trade with bank
        elif move.move_type == Move.TRADE_BANK:
            self.bank_trades += 1
            self.trade_resources(move.give_resource, move.resource)

        # Move robber.
        elif move.move_type == Move.MOVE_ROBBER:
            self.move_robber = False

        elif move.move_type == Move.END_TURN:
            self.dev_played = 0
            self.trades_tried = 0
            self.has_rolled = False
            self.dev_drawn = -1

        # Apply the changes to the board
        board.update_board(self, move)
        return 1

    # A helper function to handle playing dev cards
    def dev_card_handler(self, board, deck, players, move):

        # Handle the knight
        if move.card_type == Card.KNIGHT:
            self.num_knights_played += 1
        # Handle road builder; give the player resources for 2 roads then call
        # make_move for building roads until they place 2 valid roads
        elif move.card_type == Card.ROAD_BUILDING:
            self.num_road_builder_played += 1
            if move.road != None:
                self.add_road(board, move.road)
            if move.road2 != None:
                self.add_road(board, move.road2)
        # year of plenty; choose 2 cards to receive
        elif move.card_type == Card.YEAR_OF_PLENTY:
            possible_cards = ['w', 'l', 'g', 'b', 'o']
            self.num_yop_played += 1
            self.resources[move.resource] += 1
            self.resources[move.resource2] += 1

        # monopoly: choose a card and steal it from all other players
        elif move.card_type == Card.MONOPOLY:
            self.num_monopoly_played += 1


    # A helper function to decrement the resources correctly if the trade
    # with bank option is chosen.
    def trade_resources(self, old_res, new_res):
        if '2 ' + old_res in self.ports:
            self.resources[old_res] -= 2
        elif '3' in self.ports:
            self.resources[old_res] -= 3
        else:
            self.resources[old_res] -= 4
        self.resources[new_res] += 1
        return


    # A helper function to check if we can build a settlement at a specific
    # location
    def can_build_settlement(self, coord, board):

        # Check that the coordinates are valid
        if coord not in board.coords:
            return False

        state = board.coords[coord]

        # Does not overlap with already created settlement
        if state.player == None:
            next_list = list(state.roads.keys()) + state.available_roads

            # Two spaces away from another settlement
            for n in next_list:
                next_state = board.coords[n]
                if next_state.player:
                    return False
            return True
        if self.print_invalid_move():
            print('Cannot build settlement here...')
        return False


    # A helper function to check if we can build a road at a specific
    # location
    def can_build_road(self, move, board):
        road_coords = list(move.road)
        if road_coords[0] in board.coords.keys():
            state_o = board.coords[road_coords[0]]

            # Does not overlap with already created road
            if road_coords[1] in state_o.available_roads:

                # Next to another road or settlement
                if move.road & (set(self.roads.keys()) | set(self.settlements)):
                    return True
        if self.print_invalid_move():
            print('Cannot build road here...')
        return False

    # Can the player accept the trade? trade_map is a map of the resources
    # that another player is asking for from this player
    def can_accept_trade(self, trade_map):
        return self.resources[trade_map[0]] >= int(trade_map[1])
