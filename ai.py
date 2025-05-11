import random
import printing as pr
import numpy as np
from collections import defaultdict
from copy import deepcopy
import play as pl
import dill as pickle
from sklearn.neural_network import MLPRegressor

NN = None

def encode(board, turns_taken):
    '''Create the 42-length array to represent the board as a node'''
    #Copied from generate_data.py, used here to encode the board for the net
    #First 41 are the board state, last is the number of turns taken so far
    encoding = [0]*42
    for i in range(1,42):
        encoding[i - 1] = board.positions[i]
    encoding[-1] = turns_taken
    return encoding

def bogo(moves, captures, name):
    '''Starting AI - pick a move at random'''
    #pr.ai_thought(name)
    options = []
    for move_from in moves:
        for move_to in moves[move_from]:
            options.append((move_from, move_to))
    for move_from in captures:
        for move_to in captures[move_from]:
            options.append((move_from, move_to))

    #print(len(options))
    random_move = random.choice(options)
    move_from = random_move[0]
    move_to = random_move[1]
    #pr.ai_decision(name, move_to, move_from, moves)
    return random_move

def life_heuristic(p1, p2):
    '''Return the difference in lives. If someone's dead, maximize the value'''
    if not p1.is_alive():
        return -7
    elif not p2.is_alive():
        return 7
    else:
        return p1.get_life_count() - p2.get_life_count()

def dfs(depth, board, active_player, other_player):
    '''Run a DFS with Minimax to calculate a move'''
    current_locations = active_player.get_positions()
    current_order = active_player.get_order()

    moves  = {}
    captures = {}

    for token in current_locations:
        moves[token] =  pl.get_legal_moves(token, board)
        captures[token] = pl.get_legal_captures(token, board, current_order)

    options = []
    for move_from in moves:
        for move_to in moves[move_from]:
            options.append((move_from, move_to))
    for move_from in captures:
        for move_to in captures[move_from]:
            options.append((move_from, move_to))


    best_moves = []
    best_value = -10

    for option in options:
        test_board = deepcopy(board)
        test_active_player = deepcopy(active_player)
        test_other_player = deepcopy(other_player)
        move_from = int(option[0])
        move_to = int(option[1])

        test_active_player.move_token(move_from, move_to)
        occupant_of_target = test_board.get_occupant_of_position(move_to)
        if occupant_of_target not in (0, current_order):
            test_other_player.lose_token(move_to)
            if not test_other_player.is_alive():
                return option[0], option[1], 7 + depth
        test_board.change_state(move_from, 0)
        test_board.change_state(move_to, current_order)

        if depth == 0:
            value = life_heuristic(test_active_player, test_other_player)


        else:
            #returned value is opponent's best move
            move_from, move_to, value = dfs(depth - 1, test_board, test_other_player, test_active_player)
            value *= -1

        if value > best_value:
            best_value = value
            best_moves = [option]
        elif value == best_value:
            best_moves.append(option)
        del test_board
        del test_active_player
        del test_other_player

    if depth == 3:
        print(best_value)
    best_move = random.choice(best_moves)
    final_move_from, final_move_to = best_move[0], best_move[1]
    return final_move_from, final_move_to, best_value


def nn(depth, board, active_player, other_player, turn_number):
    '''Use the neural net with Minimax to calculate a move'''

    #Upload the net if not yet done
    global NN
    #Load up the Neural Net if needed
    if NN == None:
        mlp_file = 'mlp_5.pkl'
        with open(mlp_file, 'rb') as f:
            NN = pickle.load(f)

    current_locations = active_player.get_positions()
    current_order = active_player.get_order()

    moves  = {}
    captures = {}

    for token in current_locations:
        moves[token] =  pl.get_legal_moves(token, board)
        captures[token] = pl.get_legal_captures(token, board, current_order)

    options = []
    for move_from in moves:
        for move_to in moves[move_from]:
            options.append((move_from, move_to))
    for move_from in captures:
        for move_to in captures[move_from]:
            options.append((move_from, move_to))

    best_moves = []
    best_value = -10

    for option in options:
        test_board = deepcopy(board)
        test_active_player = deepcopy(active_player)
        test_other_player = deepcopy(other_player)
        move_from = int(option[0])
        move_to = int(option[1])

        test_active_player.move_token(move_from, move_to)
        occupant_of_target = test_board.get_occupant_of_position(move_to)
        if occupant_of_target not in (0, current_order):
            test_other_player.lose_token(move_to)
            #Commented out - ignoring rules to determine end of game
            #if not test_other_player.is_alive():
            #    return option[0], option[1], 7 + depth
        test_board.change_state(move_from, 0)
        test_board.change_state(move_to, current_order)

        if depth == 0:
            board_encoding = encode(test_board,turn_number)
            value = NN.predict([board_encoding])

        else:
            #returned value is opponent's best move
            move_from, move_to, value = nn(depth - 1, test_board, test_other_player, test_active_player, turn_number + 1)
            value = 1 - value

        if value > best_value:
            best_value = value
            best_moves = [option]
        elif value == best_value:
            best_moves.append(option)
        del test_board
        del test_active_player
        del test_other_player

    best_move = random.choice(best_moves)
    final_move_from, final_move_to = best_move[0], best_move[1]
    return final_move_from, final_move_to, best_value
