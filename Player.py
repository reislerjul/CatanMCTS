# The player class. Each player should keep track of their roads, cities, 
# settlements, dev cards, whether they're on a port, number of victory
# points, and resource cards. 
import random
class Player():


    # TODO: Complete this constructor. player_type should be 0 if the player is
    # human, 1 if the player is the random AI, and 2 if the player is the 
    # MCTS AI
    def __init__(self, player_type):
        self.9 = ''
        self.resources = {'w':0, 'b':0, 'l':0, 'g':0, 'o':0}
        self.vp_dev_cards = 0
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


    # A getter function to return the player's hand of dev cards
    def get_dev_cards(self):
        return self.dev_cards

    # Allows the game to access the number of victory points that a player has
    def calculate_vp(self):
        return self.vp_dev_cards + len(self.cities.items()) + \
        len(self.settlements.items()) + self.longest_road + self.largest_army


    # TODO: implement a function that allows the players to choose their 
    # settlement and road placement at the beginning of the game
    def choose_spot(self, board):
        self.resources['l'] += 2
        self.resources['b'] += 2
        self.resources['g'] += 1
        self.resources['w'] += 1
        make_move(1, board, None)
        make_move(2, board, None)
        return board


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
    def check_legal_move(self, move, move_type, board, deck=None):
        if move_type == 1 and move[0] in board.coords.keys():
            # Resources available to make a road
            if self.resources['b'] >= 1 and self.resources['l'] >=1:
                state_o = board.coords[move[0]]
                # Does not overlap with already created road
                if move[1] in state_o['available roads']:
                    # Next to another road or settlement
                    if (move[0] in self.roads.keys()) or (move[1] in self.roads.keys()) \
                        or (move[0] in self.settlements) or (move[1] in self.settlements)):
                            return True

        if move_type == 2 and move in board.coords.keys():
            # Resources available to make a settlement
            if self.resources['b'] >= 1 and self.resources['l'] >=1 and \
               self.resources['g'] >= 1 and self.resources['w'] >=1:
               state = board.coords[move]
               # Does not overlap with already created settlement
               if state['player'] == 0:
                    next_list = state['roads'] + state['available roads']
                    # Next to another road
                    if (move in self.roads.keys()):
                        # Two spaces away from another settlement
                        for next in next_list:
                            next_state = board.coords[next]
                            if next_state['player'] != 0:
                                return False
                        return True
            
        if move_type == 3 and move in board.coords.keys():
            # Resources available to make a city
            if self.resources['o'] >= 3 and self.resources['g'] >=2:
                # Have a settlement at that spot
                state = board.coords[move]
                if state['player'] == self.player_name:
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

        if move_type == 7 and move in board.coords.keys():
            return True

        return False


    # TODO: this should represent a single move within a turn. Return 
    # 0 if we are passing our turn, 1 if the move is a valid move, 
    # -1 if the move is not legal
    def make_move(self, move_type, board, deck):

    legal_move = False
    while not legal_move:
        # End turn
        if move_type == 0:
            legal_move = True
            return 0

        # Build a road
        elif move_type == 1:
            move = self.build_road(board)
            legal_move = self.check_legal_move(move, move_type, board)
            if legal_move:
                self.resources['b'] -= 1
                self.resources['l'] -= 1
                self.roads[move[0]] = move[1]
                self.roads[move[1]] = move[0]

        # Build a settlement
        elif move_type == 2:
            move = self.build_settlement(board)
            legal_move = self.check_legal_move(move, move_type, board)
            if legal_move:
                self.resources['b'] -= 1
                self.resources['l'] -= 1
                self.resources['g'] -= 1
                self.resources['w'] -= 1
                self.settlements.append(move)
                state = board.coords[move]
                if state.ports != '':
                    self.ports.append(state.ports)

        # Build a city
        elif move_type == 3:
            move = self.build_city(board)
            legal_move = self.check_legal_move(move, move_type, board)
            if legal_move:
                self.resources['o'] -= 3
                self.resources['g'] -= 2
                self.cities.append(move)

        # Draw a dev card
        elif move_type == 4:
            legal_move = self.check_legal_move(None, move_type, board, deck)
            if legal_move:
                move = self.drawDevCard(deck)

        # Play a dev card 
        #################### PLAY ONLY ONE ######################
        elif move_type == 5:
            move = self.playDevCard(board, deck)
            legal_move = self.check_legal_move(move, move_type, board, deck)
            if legal_move:
                self.dev_cards[move] -= 1
                if move == 'Knight':
                    self.largest_army += 1
                    move_type = 7
        #################### PLAY ONLY ONE ######################

        # Trade with bank
        elif move_type == 6:
            move = self.trade(board)
            legal_move = self.check_legal_move(move, move_type, board)
            if legal_move:
                oldRes = move[0]
                newRes = move[1]
                self.resources[newRes] += 1
                self.resources[oldRes[1]] -= int(oldRes[0])

        # Move robber
        if move_type == 7:
            move = self.moveRobber(board)
            legal_move = self.check_legal_move(move, move_type, board)
            move_type = 6

        if not legal_move and self.player_type == 0: 
            print('Illegal move')
        elif not legal_move:
            continue
        else:
            return 1 


    
    # TODO: this function will be used to choose the move. it should 
    # be different depending on whether the player is a random AI, 
    # human, or MCTS AI
    def decide_move(self):
        if self.player_type == 0:
            print('Moves available:')



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
    def make_turn(self, board):

        while True:
            move = self.decide_move()

            # We made a move that is not passing our turn
            if self.make_move(move) == 1:
                board.update_board()

                # Did the move cause us to win?
                if self.calculate_vp() >= 10:
                    return 1

            # TODO: change this to 0 when we atually have the game playable
            elif self.make_move(move) == 0:
                return 1

    def build_road(self, board):
        if self.player_type == 0:
            r0,c0 = map(int, input("Coordinate for road origin (Input form: row# col#): ").split)
            r1,c1 = map(int, input("Coordinate for road origin (Input form: row# col#): ").split)
            print('Building road from (', r0, ', ', c0, ') to (', r1, ', ', c1, ') ...')
        elif self.player_type == 1:
            r0 = random.randint(0, 11)
            c0 = random.randint(0, 5)
            r1 = r0 + random.randint(-1, 1)
            c1 = c0 + random.randint(-1, 1)
        move = [(r0, c0), (r1, c1)]
        return move     # List of tuples: two coordinates

    def build_settlement(self, board):
        if self.player_type == 0:
            r,c = map(int, input("Coordinate for settlement (Input form: row# col#): ").split)
            print('Building settlement at (', r, ', ', c, ') ...')
        elif self.player_type == 1:
            r = random.randint(0, 11)
            c = random.randint(0, 5)
        move = (r, c)
        return move     # Tuple: one coordinate

    def build_city(self, board):
        if self.player_type == 0:
            r,c = map(int, input("Coordinate for city (Input form: row# col#): ").split)
            print('Building city at (', r, ', ', c, ') ...')
        elif self.player_type == 1:
            r = random.randint(0, 11)
            c = random.randint(0, 5)
        move = (r, c)
        return move     # Tuple: one coordinate

    def drawDevCard(self, deck):
        move = deck.take_card(self)
        return move

    ##################################### WRITE DEV CARD CODE #####################################
    def playDevCard(self, board, deck):
        if self.player_type == 0:
            move = input("Which dev card do you want to play (Choose from form: Knight, Road Building, Monopoly, Year of Plenty): ")
            print('Playing dev card ...')
            move = (r, c)
        elif self.player_type == 1:
            #move = 
        return move
    ##################################### WRITE DEV CARD CODE #####################################

    def trade(self, board):
        if self.player_type == 0:
            numCards = input("How many cards do you want to trade?")
            card = input("Lumber, Ore, Wool, Brick, or Grain? (Input form: l, o, w, b, g)")
            oldRes = (numCards, card)
            newRes = input("Which resource would you like in exchange? (Input form: l, o, w, b, g)")
            move = (oldRes, newRes)
        elif self.player_type == 0:


        return move     # Tuple of tuple: Trade of multiple cards for one card

            

