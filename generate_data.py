import play as pl
#from numpy import random
import random
from collections import defaultdict
import dill as pickle
from sklearn.neural_network import MLPRegressor
import sys
import numpy as np

success_results =  defaultdict(lambda: [0, 0])

mlp_file = 'mlp_5.pkl'
with open(mlp_file, 'rb') as f:
    neural_net = pickle.load(f)


def simulate():
    '''Run number_of_games search trees'''
    number_of_games = int(input("How many games to simulate?: "))

    global success_results
    moves_played = 0

    training_file = 'training_data_2.pkl'

    try:
        print("Opening the file...")
        with open(training_file, 'rb') as f:
            success_results = pickle.load(f)
    except:
        pass

    print("Data loaded - starting the training")
    for i in range(number_of_games):
        if i % 1000 == 0:
            print(i)
        p1 = pl.player([1,2,3,4,6,11,16], 1, 'x', 0)
        p2 = pl.player([10,15,20,22,23,24,25], -1, 'y', 0)
        gameboard = pl.board(p1.get_positions(), p2.get_positions())
        winner, game_states_involved = random_tree(gameboard, p1, p2, [])
        moves_played += len(game_states_involved)
        for state in game_states_involved:
            #Add 1 for every state if P1 won
            #Add 1 to the number of games played
            success_results[state][0] += winner
            success_results[state][1] += 1
            #print(state, success_results[state])

    print("Storing the file....")
    with open(training_file, 'wb') as f:
        pickle.dump(success_results, f)
    print(moves_played, len(success_results))
        
        

def encode(board, turns_taken):
    '''Create the 42-length array to represent the board as a node'''
    #First 41 are the board state, last is the number of turns taken so far
    encoding = [0]*42
    for i in range(1,42):
        encoding[i - 1] = board.positions[i]
    encoding[-1] = turns_taken
    return encoding

def create_next_moves(current_board, turn_number, option):
    '''Create all of the next possible board states'''
    board_encoding = encode(current_board,turn_number)
    move_from, move_to = option[0], option[1]
    
    player_number = turn_number % 2
    if player_number == 0:
        player_number = 2

    board_encoding[move_from - 1] = 0
    board_encoding[move_to - 1] = player_number
    return board_encoding

def find_best_move(current_board, turn_number, options):
    '''Use the neural net to find the best option'''

    #Encode all of the next possible states
    encodings = [create_next_moves(current_board,turn_number, option) for option in options]

    global neural_net
    #Use the neural net to assess these next states
    evals = neural_net.predict(encodings)
    
    #Flip the probabilities for P2 - take their best option (worst for P1)
    if turn_number % 2 == 0:
        evals = list(map(lambda x: 1 - x, evals))

    #Set the value to be very small if the ultimate weight is negative    
    evals = [max(eval_value, 0.00000001) for eval_value in evals]
    
    total_eval_values = sum(evals)
    weighted_evals = list(map(lambda x: x/total_eval_values, evals))

    for i in range(len(evals)):
        print(evals[i], weighted_evals[i], options[i])
    if turn_number == 2:
        sys.exit(0)
    
    #Can't randomly choose from non 1D array, so randomly choosing index for the options list instead (numpy.random allows random)
    try:
        random_move = np.random.choice(range(len(weighted_evals)), p=weighted_evals)
    except:
        print(weighted_evals)
    move_from = options[random_move][0]
    move_to = options[random_move][1]
    #print(random_move)
    #print(move_from, move_to)

    #print(move_from, move_to, evals[random_move], turn_number)
    return move_from, move_to

def random_tree(board, active_player, other_player, past_states):
    '''Choose a random move from this position'''

    
    current_locations = active_player.get_positions()
    current_order = active_player.get_order()

    turn_number = len(past_states) + 1
    options = []
    for token in current_locations:
        moves =  pl.get_legal_moves(token, board)
        for move_to in moves:
            options.append((token, move_to))
        captures = pl.get_legal_captures(token, board, current_order)
        for capture_on in captures:
            options.append((token, capture_on))

    move_technique = "RANDOM"
    if move_technique == "RANDOM":
        random_move = random.choice(options)
        move_from = random_move[0]
        move_to = random_move[1]
    else:
        move_from, move_to = find_best_move(board, turn_number, options)


    active_player.move_token(move_from, move_to)
    occupant_of_target = board.get_occupant_of_position(move_to)
    if occupant_of_target not in (0, active_player.get_order()):
        other_player.lose_token(move_to)
    board.change_state(move_from, 0)
    board.change_state(move_to, active_player.get_order())

    encoded_state = tuple(encode(board, turn_number))
    past_states.append(encoded_state)
    #Add in the state to the final grid
    #print(len(past_states) + 1)
    #print(move_from, move_to)

    #Check if the game is over
    #Either there are 4 or fewer tokens in the encoding, or turn count as ellapsed
    if encoded_state[:-1].count(-1) <= 3:
        return 1, past_states
    elif encoded_state[:-1].count(1) <= 3:
        return 0, past_states
    elif encoded_state[-1] == 200:
        p1_lives = encoded_state[:-1].count(1)
        p2_lives = encoded_state[:-1].count(-1)
        return p1_lives > p2_lives, past_states

    #Not over, - make another move
    
    return random_tree(board, other_player, active_player, past_states)

if __name__ == "__main__":
    simulate()
