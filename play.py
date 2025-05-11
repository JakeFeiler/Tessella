import board_qualities as bq
import printing as pr
import sys
import ai
from collections import defaultdict
from copy import deepcopy
import generate_data
import dill as pickle
from sklearn.neural_network import MLPRegressor

P1_WINS = 0
P2_WINS = 0

class player:
    '''The player of the game, with information about where all their tokens are located'''
    def __init__(self, positions, order, name, difficulty):
        self.positions = positions
        self.order = order
        self.name = name
        self.difficulty = difficulty
        if name in ("Tess", "Ella"):
            self.is_bot = True
        else:
            self.is_bot = False

    def get_name(self):
        '''get the name'''
        return self.name

    def get_difficulty(self):
        '''get the diffculty (0=human, 1=easy, 2=medium, 3=hard)'''
        return self.difficulty

    def get_order(self):
        '''return the order (marker) for this player'''
        return self.order

    def get_life_count(self):
        '''Determine how many lives remain for this player'''
        return len(self.positions)

    def is_alive(self):
        '''Determine if the game is losst'''
        return self.get_life_count() > 3

    def get_positions(self):
        '''Find where all tokens are currently placed'''
        return self.positions

    def move_token(self, old_position, new_position):
        '''Move a token to a new position'''
        for i in range(len(self.positions)):
            if self.positions[i] == old_position:
                self.positions[i] = new_position
                return True

    def lose_token(self, captured_position):
        '''A token is captured, remove it from tracked tokens'''
        self.positions.remove(captured_position)

    def take_turn(self, gameboard, other_player, turn_count):
        '''Go through the process of making 1 move'''
        difficulty = self.get_difficulty()
        name = self.get_name()

        #Get all possible MOVES (not captures) for all tokens
        possible_moves = {}
        possible_captures = {}
        for token in self.positions:
            possible_moves[token] = get_legal_moves(token, gameboard)
            possible_captures[token] = get_legal_captures(token, gameboard, self.order)

        #pr.print_current_board_state(gameboard)

        if difficulty == '0':
            move_is_not_finished = True
            while move_is_not_finished:
                move_from = pr.ask_for_input(gameboard, self.order, self.name, turn_count, possible_moves, possible_captures)
                #Start again with a different move
                if move_from == '0':
                    continue

                move_to = pr.ask_for_input(gameboard, self.order, self.name, turn_count, possible_moves, possible_captures, move_from)
                if move_to == '0':
                    continue
                else:
                    move_is_not_finished = False
            move_from = int(move_from)
            move_to = int(move_to)

        elif difficulty == '1':
            random_choice = ai.bogo(possible_moves, possible_captures, self.name)
            move_from = random_choice[0]
            move_to = random_choice[1]

        elif difficulty == '2':
            move_from, move_to, planned_value = ai.dfs(1, deepcopy(gameboard), deepcopy(self), deepcopy(other_player))
            #pr.ai_decision(name, move_to, move_from, possible_moves)

        elif difficulty == '3':
            move_from, move_to, planned_value = ai.dfs(3, deepcopy(gameboard), deepcopy(self), deepcopy(other_player))
            #pr.ai_decision(name, move_to, move_from, possible_moves)

        elif difficulty == '4':
            move_from, move_to, planned_value = ai.nn(1, deepcopy(gameboard), deepcopy(self), deepcopy(other_player), turn_count)
            print(move_from, move_to, planned_value)
            #pr.ai_decision(name, move_to, move_from, possible_moves)
            pass



        #Valid move to and from are passed, update status everywhere
        self.move_token(move_from, move_to)
        occupant_of_target = gameboard.get_occupant_of_position(move_to)
        if occupant_of_target not in (0, self.order):
            other_player.lose_token(move_to)
        gameboard.change_state(move_from, 0)
        gameboard.change_state(move_to, self.order)
        return True






class board:
    '''The game board, which contains information on what every place is populated by'''
    def __init__(self, p1_places, p2_places):
        #0 = unoccupied, 1 = p1, 2 = p2
        self.positions = {}
        for i in range(1, 42):
            self.positions[i] = 0
        for token_1 in p1_places:
            self.positions[token_1] = 1
        for token_2 in p2_places:
            self.positions[token_2] = -1

    def change_state(self, position, new_value):
        '''Set the occupant of this position to new_value'''
        self.positions[position] = new_value

    def get_occupant_of_position(self, position):
        '''Get the player in this position'''
        return self.positions[position]



def get_legal_moves(position, board_state):
    '''Get all legal MOVES from a position (must be unoccupied)'''
    final_moves = []
    possible_moves = bq.legal_moves[position]
    #Look at all adjacent squares, see which are unoccupied
    for destination in possible_moves:
        if board_state.get_occupant_of_position(destination) == 0:
            final_moves.append(destination)
    return final_moves

