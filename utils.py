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
    DRAW_DEV = 11

    def __init__(self,
                 move_type,
                 card_type=None,
                 road=None,
                 coord=None,
                 player=None,
                 num_trade=None,
                 give_resource=None,
                 resource=None,
                 roll=None):
        self.move_type = move_type
        self.card_type = card_type
        self.road = road
        self.coord = coord
        self.player = player
        self.num_trade = num_trade
        self.give_resource = give_resource
        self.resource = resource
        self.roll = roll

    def __str__(self):
        s = 'Move(move_type: {}'.format(self.move_type)
        s += ', card_type: {}'.format(self.card_type)
        s += ', road: {}'.format(self.road)
        s += ', coord: {}'.format(self.coord)
        s += ', player: {}'.format(self.player)
        s += ', num_trade: {}'.format(self.num_trade)
        s += ', give_resource: {}'.format(self.give_resource)
        s += ', resource: {}'.format(self.resource)
        s += ', roll: {}'.format(self.roll)
        s += ')'
        return s

    def __hash__(self):
        return hash((self.move_type,
                     self.card_type,
                     self.road,
                     self.coord,
                     self.player,
                     self.num_trade,
                     self.give_resource,
                     self.resource,
                     self.roll))

    def __eq__(self, other):
        return ((self.move_type,
                 self.card_type,
                 self.road,
                 self.coord,
                 self.player,
                 self.num_trade,
                 self.give_resource,
                 self.resource,
                 self.roll) ==
                 (other.move_type,
                 other.card_type,
                 other.road,
                 other.coord,
                 other.player,
                 other.num_trade,
                 other.give_resource,
                 other.resource,
                 other.roll))
