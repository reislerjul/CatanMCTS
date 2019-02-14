from utils import Card
import settings
from utils import Move
import pickle

# This function converts a current board state to a matrix representation of its features
def board_to_vector(board, deck):
    board_vect = []

    # Note that we want a canonical representation. Thus, the active player will become 
    # "player 1", and the other players will be represented as subsequent numbers depending on 
    # the order of play.
    canonical_player = []
    start = board.players[board.active_player.player_num - 1]
    while start not in canonical_player:
        canonical_player.append(start)
        start = board.players[start.player_num % len(board.players)]

    # First, encode the dice values, dots, and resource at each hex. The dice 
    # values and the resource will be one hot encoded
    for i in range(len(settings.hexes)):
        hex_coord = settings.hexes[i]
        resource = board.resources[hex_coord][0]
        roll = board.resources[hex_coord][1]
        dots = board.resources[hex_coord][2]
        # resources
        for j in range(len(settings.resources)):
            board_vect.append(int(resource == settings.resources[j]))
        #dice values
        for j in range(2, 13):
            board_vect.append(int(roll == j))
        # dots
        board_vect.append(dots)
        # robber location
        board_vect.append(int(hex_coord == board.robber))

    # Now, for each vertex, we will encode the port
    for i in range(len(settings.vertices)):
        coord = board.coords[settings.vertices[i]]
        port = list(coord.ports)[0] if len(list(coord.ports)) > 0 else ""
        # ports
        for j in range(len(settings.ports)):
            board_vect.append(int(port == settings.ports[j]))

    # largest army, longest road, people who accepted the trade, seven roller.
    # Also, information for each player. For self, the neural net can know all 
    # the information. Otherwise, it should only know the amount of resources, 
    # amount of dev cards, and which dev cards have been played by other players.
    # We will also use this loop to do the roads
    board_vect.append(board.largest_army_size)
    board_vect.append(board.longest_road_size)

    for i in range(len(canonical_player)):
        player = canonical_player[i]
        board_vect.append(int(player == board.largest_army_player))
        board_vect.append(int(player == board.longest_road_player))
        board_vect.append(int(player == board.seven_roller))
        board_vect.append(player.num_knights_played)
        board_vect.append(player.total_roads)
        board_vect.append(player.num_yop_played)
        board_vect.append(player.num_monopoly_played)
        board_vect.append(player.num_road_builder_played)
        board_vect.append(player.devs_bought)

        # roads
        for j in range(len(settings.roads)):
            road = settings.roads[j]
            board_vect.append(int(road[0] in player.roads and road[1] in player.roads[road[0]]))
        # settlements/cities
        for j in range(len(settings.vertices)):
            coord = board.coords[settings.vertices[j]]
            if player == coord.player and not coord.settlement:
                board_vect.append(2)
            else:
                board_vect.append(int(player == coord.player))
        if i > 0:
            board_vect.append(int(player in board.traders))
            board_vect.append(sum(player.resources.values()))
            board_vect.append(sum(player.dev_cards.values()))
        else:
            # which resources the current player has
            for j in range(len(settings.resources)):
                resource = settings.resources[j]
                board_vect.append(player.resources[resource])
            # which dev cards the current player has
            for j in range(0, 5):
                board_vect.append(player.dev_cards[j])
                board_vect.append(player.dev_drawn == j)
            board_vect.append(player.has_rolled)
            board_vect.append(player.move_robber)
            board_vect.append(player.dev_played)
            board_vect.append(player.trades_tried)  

    # round number
    board_vect.append(board.round_num)

    # pending trade
    board_vect.append(int(bool(board.pending_trade)))

    # deck 
    board_vect.append(len(deck.cards_left))

    return board_vect




