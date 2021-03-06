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

    def __init__(self, players, random_board, verbose=False):
        self.players = players
        self.robber = (2, 0)
        self.resources = self.init_resources(random_board)
        self.hex = self.init_hexes_from_resources()
        self.coords = self.init_coords(random_board)
        self.r_allocator = {}
        self.adjacent = {}
        self.largest_army_size = 2
        self.largest_army_player = None
        self.longest_road_size = 4
        self.longest_road_player = None
        self.resource_list = ['w', 'o', 'l', 'b', 'g']
        self.active_player = players[0]
        self.round_num = 0
        self.pending_trade = False
        self.traders = []
        self.longest_road_path = ()
        self.seven_roller = None
        self.verbose = verbose

    def init_coords(self, random_board):
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

        if not random_board:
            return coords
        ports = 4 * ['3'] + ['2 w'] + ['2 l'] + ['2 b'] + ['2 o'] + ['2 g']
        # Ports are always 2 or 3 roads away from other ports
        distances = 6 * [2] + 3 * [3]
        edge_vertices = []
        for coord in coords.keys():
            coords[coord].ports = set()
            if len(coords[coord].resource_locs) < 3:
                edge_vertices.append(coord)
        random.shuffle(distances)
        random.shuffle(ports)
        random.shuffle(edge_vertices)

        curr = edge_vertices.pop()
        dist = distances.pop()
        port = ports.pop()
        coords[curr].ports.add(port)
        while len(edge_vertices) > 0:
            # Find the neighbor that will also share the port
            for neighbour in coords[curr].neighbours:
                if neighbour in edge_vertices:
                    coords[neighbour].ports.add(port)
                    edge_vertices.remove(neighbour)
                    curr = neighbour
                    break 

            # Traverse until we've skipped over 2 or 3 spaces
            for i in range(dist):
                for neighbour in coords[curr].neighbours:
                    if neighbour in edge_vertices:
                        edge_vertices.remove(neighbour)
                        curr = neighbour
                        break

            # After traversing 2 or 3 spaces, we're at the next 
            # spot for a port! 
            if len(distances) > 0:
                dist = distances.pop()
                port = ports.pop()
                coords[curr].ports.add(port)
        assert(len(distances) == 0 and len(ports) == 0 and len(edge_vertices) == 0) 
        return coords

    def print_board_state(self):
        # Print the coordinates if there is a settlement or city there.
        board_items = self.coords.items()
        for coordinate in board_items:
            if coordinate[1].player:
                print("Coordinates: {}\n\n".format(coordinate))
        print("Robber location: {}".format(self.robber))

    def init_resources(self, random_board):
        '''
        this function initializes the nodes of resources in a list like faction
        a resource is given by a tuple with the first element being the resource
        the second element being the number on the die needed to roll that resource
        and the third element being the dots corresponding to the probability of the number rolling and
        this list of resources is a list of list with each location being a hexagonal thing on the map
        i.e. the top left corner https://www.catan.com/en/download/?SoC_rv_Rules_091907.pdf of
        this is a forestt with 11
        w = wool, b= brick, l = lumber, g= grain, o = ore n = none
        '''
        if not random_board:
            return {(0, 0): ('l', 11, 2), (0, 1): ('w', 12, 1), (0, 2): ('g', 9, 4),
                    (1, 0): ('b', 4, 3), (1, 1): ('o', 6, 5), (1, 2): ('b', 5, 4), 
                    (1, 3): ('w', 10, 3), (2, 0): ('n', -1, 0), (2, 1): ('l', 3, 2), 
                    (2, 2): ('g', 11, 2), (2, 3): ('l', 4, 3), (2, 4): ('g', 8, 5),
                    (3, 0): ('b', 8, 5), (3, 1): ('w', 10, 3), (3, 2): ('w', 9, 4), 
                    (3, 3): ('o', 3, 2), (4, 0): ('o', 5, 4), (4, 1): ('g', 2, 1), 
                    (4, 2): ('l', 6, 5)}
        else:
            return self.randomize_resources_helper()

    def randomize_resources_helper(self):
        resource_dict = {}
        spots = [(4, 1), (2, 1), (3, 3), (1, 0), (2, 3), (1, 2), (4, 0), \
                 (1, 1), (4, 2), (2, 4), (3, 0), (0, 2), (3, 2), (1, 3), \
                 (3, 1), (0, 0), (2, 2), (0, 1), (2, 0)]
        resources = ['w'] * 4 + ['g'] * 4 + ['l'] * 4 + ['o'] * 3 + ['b'] * 3 + ['n'] * 1
        rolls = [(2, 1)] + 2 * [(3, 2)] + 2 * [(4, 3)] + 2 * [(5, 4)] + \
        2 * [(6, 5)] + 2 * [(8, 5)] + 2 * [(9, 4)] + 2 * [(10, 3)] + 2 * [(11, 2)] + [(12, 1)]
        random.shuffle(spots)
        random.shuffle(resources)
        random.shuffle(rolls)
        while len(spots) > 0:
            spot = spots.pop()
            resource = resources.pop()
            if resource == 'n':
                roll = (-1, 0)
            else:
                roll = rolls.pop()
            resource_dict[spot] = tuple(resource) + roll
        assert(len(spots) == 0 and len(resources) == 0 and len(rolls) == 0)
        return resource_dict

    # Resources are always initialized first, so we can just use self.resources to initialize the 
    # hexes. Input to hexes is a die roll, output is a list of hex coordinates representing the locations
    def init_hexes_from_resources(self):
        hexes = {}
        for element in self.resources.items():
            hex_coord = element[0]
            dice_roll = element[1][1]
            if dice_roll != -1:
                if dice_roll not in hexes:
                    hexes[dice_roll] = [hex_coord]
                else:
                    hexes[dice_roll].append(hex_coord)
        hexes[7] = []
        return hexes

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
            resource = self.discard_random(self.players[victim_player - 1])

            # If the player doesn't have a resource, nothing should happen
            if resource:
                thief_player.resources[resource] += 1

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

    def allocate_resources(self, die_roll):
        '''
        given a die roll, gives the resources to the appropriate players
        if the die roll is 7, instead, all players with more than 7 resources will discard half of their
        total resources, rounded down
        '''
        if die_roll in self.r_allocator:
            vals = self.r_allocator[die_roll]
            for player, resource, loc in vals:
                if self.robber != loc:
                    player.resources[resource] += 1
        # In debug mode, print the resources that each player now has
        if settings.DEBUG:
            for player in self.players:
                print("Player {} has resources:".format(player.player_num))
                for r in self.resource_list:
                    print('    {}: {}'.format(r, player.resources[r]))

    def change_longest_road_owner(self, new_road, new_length, player, decreasing_size=False):
        if new_length > self.longest_road_size or decreasing_size:
            if self.longest_road_player != None:
                self.longest_road_player.longest_road = 0
            self.longest_road_player = player
            if player != None:
                player.longest_road = 2     
            self.longest_road_path = tuple(new_road)
            self.longest_road_size = new_length

    def build_road(self, loc1, loc2, player):
        '''
        builds a road from loc1 to loc2 (assuming they are adjacent)
        '''
        # When building a road, the only possibilities are that longest road stays 
        # the same or increases. We don't have to worry about someone losing their 
        # longest road. Before we do anything, we should check if loc2 is reachable 
        # from loc 1. If it is not, the longest path with a road through loc 1 and 2
        # is 1 + (longest path from loc 1) + (longest path from loc 2)
        longest_path_1, seen, reachable = self.longest_road_single_source(loc1, player)
        can_reach = False
        if loc2 not in reachable:
            # The return value of longest_road_single_source is a tuple of vertices along
            # the path. Thus, the road length is the length of the tuple - 1
            longest_path_2, seen2, reachable2 = self.longest_road_single_source(loc2, player)
            self.change_longest_road_owner(tuple(longest_path_1[::-1]) + tuple(longest_path_2), 
                len(longest_path_1) + len(longest_path_2) - 1, player)
        else:
            can_reach = True

        self.coords[loc1].roads[loc2] = player
        self.coords[loc2].roads[loc1] = player
        self.coords[loc1].available_roads.remove(loc2)
        self.coords[loc2].available_roads.remove(loc1)

        if can_reach:
            # Calculate the single source shortest path from every location in reachable. 
            # Adding the road from loc1 to loc2 does not change the reachable set.
            longest_road = 0
            longest_path = ()
            for coord in reachable:
                path, seen, reachable = self.longest_road_single_source(coord, player)
                if len(path) - 1 > longest_road:
                    longest_path = path
                    longest_road = len(path) - 1
            self.change_longest_road_owner(longest_path, longest_road, player)

    def longest_road_single_source(self, source, player):
        return self.DFS(source, player, tuple([source]))
 
    def DFS(self, v, player, longest_path=(), seen=None, reachable=None, path=None, start=True):
        if seen == None: 
            seen = set()
            reachable = set()
        if path == None: 
            path = [v]
        reachable.add(v)
        if start or (self.coords[v].player == None or self.coords[v].player == player):
            for t in self.coords[v].neighbours:
                if self.coords[v].roads[t] == player and frozenset([t, v]) not in seen:
                    t_path = path + [t]
                    if len(t_path) > len(longest_path):
                        longest_path = t_path
                    seen.add(frozenset([v, t]))
                    new_longest, new_seen, reach = self.DFS(t, player, longest_path, 
                        seen, reachable, t_path, False)
                    if len(new_longest) > len(longest_path):
                        longest_path = new_longest
        return longest_path, seen, reachable

    def check_longest_road_cutoff(self, player, loc):
        try:
            length = len(self.longest_road_path)
            if self.longest_road_player != None and self.longest_road_player != player:
                index = list(self.longest_road_path)[1:].index(loc)
                if index != length - 2:
                    # Longest road goes through this coordinate and the coordinate is not 
                    # an endpoint of the road. Unfortunately, we have to recalculate the 
                    # longest road by looking at all the players' roads
                    longest = 0
                    arg_max_person = 0
                    arg_max_road = ()
                    for person in self.players:
                        for vertex in person.roads.keys():
                            path, seen, reachable = self.longest_road_single_source(vertex, person)
                            if len(path) - 1 > longest:
                                longest = len(path) - 1
                                arg_max_person = person
                                arg_max_road = path
                    if longest > 4:
                        self.change_longest_road_owner(arg_max_road, longest, arg_max_person, True)
                    else:
                        self.change_longest_road_owner((), 4, None, True)
        except ValueError:
            return

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

        # Check to see if we're cutting off the longest road
        self.check_longest_road_cutoff(player, loc)

    def upgrade_settlement(self, player, loc):
        '''
        upgrades a to a city
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
            if self.round_num != 1:
                if player.player_num == len(self.players):
                    self.round_num += 1
                    if self.verbose:
                        print("*** CHANGE TO ROUND " + str(self.round_num) + " ***")
#                    else:
#                        print("*** CHANGE TO ROUND " + str(self.round_num) + " IN MCTS PLAYOUT ***")
                if self.round_num != 1:
                    self.active_player = self.players[player.player_num % len(self.players)]
            else:
                if player.player_num == 1:
                    self.round_num += 1
                    if self.verbose:
                        print("*** CHANGE TO ROUND " + str(self.round_num) + " ***")
#                    else:
#                        print("*** CHANGE TO ROUND " + str(self.round_num) + " IN MCTS PLAYOUT ***")
                else:
                    self.active_player = self.players[player.player_num - 2]
            self.active_player.avg_moves_round[0] += 1

            #if self.verbose:
            #    print("_____PLAYER " + str(self.active_player.player_num) + " TURN_____")
 #           else:
 #               print("_____PLAYER " + str(self.active_player.player_num) + " TURN IN MCTS PLAYOUT_____")
            if settings.DEBUG:
                print("_____PLAYER " + str(self.active_player.player_num) + " TURN_____")
                print("STATE OF BOARD BEFORE TURN")
                print("PLAYERS")
                for player in self.players:
                    print("Player {} has resources and devs:".format(player.player_num))
                    for r in self.resource_list:
                        print('    {}: {}'.format(r, player.resources[r]))
                    for dev in player.dev_cards.items():
                        print('    {}: {}'.format(dev[0], dev[1]))
                print("settlements: " + str(self.settlements))
                print("cities: " + str(self.cities))
                print("ports: " + str(self.ports))
                print("roads: " + str(self.roads))
                print("BOARD")
                print("robber: " + str(self.robber))
                if self.largest_army_player != None:
                    print("largest army player: " + str(self.largest_army_player.player_num))
                if self.longest_road_player != None:
                    print("longest road player: " + str(self.longest_road_player.player_num))
                for coord in self.coords.values():
                    if coord.player != None:
                        print("COORD")
                        print("location: " + str(coord.location))
                        print("settlement: " + str(coord.settlement))
                        print("player: " + str(coord.player.player_num))
                        print("roads: " + str(coord.roads))
                        print("available roads: " + str(coord.available_roads))
                        print("")

        elif move.move_type == Move.ROLL_DICE:
            self.allocate_resources(move.roll)
            if move.roll == 7:
                for person in self.players:
                    total_resources = sum(person.resources[r] for r in self.resource_list)
                    if total_resources >= 8:
                        #if self.verbose:
                        #    print("someone has more than 7 resources")
                        self.seven_roller = player
                        self.active_player = person
                        break

        elif move.move_type == Move.DISCARD_HALF:
            for i in range(player.player_num, len(self.players)):
                person = self.players[i]
                total_resources = sum(person.resources[r] for r in self.resource_list)
                if total_resources >= 8:
                    self.active_player = person
                    break
            # Everyone has discarded!
            if self.active_player == player:
                self.active_player = self.seven_roller
                self.seven_roller = None

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
            self.active_player = self.players[player.player_num % len(self.players)]

        elif move.move_type == Move.ACCEPT_TRADE or move.move_type == Move.DECLINE_TRADE:
            if move.move_type == Move.ACCEPT_TRADE and player not in self.traders:
                self.traders.append(player)
            self.active_player = self.players[player.player_num % len(self.players)]

        elif move.move_type == Move.CHOOSE_TRADER:
            self.pending_trade = False
            self.traders = []