def get_legal_captures(position, board_state, turn):
    '''Get all legal CAPUTRES from a position'''
    final_captures = []

    #Get the 3/4 rows this spot is in
    shared_rows = bq.positions_to_paths[position]
    for row in shared_rows:
        spots_in_row = bq.attack_paths[row]
        index_in_row = spots_in_row.index(position)
        i = index_in_row - 1
        closest_player_going_down = 0
        closest_player_going_down_position = 0
        #going down in the row, look for the next token
        while i >= 0 and closest_player_going_down == 0:
            board_label = spots_in_row[i]
            occupant = board_state.get_occupant_of_position(board_label)
            if occupant == 0:
                pass
            elif occupant == 1:
                closest_player_going_down = 1
                closest_player_going_down_position = board_label
            elif occupant == -1:
                closest_player_going_down = -1
                closest_player_going_down_position = board_label
            i -= 1

        #skip to next row, there was nothing in this direction
        if closest_player_going_down == 0:
            continue

        i = index_in_row + 1
        closest_player_going_up = 0
        closest_player_going_up_position = 0
        while i < len(spots_in_row) and closest_player_going_up == 0:
            board_label = spots_in_row[i]
            occupant = board_state.get_occupant_of_position(board_label)
            if occupant == 0:
                pass
            elif occupant == 1:
                closest_player_going_up = 1
                closest_player_going_up_position = board_label
            elif occupant == -1:
                closest_player_going_up = -1
                closest_player_going_up_position = board_label
            i += 1

        #skip to next row, there was nothing in this direction
        if closest_player_going_up == 0:
            continue

        #Skip to next row, same token on either side
        if closest_player_going_up == closest_player_going_down:
            continue

        #Otherwise, capture is avaialble
        #Friend is down, foe is up
        if closest_player_going_down == turn:
            capturable_square = closest_player_going_up_position
        #Friend is up, foe is down
        else:
            capturable_square = closest_player_going_down_position
        final_captures.append(capturable_square)
    return final_captures


def create_game(player_1_name='', player_2_name='', player_1_difficulty='', player_2_difficulty='', game_count=''):
    '''Initialize the starting positions of the players, set up the board'''
    if game_count == '':
        player_1_name, player_2_name, player_1_difficulty, player_2_difficulty, game_count = pr.introduction()
    p1 = player([1,2,3,4,6,11,16], 1, player_1_name, player_1_difficulty)
    p2 = player([10,15,20,22,23,24,25], -1, player_2_name, player_2_difficulty)
    gameboard = board(p1.get_positions(), p2.get_positions())
    return p1, p2, gameboard, int(game_count)


def play_game():
    '''Run the game of Tessella'''
    global P1_WINS, P2_WINS
    #how_many_turns = defaultdict(int)

    p1, p2, gameboard, number_of_games = create_game()
    p1_fixed_name = p1.get_name()
    p2_fixed_name = p2.get_name()
    p1_fixed_difficulty = p1.get_difficulty()
    p2_fixed_difficulty = p2.get_difficulty()

    current_game_number = 1
    while current_game_number <= number_of_games:
        if current_game_number % 2 == 1:
            p1, p2, gameboard, number_of_games = create_game(p1_fixed_name, p2_fixed_name, p1_fixed_difficulty, p2_fixed_difficulty, number_of_games)
        else:
            p1, p2, gameboard, number_of_games = create_game(p2_fixed_name, p1_fixed_name, p2_fixed_difficulty, p1_fixed_difficulty, number_of_games)


        print("Playing game number " + str(current_game_number))
        it_is_player_ones_turn = True
        turn_count = 1

        #p1_is_bot = False
        #p2_is_bot = False

        while p1.is_alive() and p2.is_alive() and turn_count < 200:
            turn_count += 1
            if it_is_player_ones_turn:
                p1.take_turn(gameboard, p2, turn_count)
                it_is_player_ones_turn = False
            else:
                p2.take_turn(gameboard, p1, turn_count)
                it_is_player_ones_turn = True

        #pr.print_current_board_state(gameboard)

        #how_many_turns[turn_count] += 1
        if not p2.is_alive():
            if current_game_number % 2 == 1:
                P1_WINS += 1
            else:
                P2_WINS += 1
            print(p1.get_name() + " wins in " + str(turn_count) + " turns!")
        elif not p1.is_alive():
            if current_game_number % 2 == 1:
                P2_WINS += 1
            else:
                P1_WINS += 1
            print(p2.get_name() + " wins in " + str(turn_count) + " turns!")
        else:
            #tiebreaker is the number of lives remaining
            p1_lives = p1.get_life_count()
            p2_lives = p2.get_life_count()
            if p1_lives > p2_lives:
                if current_game_number % 2 == 1:
                    P1_WINS += 1
                else:
                    P2_WINS += 1
                print(p1.get_name() + " wins in tiebreaker, with " + str(p1_lives) + " lives to " + str(p2_lives) + "!")
            elif p1_lives < p2_lives:
                if current_game_number % 2 == 1:
                    P2_WINS += 1
                else:
                    P1_WINS += 1
                print(p2.get_name() + " wins in tiebreaker, with " + str(p2_lives) + " lives to " + str(p1_lives) + "!")
            else:
                P2_WINS += 1
                print(p2.get_name() + " wins! Both players have " + str(p1_lives) + " lives remaining at the end of the game!")
        print("Match score - " + p1_fixed_name + ": " + str(P1_WINS) + " " + p2_fixed_name + ": " + str(P2_WINS))

        current_game_number += 1

    print("Final match score - " + p1_fixed_name + ": " + str(P1_WINS) + " " + p2_fixed_name + ": " + str(P2_WINS))
    if P1_WINS > P2_WINS:
        print(p1_fixed_name + " is the grand champion!")
    elif P1_WINS < P2_WINS:
        print(p2_fixed_name + " is the grand champion!")
    else:
        print("You both did semi-good!")

    """
    how_many_turns = dict(sorted(how_many_turns.items()))
    print("Here are all the turns:\n")
    longer_than_100 = 0
    for x in how_many_turns:
        print(x, how_many_turns[x])
        if x >= 100:
            longer_than_100 += how_many_turns[x]
    print("All games longer than <limit>: " + str(longer_than_100))
    """

if __name__ == "__main__":
    play_game()
