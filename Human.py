from Player import Player

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
    def move_robber(self, board, spot, victim):
        while True:
            invalid = self.make_move(7, board, None, (spot, victim))
            if invalid == 1:
                return


    def choose_victim(self, board, move):
        victim = None

        # Determine the players adjacent to the robber
        possible_players = [p for p in board.players_adjacent_to_hex(move.coord) if p is not self]

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


    def choose_robber_position(self):
        r,c = map(int, input("Where are you moving the robber? (Input form: row# col#): ").split())
        return (r, c)


    def choose_card(self, string):
        full_string = "Choose " + string + " card"
        return input(full_string)


    def decide_move(self, dev_played, board, deck, players, robber):
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


    def choose_road(self, board):
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

