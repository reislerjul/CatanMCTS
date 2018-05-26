import random
import settings

# The player class. Each player should keep track of their roads, cities, 
# settlements, dev cards, whether they're on a port, number of victory
# points, and resource cards. 
class Player():


    # TODO: Complete this constructor. player_type should be 0 if the player is
    # human, 1 if the player is the random AI, and 2 if the player is the 
    # MCTS AI
    def __init__(self, player_type, player_num):
        self.player_num = player_num
        self.resources = {'w':0, 'b':0, 'l':0, 'g':0, 'o':0}
        self.player_type = player_type
        self.dev_cards = {'Knight': 0, 'Victory Point': 0,\
            'Road Building':0, 'Monopoly': 0, 'Year of Plenty': 0} #{type: #cards}
        self.num_knights_played = 0
        self.longest_road = 0
        self.largest_army = 0
        self.ports = []    # {} 
        self.cities = []    # [(0,0), (1,1)...]
        self.settlements = []   #[(0,0), (1,1)...]
        self.roads = {}     # {(0,0):(1,1), (1,1):(0,0)...}

    # When in debug mode, use this function to print out the player's fields in a 
    # readable way. 
    def printResources(self):
        print("\nPlayer", self.player_num)
        print('Resources:', self.resources)
        print("     w: " + str(self.resources['w']))
        print("     l: " + str(self.resources['l']))
        print("     b: " + str(self.resources['b']))
        print("     o: " + str(self.resources['o']))
        print("     g: " + str(self.resources['g']))

        total_resources = 0
        
        for resource in self.resources.values():
            total_resources += resource
            

        print("Total Resources: " + str(total_resources))

        print('Dev Cards:', self.dev_cards)
        print("     Knights: " + str(self.dev_cards['Knight']))
        print("     Victory Point: " + str(self.dev_cards['Victory Point']))
        print("     Road Building: " + str(self.dev_cards['Road Building']))
        print("     Monopoly: " + str(self.dev_cards['Monopoly']))
        print("     Year of Plenty: " + str(self.dev_cards['Year of Plenty']))
        print("Longest Road Points: " + str(self.longest_road))
        print("Largest Army Points: " + str(self.largest_army))

        print('Number of Victory Points: ', self.calculate_vp())
        print('Knights Played: ', self.num_knights_played)
        print('Roads: ', self.roads)
        print('Settlements: ', self.settlements)
        print('Cities: ', self.cities)
        print("Ports: ", self.ports)
        return 0



    # A getter function to return the player's hand of dev cards
    def get_dev_cards(self):
        return self.dev_cards

    # Allows the game to access the number of victory points that a player has
    def calculate_vp(self):
        return self.dev_cards['Victory Point'] + len(self.cities) + \
        len(self.settlements) + self.longest_road + self.largest_army


    # A function that allows the players to choose their 
    # settlement and road placement at the beginning of the game
    def choose_spot(self, board, idx):
        legal_settlement = False
        legal_road = False

        while not legal_settlement:

            # Pick a legal spot 
            if self.player_type == 0:
                loc = self.build_settlement(board)

            # This may yield coordinates that are not valid
            elif self.player_type == 1:
                loc = (random.randint(0, 11), random.randint(0, 5))

            legal_settlement = self.can_build_settlement(loc, board)

        # Add the settlement to the board and update player fields
        self.settlements.append(loc)
        state = board.coords[loc]
        if state['ports'] != '':
            self.ports.append(state['ports'])
        if idx == 2:
            board.add_settlement(self, loc, True)
        else:
            board.add_settlement(self, loc)

        # Choose where to play a road
        while not legal_road:

            if self.player_type == 0:
                move = self.build_road(board)
            elif self.player_type == 1:

                # Choose from set of roads coming from settlement; any should work
                possible_sinks = state['available roads']
                sink = possible_sinks[random.randint(0, len(possible_sinks) - 1)]
                move = (loc, sink)

            legal_road = self.can_build_road(move, board)

        # build the road
        self.roads[move[0]] = move[1]
        self.roads[move[1]] = move[0]
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
    def check_legal_move(self, move, move_type, board, deck):
        if move_type == 1 and move[0] in board.coords.keys():
            # Resources available to make a road
            if self.resources['b'] >= 1 and self.resources['l'] >=1:
                state_o = board.coords[move[0]]
                # Does not overlap with already created road
                if move[1] in state_o['available roads']:
                    # Next to another road or settlement
                    if (move[0] in self.roads.keys()) or (move[1] in self.roads.keys()) or \
                    (move[0] in self.settlements) or (move[1] in self.settlements):
                            return True

        if move_type == 2 and move in board.coords.keys():
            # Resources available to make a settlement
            if self.resources['b'] >= 1 and self.resources['l'] >=1 and \
               self.resources['g'] >= 1 and self.resources['w'] >=1:
               state = board.coords[move]
               # Does not overlap with already created settlement
               if state['player'] == 0:
                    next_list = list(state['roads'].keys()) + state['available roads']
                    # Next to another road
                    if (move in self.roads.keys()):
                        # Two spaces away from another settlement
                        for next in next_list:
                            next_state = board.coords[next]
                            if next_state['player'] != 0:
                                return False
                        return True
            
        # Have a settlement at that spot
        if move_type == 3 and move in self.settlements:
            # Resources available to make a city
            if self.resources['o'] >= 3 and self.resources['g'] >=2:
                return True

        if move_type == 4:
            # Resources available to draw a dev card and enough dev cards in deck
            if self.resources['o'] >= 1 and self.resources['g'] >=1 \
                and self.resources['w'] >=1 and deck.cards_left > 0:
                return True

        if move_type == 5:
            # Dev card available and not a victory point card
            if move in self.dev_cards.keys() and self.dev_cards[move] > 0 and move != 'Victory Point':
                return True

        if move_type == 6:
            oldRes = move[0]
            newRes = move[1]
            if int(oldRes[0]) == 4 and self.resources[oldRes[1]] >=4:
                return True
            elif int(oldRes[0]) == 3 and self.resources[oldRes[1]] >=3 \
                and (oldRes[0] in self.ports):
                return True
            elif int(oldRes[0]) == 2 and self.resources[oldRes[1]] >=2 \
                and ((oldRes[0]+ ' ' + oldRes[1]) in self.ports):
                return True

        if move_type == 7 and move[0] in board.coords.keys():
            return True

        if move_type == 0:
            return True

        return False


    # TODO: this should represent a single move within a turn. Return 
    # 0 if we are passing our turn, 1 if the move is a valid move, 
    # -1 if the move is not legal
    def make_move(self, move_type, board, deck, move):

        # Play corresponds to the information that the board may 
        # need when a dev card is played
        play = None

        if not self.check_legal_move(move, move_type, board, deck):
            if self.player_type == 0:
                print("Illegal move!")
            return -1

        # This is a legal move so if we're in debug mode, we should 
        # print the move out! 
        if settings.DEBUG:
            print("Printing the move:")
            print("Move type: " + str(move_type))
            print("Move: " + str(move))

        # End turn
        if move_type == 0:
            return 0

        # Build a road
        elif move_type == 1:
            self.resources['b'] -= 1
            self.resources['l'] -= 1
            self.roads[move[0]] = move[1]
            self.roads[move[1]] = move[0]

        # Build a settlement
        elif move_type == 2:
            self.resources['b'] -= 1
            self.resources['l'] -= 1
            self.resources['g'] -= 1
            self.resources['w'] -= 1
            self.settlements.append(move)
            state = board.coords[move]
            if state['ports'] != '':
                self.ports.append(state['ports'])

        # Build a city
        elif move_type == 3:
            self.resources['o'] -= 3
            self.resources['g'] -= 2
            self.cities.append(move)
            self.settlements.remove(move)

        # Draw a dev card
        elif move_type == 4:
            self.drawDevCard(deck)
            self.resources['w'] -= 1
            self.resources['g'] -= 1
            self.resources['o'] -= 1

        # Play a dev card 
        elif move_type == 5:
            self.dev_cards[move] -= 1
            play = self.dev_card_handler(move, board)

            # If the dev card is road building, we've covered this in 
            # the dev card handler, so we can just return
            if move == 'Road Building':
                return 1                

        # Trade with bank
        elif move_type == 6:
            self.trade_resources(move[0], move[1])

        # Move robber.
        if move_type == 7:
            play = move[1]
            move = move[0]

        # Apply the changes to the board
        board.update_board(self, move_type, move, play)

        return 1


    # A helper function for moving the robber in the case of rolling a 7 
    def moveRobber(self, board):
        while True:
            if self.player_type == 0:
                r,c = map(int, input("Where are you moving the robber? (Input form: row# col#): ").split())
                spot = (r, c)
            elif self.player_type == 1:
                spots = [(4, 1), (2, 1), (3, 3), (1, 0), (2, 3), (1, 2), (4, 0), \
                (1, 1), (4, 2), (2, 4), (3, 0), (0, 2), (3, 2), (1, 3), (3, 1), \
                (0, 0), (2, 2), (0, 1)]
                spots.remove(self.board.robber)
                spot = spots[random.randint(0, len(spots) - 1)]
            victim = self.choose_victim(board, spot)
            invalid = self.make_move(7, board, None, (spot, victim))
            if invalid == 1:
                return


    # A helper function to move the robber and steal from 
    # a player 
    def choose_victim(self, board, move):

        victim = None

        # Determine the players adjacent to the robber
        possible_players = board.players_adjacent_to_hex(move)
        
        # Get a list of the player numbers
        player_nums = []
        for player in possible_players:
            player_nums.append(player.player_num)

        # We can't steal from ourself! 
        if self in possible_players:
            possible_players.remove(self)
            player_nums.remove(self.player_num)

        if len(possible_players) > 0:

            # Keep prompting the person until they enter a valid victim
            while True:

                if self.player_type == 0:
                    num = int(input("Who do you want to steal from? (give player number)"))

                    if num in player_nums:
                        victim = possible_players[player_nums.index(num)]
                        break
                    else:
                        print("Invalid victim. Please enter a valid player to steal from.")

                elif self.player_type == 1:
                    victim = possible_players[random.randint(0, len(possible_players) - 1)]
                    break
        return victim


    # TODO: add dev cards other than knights
    # A helper function to handle playing dev cards
    def dev_card_handler(self, card_type, board):

        # Handle the knight
        if card_type == 'Knight':
            self.num_knights_played += 1
            if self.player_type == 0:
                r,c = map(int, input("Where are you moving the robber? (Input form: row# col#): ").split())
                spot = (r, c)
            elif self.player_type == 1:
                spots = [(4, 1), (2, 1), (3, 3), (1, 0), (2, 3), (1, 2), (4, 0), \
                (1, 1), (4, 2), (2, 4), (3, 0), (0, 2), (3, 2), (1, 3), (3, 1), \
                (0, 0), (2, 2), (0, 1)]
                spots.remove(self.board.robber)
                spot = spots[random.randint(0, len(spots) - 1)]
            victim = self.choose_victim(board, spot)
            return (spot, victim)

        # Handle road builder; give the player resources for 2 roads then call
        # make_move for building roads until they place 2 valid roads
        if card_type == "Road Building":
            self.resources['l'] += 2
            self.resources['b'] += 2
            roads_played = 0
            while roads_played < 2:
                if self.player_type == 0:
                    move = self.build_road(board)
                elif self.player_type == 1:
                    move = self.choose_road(board)
                if self.make_move(1, board, None, move) == 1:
                    roads_played += 1
            return None

        # year of plenty; choose 2 cards to receive
        possible_cards = ['w', 'l', 'g', 'b', 'o']
        if card_type == "Year of Plenty":
            if self.player_type == 0:
                card1 = input("Choose first card")
                card2 = input("Choose second card")
            elif self.player_type == 1:
                card1 = possible_cards[random.randint(0, len(possible_cards))]
                card2 = possible_cards[random.randint(0, len(possible_cards))]
            self.resources[card1] += 1
            self.resources[card2] += 1
            return None

        # monopoly: choose a card and steal it from all other players
        if card_type == "Monopoly":
            if self.player_type == 0:
                card_choice = input("Choose card to monopoly!")
            else:
                card_choice = possible_cards[random.randint(0, len(possible_cards))]
            return card_choice




    # A helper function for the random AI to randomly decide on an available 
    # road to play. 
    def choose_road(self, board):
        possible_roads = {}

        for road_source in self.roads.keys():
            possible_sinks = \
            board.coords[road_source]['available roads']

            for sink in possible_sinks:
                if (road_source, sink) not in possible_roads and \
                (sink, road_source) not in possible_roads:
                    possible_roads[(sink, road_source)] = True

        options = possible_roads.keys()
        return options[random.randint(0, len(options) - 1)]


    # A helper function to decrement the resources correctly if the trade 
    # with bank option is chosen.
    def trade_resources(self, oldRes, newRes):
        if '2 ' + oldRes[1] in self.ports:
            self.resources[oldRes[1]] -= 2
        elif '3' in self.ports:
            self.resources[oldRes[1]] -= 3
        else:
            self.resources[oldRes[1]] -= 4
        self.resources[newRes] += 1
        return
    

    # TODO: this function will be used to choose the move. it should 
    # be different depending on whether the player is a random AI, 
    # human, or MCTS AI
    def decide_move(self, dev_played, board):
        if self.player_type == 0:

            self.printResources()
            print('Moves available:')
            print('Enter 0 for ending/passing your turn')
            print('Enter 1 to build a road ')
            print('Enter 2 to build a settlement ')
            print('Enter 3 to build a city ')
            print('Enter 4 to draw a dev card ')
            print('Enter 5 to play a dev card ')
            print('Enter 6 to make a trade ')
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

        elif self.player_type == 1:

            # We can always end our turn
            possible_moves = [(0)]

            # Can we buy dev card?
            if self.resources['g'] > 0 and self.resources['w'] > 0 \
            and self.resources['o'] > 0:
                possible_moves.append((4))

            # Can we play a dev card?
            if dev_played == 0:
                for card in self.dev_cards.keys():
                    if card != 'Victory Point':
                        possible_moves.append((5, card))

            # Can we build a city?
            if self.resources['g'] >= 2 and self.resources['o'] >= 3 and \
            len(self.cities) < 4:
                for settlement in self.settlements:
                    possible_moves.append((3, settlement))

            # Can we build a road?
            if self.resources['b'] > 0 and self.resources['l'] > 0:
                # Get the set of possible places we can build a road 
                possible_roads = {}

                for road_source in self.roads.keys():
                    possible_sinks = \
                    board.coords[road_source]['available roads']

                    for sink in possible_sinks:
                        if (road_source, sink) not in possible_roads and \
                        (sink, road_source) not in possible_roads:
                            possible_roads[(sink, road_source)] = True

                # We now have the possible roads, so lets add those moves!
                for road in possible_roads:
                    possible_moves.append((1, road))

            # Can we build a settlement?
            if self.resources['w'] > 0 and self.resources['l'] > 0 and \
            self.resources['b'] > 0 and self.resources['g'] > 0:

                # Check the possible places for us to build a settlement
                for source in self.roads.keys():
                    if (can_build_settlement(source, board)):
                        possible_moves.append((2, source))

            # Should we trade in resources? Try cases for the 5 different resources
            if (self.resources['w'] >= 2 and '2 w' in self.ports) or \
            (self.resources['w'] >= 3 and '3' in self.ports) or (self.resources['w'] >= 4):
                possible_moves.append((6, ('w', 'o')))
                possible_moves.append((6, ('w', 'l')))
                possible_moves.append((6, ('w', 'g')))
                possible_moves.append((6, ('w', 'b')))

            if (self.resources['o'] >= 2 and '2 o' in self.ports) or \
            (self.resources['o'] >= 3 and '3' in self.ports) or (self.resources['o'] >= 4):
                possible_moves.append((6, ('o', 'w')))
                possible_moves.append((6, ('o', 'l')))
                possible_moves.append((6, ('o', 'g')))
                possible_moves.append((6, ('o', 'b')))

            if (self.resources['l'] >= 2 and '2 l' in self.ports) or \
            (self.resources['l'] >= 3 and '3' in self.ports) or (self.resources['l'] >= 4):
                possible_moves.append((6, ('l', 'o')))
                possible_moves.append((6, ('l', 'w')))
                possible_moves.append((6, ('l', 'g')))
                possible_moves.append((6, ('l', 'b')))

            if (self.resources['b'] >= 2 and '2 b' in self.ports) or \
            (self.resources['b'] >= 3 and '3' in self.ports) or (self.resources['b'] >= 4):
                possible_moves.append((6, ('b', 'l')))
                possible_moves.append((6, ('b', 'o')))
                possible_moves.append((6, ('b', 'w')))
                possible_moves.append((6, ('b', 'g')))

            if (self.resources['g'] >= 2 and '2 g' in self.ports) or \
            (self.resources['g'] >= 3 and '3' in self.ports) or (self.resources['g'] >= 4):
                possible_moves.append((6, ('g', 'l')))
                possible_moves.append((6, ('g', 'o')))
                possible_moves.append((6, ('g', 'w')))
                possible_moves.append((6, ('g', 'b')))

            # Choose a move randomly from the set of possible moves! 
            return list(possible_moves[random.randint(0, len(possible_moves) - 1)])



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
        if self.player_type == 0:
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
        if self.player_type == 0:
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
    def make_turn(self, board, deck):

        # This should indicate whether a dev card has already been 
        # played during this turn. If so, we can't play another one. 
        dev_played = 0

        while True:

            move = self.decide_move(dev_played, board)
            # move is list

            move_type = move[0]
            move_instructs = None
            if len(move) > 1:
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

            

