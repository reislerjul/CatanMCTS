from utils import Card
import settings
from utils import Move
import random
import numpy as np

def action_to_move(index, move_array, current_player, total_players, deck):
    move = move_array[index].copy_move()
    if move.move_type == move.BUY_DEV:
        move.card_type = deck.peek()
        move.player = current_player.player_num
    elif ((move.card_type == Card.KNIGHT and move.move_type == move.PLAY_DEV) \
                or move.move_type == move.MOVE_ROBBER or \
                move.move_type == move.CHOOSE_TRADER) and move.player != None:
        victim = current_player.player_num + move.player - 1 \
        if current_player.player_num + move.player - 1 <= total_players \
        else (current_player.player_num + move.player - 1) % total_players
        move.player = victim
    elif move.move_type == Move.PROPOSE_TRADE:
        move.player = current_player.player_num
    elif move.move_type == Move.ROLL_DICE:
        move.roll = random.randint(1, 6) + random.randint(1, 6)
        move.player = current_player.player_num
    elif move.move_type == Move.DISCARD_HALF:
        resource_list = current_player.resources['w'] * ['w'] + current_player.resources['o'] * ['o'] + \
        current_player.resources['l'] * ['l'] + current_player.resources['b'] * ['b'] + \
        current_player.resources['g'] * ['g']
        total_resources = len(resource_list)
        discard = total_resources // 2
        combo = ()
        for i in range(discard):
            res = resource_list.pop(random.randint(0, len(resource_list) - 1))
            combo = combo + tuple(res)
        move.resource = combo
    return move

def action_to_index(move, current_player_num, total_players, move_to_index):
    try:
        if ((move.card_type == Card.KNIGHT and move.move_type == move.PLAY_DEV) \
            or move.move_type == move.MOVE_ROBBER or \
            move.move_type == move.CHOOSE_TRADER) and move.player != None:
            victim = move.player - current_player_num + 1 if move.player - current_player_num > 0 \
            else total_players - current_player_num + move.player + 1
            return move_to_index[Move(move.move_type, card_type=move.card_type, \
                coord=move.coord, player=victim)]
        if move in move_to_index:
            return move_to_index[move]
        if move.move_type == move.BUY_DEV:
            return move_to_index[Move(Move.BUY_DEV)]
        if move.card_type == Card.ROAD_BUILDING:
            return move_to_index[Move(move.move_type, card_type=move.card_type, \
                road=move.road2, road2=move.road)]
        if move.move_type == Move.PROPOSE_TRADE:
            return move_to_index[Move(move.move_type, give_resource=move.give_resource, \
                resource=move.resource)]
        if move.move_type == Move.ROLL_DICE:
            return move_to_index[Move(move.move_type)]
        if move.move_type == Move.DISCARD_HALF:
            return move_to_index[Move(move.move_type)]
        elif move.card_type == Card.YEAR_OF_PLENTY:
            return move_to_index[Move(move.move_type, card_type=move.card_type, \
                resource=move.resource2, resource2=move.resource)]
        else:
            print("Cannot find index for this move: ")
            print(move)
            raise(Exception("move not in all possible move array!"))    
    except:
        print("Cannot find index for this move; key exception")
        print(move)
        raise(Exception("move not in all possible move array!"))           

# Legal moves should be a list of legal moves that the player can make
def possible_actions_to_vector(legal_moves, current_player_num, total_players, move_to_index):
    # There are 3151 moves in Catan
    legal_vect = np.zeros(3151)
    
    # Go through each move in legal moves and find its corresponding index. Note that 
    # some of the moves might not be exactly the same as what's stored in the dictionary.
    # In these cases, we will reconstruct the right moves.
    for move in legal_moves:
        set_value_in_action_vector(legal_vect, current_player_num, total_players, \
            move_to_index, move, 1)
    return legal_vect

def set_value_in_action_vector(action_vector, current_player_num, \
    total_players, move_to_index, move, value):
    if ((move.card_type == Card.KNIGHT and move.move_type == move.PLAY_DEV) \
        or move.move_type == move.MOVE_ROBBER or \
        move.move_type == move.CHOOSE_TRADER) and move.player != None:
        victim = move.player - current_player_num + 1 if move.player - current_player_num > 0 \
        else total_players - current_player_num + move.player + 1
        action_vector[move_to_index[Move(move.move_type, card_type=move.card_type, \
            coord=move.coord, player=victim)]] = value        
    elif move in move_to_index:
        action_vector[move_to_index[move]] = value
    elif move.move_type == move.BUY_DEV:
        action_vector[move_to_index[Move(Move.BUY_DEV)]] = value
    elif move.card_type == Card.ROAD_BUILDING:
        action_vector[move_to_index[Move(move.move_type, card_type=move.card_type, \
            road=move.road2, road2=move.road)]] = value
    elif move.move_type == Move.PROPOSE_TRADE:
        action_vector[move_to_index[Move(move.move_type, give_resource=move.give_resource, \
            resource=move.resource)]] = value
    elif move.move_type == Move.ROLL_DICE:
        action_vector[move_to_index[Move(move.move_type)]] = value
    elif move.move_type == Move.DISCARD_HALF:
        action_vector[move_to_index[Move(move.move_type)]] = value
    elif move.card_type == Card.YEAR_OF_PLENTY:
        action_vector[move_to_index[Move(move.move_type, card_type=move.card_type, \
            resource=move.resource2, resource2=move.resource)]] = value
    else:
        print("Cannot find index for this move: ")
        print(move)
        raise(Exception("move not in all possible move array!"))


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

    return np.asarray(board_vect)




