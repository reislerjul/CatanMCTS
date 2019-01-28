import random
import settings

from utils import Card, Move

class Coord():
    def __init__(self,
                 location,
                 player=None,
                 resource_locs=[],
                 ports=set(),
                 neighbours=[]):
        self.player = player
        self.location = location
        self.settlement = True
        self.resource_locs = resource_locs
        self.ports = ports
        self.neighbours = neighbours
        self.roads = {n: 0 for n in neighbours}
        self.available_roads = self.neighbours[:]


# This represents the catan board. The board should essentially have a
# coordinate system that keeps track of where the ports are, where each
# resource is, the number that is on each hexagon, where cities/settlements
# are, where the robber is.
class Board():

    def __init__(self, players):
        self.players = players
        self.robber = (2,0)
        self.resources = self.init_resources()
        self.hex = self.init_hexes()
        self.coords = self.init_board(debug=False)
        self.r_allocator = {}
        self.adjacent = {}
        self.largest_army_size = 2
        self.largest_army_player = None
        self.longest_road_size = 4
        self.longest_road_player = None
        self.resource_list = ['w', 'b', 'l', 'g', 'o']
        self.active_player = None
        self.round_num = 0
        self.pending_trade = False
        self.traders = []
        self.trade_step = 0


    def init_board(self, debug=False):
        '''
        creates the coordinate system and inits the board
        the coordinate system for settlements and road is defined as
        0,0 is top row leftest open location. First coordinate is the row
        second coordinate is the column. dictionaries are used so we can store
        more info about the games state
        '''
        coords = {}
        coords[(0, 0)] = Coord((0, 0),
                               resource_locs=[(0, 0)],
                               ports={'3'},
                               neighbours=[(1, 0), (1, 1)])
        coords[(0, 1)] = Coord((0, 1),
                               resource_locs=[(0, 1)],
                               ports={'2 w'},
                               neighbours=[(1, 1), (1, 2)])
        coords[(0, 2)] = Coord((0, 2),
                               resource_locs=[(0, 2)],
                               neighbours=[(1, 2), (1, 3)])

        coords[(1, 0)] = Coord((1, 0),
                               resource_locs=[(0, 0)],
                               ports={'3'},
                               neighbours=[(2, 0), (0, 0)])
        coords[(1, 1)] = Coord((1, 1),
                               resource_locs=[(0, 0), (0, 1)],
                               neighbours=[(0, 0), (0, 1), (2, 1)])
        coords[(1, 2)] = Coord((1, 2),
                               resource_locs=[(0, 1), (0, 2)],
                               ports={'2 w'},
                               neighbours=[(0, 2), (0, 1), (2, 2)])
        coords[(1, 3)] = Coord((1, 3),
                               resource_locs=[(0, 2)],
                               neighbours=[(0, 2), (2, 3)])

        coords[(2, 0)] = Coord((2, 0),
                               resource_locs=[(0, 0), (1, 0)],
                               neighbours=[(3, 0), (1, 0), (3, 1)])
        coords[(2, 1)] = Coord((2, 1),
                               resource_locs=[(0, 0), (0, 1), (1, 1)],
                               neighbours=[(3, 1), (1, 1), (3, 2)])
        coords[(2, 2)] = Coord((2, 2),
                               resource_locs=[(0, 2), (0, 1), (1, 2)],
                               neighbours=[(3, 2), (1, 2), (3, 3)])
        coords[(2, 3)] = Coord((2, 3),
                               resource_locs=[(0, 2), (1, 3)],
                               ports={'3'},
                               neighbours=[(3, 3), (1, 3), (3, 4)])

        coords[(3, 0)] = Coord((3, 0),
                               resource_locs=[(1, 0)],
                               ports={'2 o'},
                               neighbours=[(4, 0), (2, 0)])
        coords[(3, 1)] = Coord((3, 1),
                               resource_locs=[(1, 0), (0, 0), (1, 1)],
                               neighbours=[(4, 1), (2, 0), (2, 1)])
        coords[(3, 2)] = Coord((3, 2),
                               resource_locs=[(1, 1), (0, 1), (1, 2)],
                               neighbours=[(4, 2), (2, 2), (2, 1)])
        coords[(3, 3)] = Coord((3, 3),
                               resource_locs=[(1, 2), (0, 2), (1, 3)],
                               neighbours=[(4, 3), (2, 3), (2, 2)])
        coords[(3, 4)] = Coord((3, 4),
                               resource_locs=[(1, 2)],
                               ports={'3'},
                               neighbours=[(2, 3), (4, 4)])

        coords[(4, 0)] = Coord((4, 0),
                               resource_locs=[(1, 0), (2, 0)],
                               ports={'2 o'},
                               neighbours=[(3, 0), (5, 0), (5, 1)])
        coords[(4, 1)] = Coord((4, 1),
                               resource_locs=[(1, 0), (1, 1), (2, 1)],
                               neighbours=[(3, 1), (5, 1), (5, 2)])
        coords[(4, 2)] = Coord((4, 2),
                               resource_locs=[(1, 1), (1, 2), (2, 2)],
                               neighbours=[(3, 2), (5, 2), (5, 3)])
        coords[(4, 3)] = Coord((4, 3),
                               resource_locs=[(1, 2), (1, 3), (2, 3)],
                               neighbours=[(3, 3), (5, 3), (5, 4)])
        coords[(4, 4)] = Coord((4, 4),
                               resource_locs=[(1, 3), (2, 4)],
                               neighbours=[(3, 4), (5, 5), (5, 4)])

        coords[(5, 0)] = Coord((5, 0),
                               resource_locs=[(2, 0)],
                               neighbours=[(4, 0), (6, 0)])
        coords[(5, 1)] = Coord((5, 1),
                               resource_locs=[(1, 0), (2, 0), (2, 1)],
                               neighbours=[(6, 1), (4, 0), (4, 1)])
        coords[(5, 2)] = Coord((5, 2),
                               resource_locs=[(1, 1), (2, 1), (2, 2)],
                               neighbours=[(6, 2), (4, 1), (4, 2)])
        coords[(5, 3)] = Coord((5, 3),
                               resource_locs=[(1, 2), (2, 2), (2, 3)],
                               neighbours=[(6, 3), (4, 2), (4, 3)])
        coords[(5, 4)] = Coord((5, 4),
                               resource_locs=[(1, 3), (2, 3), (2, 4)],
                               neighbours=[(6, 4), (4, 3), (4, 4)])
        coords[(5, 5)] = Coord((5, 5),
                               resource_locs=[(2, 4)],
                               ports={'3'},
                               neighbours=[(6, 5), (4, 4)])

        coords[(6, 0)] = Coord((6, 0),
                               resource_locs=[(2, 0)],
                               neighbours=[(5, 0), (7, 0)])
        coords[(6, 1)] = Coord((6, 1),
                               resource_locs=[(3, 0), (2, 0), (2, 1)],
                               neighbours=[(5, 1), (7, 0), (7, 1)])
        coords[(6, 2)] = Coord((6, 2),
                               resource_locs=[(3, 1), (2, 1), (2, 2)],
                               neighbours=[(5, 2), (7, 1), (7, 2)])
        coords[(6, 3)] = Coord((6, 3),
                               resource_locs=[(3, 2), (2, 2), (2, 3)],
                               neighbours=[(5, 3), (7, 2), (7, 3)])
        coords[(6, 4)] = Coord((6, 4),
                               resource_locs=[(3, 3), (2, 3), (2, 4)],
                               neighbours=[(5, 4), (7, 3), (7, 4)])
        coords[(6, 5)] = Coord((6, 5),
                               resource_locs=[(2, 4)],
                               ports={'3'},
                               neighbours=[(5, 5), (7, 4)])

        coords[(7, 0)] = Coord((7, 0),
                               resource_locs=[(3, 0), (2, 0)],
                               ports={'2 g'},
                               neighbours=[(6, 0), (6, 1), (8, 0)])
        coords[(7, 1)] = Coord((7, 1),
                               resource_locs=[(3, 0), (3, 1), (2, 1)],
                               neighbours=[(6, 1), (6, 2), (8, 1)])
        coords[(7, 2)] = Coord((7, 2),
                               resource_locs=[(3, 1), (3, 2), (2, 2)],
                               neighbours=[(6, 2), (6, 3), (8, 2)])
        coords[(7, 3)] = Coord((7, 3),
                               resource_locs=[(3, 2), (3, 3), (2, 3)],
                               neighbours=[(6, 3), (6, 4), (8, 3)])
        coords[(7, 4)] = Coord((7, 4),
                               resource_locs=[(3, 3), (2, 4)],
                               neighbours=[(6, 4), (6, 5), (8, 4)])

        coords[(8, 0)] = Coord((8, 0),
                               resource_locs=[(3, 0)],
                               ports={'2 g'},
                               neighbours=[(7, 0), (9, 0)])
        coords[(8, 1)] = Coord((8, 1),
                               resource_locs=[(3, 0), (3, 1), (4, 0)],
                               neighbours=[(7, 1), (9, 0), (9, 1)])
        coords[(8, 2)] = Coord((8, 2),
                               resource_locs=[(3, 1), (3, 2), (4, 1)],
                               neighbours=[(7, 2), (9, 1), (9, 2)])
        coords[(8, 3)] = Coord((8, 3),
                               resource_locs=[(3, 2), (3, 3), (4, 2)],
                               neighbours=[(7, 3), (9, 2), (9, 3)])
        coords[(8, 4)] = Coord((8, 4),
                               resource_locs=[(3, 3)],
                               ports={'2, b'},
                               neighbours=[(7, 4), (9, 3)])

        coords[(9, 0)] = Coord((9, 0),
                               resource_locs=[(3, 0), (4, 0)],
                               neighbours=[(8, 0), (10, 0), (8, 1)])
        coords[(9, 1)] = Coord((9, 1),
                               resource_locs=[(3, 1), (4, 0), (4, 1)],
                               neighbours=[(8, 1), (10, 1), (8, 2)])
        coords[(9, 2)] = Coord((9, 2),
                               resource_locs=[(3, 2), (4, 1), (4, 2)],
                               neighbours=[(8, 2), (10, 2), (8, 3)])
        coords[(9, 3)] = Coord((9, 3),
                               resource_locs=[(3, 3), (4, 2)],
                               ports={'2 b'},
                               neighbours=[(8, 3), (10, 3), (8, 4)])

        coords[(10, 0)] = Coord((10, 0),
                                resource_locs=[(4, 0)],
                                ports={'3'},
                                neighbours=[(9, 0), (11, 0)])
        coords[(10, 1)] = Coord((10, 1),
                                resource_locs=[(4, 0), (4, 1)],
                                neighbours=[(9, 1), (11, 0), (11, 1)])
        coords[(10, 2)] = Coord((10, 2),
                                resource_locs=[(4, 1), (4, 2)],
                                ports={'2 l'},
                                neighbours=[(9, 2), (11, 1), (11, 2)])
        coords[(10, 3)] = Coord((10, 3),
                                resource_locs=[(4, 2)],
                                neighbours=[(9, 3), (11, 2)])

        coords[(11, 0)] = Coord((11, 0),
                                resource_locs=[(4, 0)],
                                ports={'3'},
                                neighbours=[(10, 0), (10, 1)])
        coords[(11, 1)] = Coord((11, 1),
                                resource_locs=[(4, 1)],
                                ports={'2 l'},
                                neighbours=[(10, 1), (10, 2)])
        coords[(11, 2)] = Coord((11, 2),
                                resource_locs=[(4, 2)],
                                neighbours=[(10, 2), (10, 3)])


        '''
        if debug == True:
            for key, val in coords.items():
                if val.available_roads != val.neighbours:
                    print(key)
                for i in val.resource_locs:
                    try:
                        a = self.resources[i]
                    except IndexError as e:
                        print(key, e)
        '''
        return coords

    # Print the board state
    def print_board_state(self):

        # Print the coordinates if there is a settlement or city there.
        board_items = self.coords.items()
        for coordinate in board_items:
            if coordinate[1].player:
                print("Coordinates: {}\n\n".format(coordinate))
        print("Robber location: {}".format(self.robber))

    def init_resources(self):
        '''
        this function initializes the nodes of resources in a list like faction
        a resource is given by a tuple with the first element being the resource
        the second element being the number on the die needed to roll that resource
        and the third element being a 0, 1 value to denote whether a robbber is at that location and
        this list of resources is a list of list with each location being a hexagonal thing on the map
        i.e. the top left corner https://www.catan.com/en/download/?SoC_rv_Rules_091907.pdf of
        this is a forestt with 11
        w = wool, b= brick, l = lumber, g= grain, o = ore n = none
        '''
        return {(0, 0): ('l',11,0), (0, 1): ('w',12,0), (0, 2): ('g', 9,0),
                (1, 0): ('b', 4,0), (1, 1): ('o', 6,0), (1, 2): ('b', 5,0), (1, 3): ('w',10,0),
                (2, 0): ('n',-1,1), (2, 1): ('l', 3,0), (2, 2): ('g',11,0), (2, 3): ('l', 4,0), (2, 4): ('g', 8,0),
                (3, 0): ('b', 8,0), (3, 1): ('w',10,0), (3, 2): ('w', 9,0), (3, 3): ('o', 3,0),
                (4, 0): ('o', 5,0), (4, 1): ('g', 2,0), (4, 2): ('l', 6,0)}

    def init_hexes(self):
        '''
        input to hexes is a die roll, output is a list of hex coordinates representing the locations
        '''
        return {2: [(4, 1)], 3: [(2, 1), (3, 3)], 4: [(1, 0), (2, 3)], 5: [(1, 2), (4, 0)],
                6: [(1, 1), (4, 2)], 7: [], 8: [(2, 4), (3, 0)], 9: [(0, 2), (3, 2)],
                10: [(1, 3), (3, 1)], 11: [(0, 0), (2, 2)], 12: [(0, 1)]}

    def discard_random(self, player):
        '''
        removes a random resource from the given player and returns it
        '''
        total_resources = sum([player.resources[r] for r in self.resource_list])

        if total_resources > 0:
            r = random.randint(1, total_resources)
            for resource in self.resource_list:
                if r <= player.resources[resource]:
                    player.resources[resource] -= 1
                    return resource
                else:
                    r -= player.resources[resource]
        return None

    def steal_from(self, victim_player, thief_player):
        '''
        gives thief_player a random resource card stolen from victim_player
        '''

        # There is a case where robber is moved and nobody is stolen from
        if victim_player:
            resource = self.discard_random(victim_player)

            # If the player doesn't have a resource, nothing should happen
            if resource:
                self.give_resource(resource, thief_player)

    def players_adjacent_to_hex(self, loc):
        '''
        returns a list of players adjacent to that hex
        '''
        if loc in self.adjacent:
            return self.adjacent[loc]
        else:
            return []

    def move_robber(self, loc, knight=False, player=None):
        '''
        moves the robber to the given hex coordinate
        '''
        self.robber = loc
        if knight:
            if player.num_knights_played > self.largest_army_size:
                # update army size
                self.largest_army_size = player.num_knights_played

                # move largest army card
                if self.largest_army_player:
                    self.largest_army_player.largest_army = 0
                self.largest_army_player = player
                player.largest_army = 2

    def allocate_resources(self, die_roll, players):
        '''
        given a die roll, gives the resources to the appropriate players
        if the die roll is 7, instead, all players with more than 7 resources will discard half of their
        total resources, rounded down
        '''
        if die_roll in self.r_allocator:
            vals = self.r_allocator[die_roll]
            for player, resource, loc in vals:
                if self.robber != loc:
                    self.give_resource(resource, player)
        if die_roll == 7:
            for player in players:
                total_resources = sum(player.resources[r] for r in self.resource_list)

                if total_resources >= 8:
                    discard = total_resources // 2
                    for _ in range(discard):
                        self.discard_random(player)

        # In debug mode, print the resources that each player now has
        if settings.DEBUG:
            for player in self.players:
                print("Player {} has resources:".format(player.player_num))
                for r in self.resource_list:
                    print('    {}: {}'.format(r, player.resources[r]))

    def give_resource(self, resource, player):
        '''
        helper function to give a resource to a player
        '''
        if resource in player.resources:
            player.resources[resource] += 1
        else:
            player.resources[resource] = 1

    def build_road(self, loc1, loc2, player):
        '''
        builds a road from loc1 to loc2 (assuming they are adjacent)
        '''
        self.coords[loc1].roads[loc2] = player
        self.coords[loc2].roads[loc1] = player
        self.coords[loc1].available_roads.remove(loc2)
        self.coords[loc2].available_roads.remove(loc1)

        longest_road = self.longest_road({(loc1, loc2)}, loc1, loc2, player, 1)
        if longest_road > self.longest_road_size:
            self.longest_road_size = longest_road

            if self.longest_road_player is not None:
                self.longest_road_player.longest_road = 0
            self.longest_road_player = player
            player.longest_road = 2

    def longest_road(self, visited, current1, current2, player, length):
        '''
        helper function for finding longest road
        '''
        longest = length

        for neighbour in self.coords[current1].neighbours:
            if self.coords[current1].roads[neighbour] == player \
                    and (current1, neighbour) not in visited \
                    and (neighbour, current1) not in visited:
                new_visited = visited | {(current1, neighbour)}
                new_longest = self.longest_road(new_visited, neighbour, current2, player, length + 1)
                longest = max(longest, new_longest)

        for neighbour in self.coords[current2].neighbours:
            if self.coords[current2].roads[neighbour] == player \
                    and (current2, neighbour) not in visited \
                    and (neighbour, current2) not in visited:
                new_visited = visited | {(current2, neighbour)}
                new_longest = self.longest_road(new_visited, neighbour, current2, player, length + 1)
                longest = max(longest, new_longest)

        return longest

    def add_settlement(self, player, loc):
        '''
        adds a settlement at a given coordinate
        '''
        assert(self.coords[loc].player == None)
        self.coords[loc].player = player
        resources = self.coords[loc].resource_locs
        for hex_loc in resources:
            vals = self.resources[hex_loc]
            die_val = vals[1]
            ret_resource = vals[0]

            if die_val in self.r_allocator:
                self.r_allocator[die_val].append((player, ret_resource, hex_loc))
            else:
                self.r_allocator[die_val] = [(player, ret_resource, hex_loc)]

            if hex_loc in self.adjacent:
                if player not in self.adjacent[hex_loc]:
                    self.adjacent[hex_loc].append(player)
            else:
                self.adjacent[hex_loc] = [player]

    def upgrade_settlement(self, player, loc):
        '''
        upgrades a settlement to a city
        '''
        assert(self.coords[loc].player.player_num == player.player_num)
        assert(self.coords[loc].settlement)
        self.coords[loc].settlement = False
        resources = self.coords[loc].resource_locs
        for loc in resources:
            vals = self.resources[loc]
            die_val = vals[1]
            ret_resource = vals[0]
            if die_val in self.r_allocator:
                self.r_allocator[die_val].append((player, ret_resource, loc))
            else:
                self.r_allocator[die_val] = [(player, ret_resource, loc)]

    def update_board(self, player, move):
        '''
        updates the board with the given move
        '''
        # End turn
        if move.move_type == Move.END_TURN:
            current_player_num = player.player_num
            next_player_index = current_player_num % len(self.players)
            self.active_player = self.players[next_player_index]
            return 0

        elif move.move_type == Move.ROLL_DICE:
          self.allocate_resources(move.roll, self.players)

        # Build a road
        elif move.move_type == Move.BUY_ROAD:
            road_coords = list(move.road)
            self.build_road(road_coords[0], road_coords[1], player)

        # Build a settlement
        elif move.move_type == Move.BUY_SETTLEMENT:
            self.add_settlement(player, move.coord)

        # Build a city
        elif move.move_type == Move.BUY_CITY:
            self.upgrade_settlement(player, move.coord)

        # Play a dev card
        elif move.move_type == Move.PLAY_DEV:
            if move.card_type == Card.KNIGHT:
                self.move_robber(move.coord, knight=True, player=player)
                if move.player:
                    self.steal_from(move.player, player)
            elif move.card_type == Card.ROAD_BUILDING:
                if move.road != None:
                    road_coords = list(move.road)
                    self.build_road(road_coords[0], road_coords[1], player)
                if move.road2 != None:
                    road_coords = list(move.road2)
                    self.build_road(road_coords[0], road_coords[1], player)
            elif move.card_type == Card.MONOPOLY:
                total = 0
                for p in self.players:
                    count = p.resources[move.resource]
                    total += count
                    p.resources[move.resource] = 0
                player.resources[move.resource] = total

        # Move robber
        elif move.move_type == Move.MOVE_ROBBER:
            self.move_robber(move.coord)
            if move.player:
                self.steal_from(move.player, player)

        # Propose trade
        elif move.move_type == Move.PROPOSE_TRADE:
            self.traders = []
            self.pending_trade = move
            self.trade_step = 1

        elif move.move_type == Move.ASK_TRADE or move.move_type == Move.ACCEPT_TRADE or move.move_type == Move.DECLINE_TRADE:
            self.trade_step += 1
            if move.move_type == Move.ACCEPT_TRADE:
                if player not in self.traders:
                    self.traders.append(player)

        elif move.move_type == Move.CHOOSE_TRADER:
            self.pending_trade = False
            self.trade_step = 0