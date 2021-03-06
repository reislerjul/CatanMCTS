import numbers 

class Card():
    '''
    Represents each of the card types
    '''
    KNIGHT = 0
    VICTORY_POINT = 1
    ROAD_BUILDING = 2
    MONOPOLY = 3
    YEAR_OF_PLENTY = 4

    def get_card_name(self, card):
        '''
        Returns name of the card id given
        '''
        return {0 : 'Knight', 1 : 'Victory Point',\
            2 : 'Road Building', 3 : 'Monopoly', 4 : 'Year of Plenty'}[card]

class Move():
    END_TURN = 0
    BUY_ROAD = 1
    BUY_SETTLEMENT = 2
    BUY_CITY = 3
    BUY_DEV = 4
    PLAY_DEV = 5
    TRADE_BANK = 6
    PROPOSE_TRADE = 7
    MOVE_ROBBER = 8
    ACCEPT_TRADE = 9
    ROLL_DICE  = 10
    DECLINE_TRADE = 11
    CHOOSE_TRADER = 12
    DISCARD_HALF = 13

    def __init__(self,
                 move_type,
                 card_type=None,
                 road=None,
                 road2=None,
                 coord=None,
                 player=None,
                 give_resource=None,
                 resource=None,
                 resource2=None,
                 roll=None):
        self.move_type = move_type
        self.card_type = card_type
        self.road = road
        self.road2 = road2
        self.coord = coord
        self.player = player
        self.give_resource = give_resource
        self.resource = resource
        self.resource2 = resource2
        self.roll = roll

    def copy_move(self):
        new_move = Move(self.move_type, card_type=self.card_type, road=self.road, \
            road2=self.road2, coord=self.coord, player=self.player, \
            give_resource=self.give_resource, resource=self.resource, \
            resource2=self.resource2, roll=self.roll)
        return new_move

    def __str__(self):
        s = 'Move(move_type: {}'.format(self.move_type)
        s += ', card_type: {}'.format(self.card_type)
        s += ', road: {}'.format(self.road)
        s += ', road 2: {}'.format(self.road2)
        s += ', coord: {}'.format(self.coord)
        if isinstance(self.player, numbers.Number) or self.player == None or isinstance(self.player, tuple):
            s += ', player: {}'.format(self.player)
        else:
            s += ', player: {}'.format(self.player.player_num)
        s += ', give_resource: {}'.format(self.give_resource)
        s += ', resource: {}'.format(self.resource)
        s += ', resource 2: {}'.format(self.resource2)
        s += ', roll: {}'.format(self.roll)
        s += ')'
        return s

    def __hash__(self):
        return hash((self.move_type,
                     self.card_type,
                     self.road,
                     self.road2,
                     self.coord,
                     self.player,
                     self.give_resource,
                     self.resource,
                     self.resource2,
                     self.roll))

    def __eq__(self, other):
        return ((self.move_type,
                 self.card_type,
                 self.road,
                 self.road2,
                 self.coord,
                 self.player,
                 self.give_resource,
                 self.resource,
                 self.resource2,
                 self.roll) ==
                 (other.move_type,
                 other.card_type,
                 other.road,
                 other.road2,
                 other.coord,
                 other.player,
                 other.give_resource,
                 other.resource,
                 other.resource2,
                 other.roll))
