import sys
import board_qualities as bq
import time

def introduction():
    print("Welcome to Tessella!")
    p1_name = input("Player 1, enter your name (leave blank for bot): ")
    p1_difficulty = '0'
    if p1_name == '':
        #bot_intro("Tess")
        p1_name = "Tess"
        p1_difficulty = input("Enter a difficulty for this bot (1=easy, 2=medium, 3=hard, 4=brutal): ")
        if p1_difficulty not in ('2', '3', '4'):
            p1_difficulty = '1'
    else:
        print("Welcome " + p1_name + "!")
    p2_name = input("Player 2, enter your name (leave blank for bot): ")
    p2_difficulty = '0'
    if p2_name == '':
        #bot_intro("Ella")
        p2_name = "Ella"
        p2_difficulty = input("Enter a difficulty for this bot (1=easy, 2=medium, 3=hard, 4=brutal): ")
        if p2_difficulty not in ('2', '3', '4'):
            p2_difficulty = '1'
    else:
        print("Welcome " + p2_name + "!")
    game_count = input("How many games would you like to play? ")
    print("\n\nFeel free to type '?' at any point for a list of all allowable inputs")
    time.sleep(1)
    print("Setting up board...")
    time.sleep(1)
    print("\n\n")

    return p1_name, p2_name, p1_difficulty, p2_difficulty, game_count

def bot_intro(name):
    print("Activating '" + name + "'...")
    time.sleep(.8)
    print("Generating self-awareness...")
    time.sleep(.8)
    print("Solving Riemann Hypothesis...")
    time.sleep(.1)
    print("Determing if ocean is soup...")
    time.sleep(2)

def print_current_board_state(gameboard):
    '''print the board with its current situation'''
    #time.sleep(2)
    board_state = open('board_state.txt', 'r')
    board_labels = open('board_labels.txt', 'r')
    label_lines = [line[:-1] for line in board_labels]
    position_to_look_at = 0
    for line_position, line in enumerate(board_state):
        for position, character in enumerate(line):
            if character == 'x':
                occupant = str(gameboard.get_occupant_of_position(bq.order_of_cells[position_to_look_at]))
                if occupant == '0':
                    occupant = ' '
                elif occupant == '1':
                    occupant = 'X'
                else:
                    occupant = 'O'
                line = line[:position] + occupant + line[position+1:]
                position_to_look_at += 1
        line = line[:-1] + " "*(100-len(line))
        print(line, end="")
        print(label_lines[line_position])

def ask_for_input(gameboard, turn, name, turn_count, moves, captures, move_from = 0):
    if move_from == 0:
        print_status_line(name, turn, turn_count)
    while True:
        if move_from == 0:
            command = input("Enter an input: ").lower()
        if move_from != 0:
            command = input("Enter an input (" + str(move_from) + " -> ?): ").lower()
        if command == '?':
            show_options()
        elif command in ('s', 'state'):
            print_current_board_state(gameboard)
        elif command in ('l', 'legal'):
            show_legal_moves(moves, captures)
        elif command in ('r', 'rules'):
            show_rules()
        elif command in ('b', 'back'):
            return '0'
        else:
            try:
                position = int(command)
                if 1 <= position <= 41:
                    final_position = check_if_move_is_legal(position, moves, captures, move_from)
                    if final_position != 0:
                        return final_position
                    #otherwise, prints were handled in check_if_move_is_legal
                else:
                    print("Position out of range (must be 1 through 41)")
            except:
                print("Please enter a valid input (type '?' to see all inputs)")

def check_if_move_is_legal(position, moves, captures, move_from):
    '''Given a movement from or movement to, determine if this an allowable move'''
    #move_from is set to 0 when inputting the move_from
    #updated once we're looking for move_to
    if move_from == 0:
        if position in moves:
            return position
        else:
            print("You have no tokens on position " + str(position))
            print("Type l(egal) to see your legal moves")
            return 0

    else:
        if position in moves[move_from]:
            print("Moving token to " + str(position) + " from " + str(move_from))
            return position
        elif position in captures[move_from]:
            print("Capturing token on " + str(position) + " from " + str(move_from))
            return position
        else:
            print("You cannot move to " + str(position) + " with the token on " + str(move_from))
            print("Type l(egal) to see your legal moves")
            return 0

def show_legal_moves(moves, captures):
    for position in moves:
        move_destinations = moves[position]
        capture_destinations = captures[position]
        if len(move_destinations) == 0:
            #print("Your token on spot " + str(position) + " cannot move anywhere")
            pass
        else:
            move_destinations_string = ", ".join(map(str, move_destinations))
            print("Your token on spot " + str(position) + " can move to spot(s) " + move_destinations_string)
        if len(capture_destinations) == 0:
            #print("Your token on spot " + str(position) + " cannot capture anything")
            pass
        else:
            capture_destinations_string = ", ".join(map(str, capture_destinations))
            print("Your token on spot " + str(position) + " can capture the token(s) on spots " + capture_destinations_string)

def print_status_line(name, turn, turn_count):
    if turn == 1:
        print("It's " + name + "'s turn (X) - Turn " + str(turn_count))
    else:
        print("It's " + name + "'s turn (O) - Turn " + str(turn_count))

def show_rules():
    print("""\n\nWelcome to Tessella! To win the game, you must be the first to capture 4 of your opponents 7 tokens.
Every turn you have 2 options: move a token, or capture an enemy's token. You must take one of these two actions.


Moving a token simply involves moving a token to an adjacent, unoccupied shape (it must share a side).
A token on a central octagon, for instance, could move to up to 8 shapes. A token on a square could move to up to 4.


Capturing tokens happen along rows, columns, and diagonals of the gameboard.
In order to capture, a sequence must exist on one of these straight lines of: your token, your token, enemy token.
Unoccupied shapes are allowed in between, and more tokens may come before or after this sequence, but this precise sequence must exist somewhere on the row/column/diagonal.

To capture, the middle token moves to occupy the enemy token's position on the gameboard. The enemy token is then removed.
Think of it like a queen in chess, or perhaps like the back token as the gun barrel, the middle token as the bullet, and your opponent's token as the target.

As an example, say your opponent had tokens on shapes 5, 38, and 21 while you had tokens on shapes 13 and 35.
Two sequences of <you, you, opponent> exist on this row.
You could either use 13 to capture on 5 (35 is the 'barrel'), or use 35 to capture on 38 (13 is the 'barrel').
Note that if it was your opponent's turn, they could use 38 to capture on 35, as they also have the needed sequence (21 is the 'barrel').

You can also capture along the 4 rows and 4 columns of the 4x4 grid of squares, even though the squares do not share sides.
The grid's diagonals are already part of rows and columns of alternating octagons and squares, so you may not ignore the octagons to make captures in those directions.
Note that in the board's diamond orientation, the diagonals appear as the horizontal and vertical rows, and vice-versa.



Have fun!\n\n""")

def show_options():
    print("\nHere are a list of all valid inputs")
    print("<Integer from 1 to 41>: Move your token from this square")
    print("After doing so: <Integer from 1 to 41>: Move your token to this square\n\n")

    print("?: Get this list you're already looking at")
    print("s(tate): See the current board state, and the labels of all positions on the board")
    print("r(ules): Learn the rules of Tessella")
    print("l(egal): See all moves you can legally make\n\n")
    print("b(ack): When choosing a token's destination, reselect which token to move")

def ai_thought(name):
    print(name + " is considering their moves very carefully...")
    time.sleep(3)
    print("Very very carefully...")
    time.sleep(3)

def ai_decision(name, move_to, move_from, moves):
    #print(move_from)
    #print(moves)
    if move_to in moves[move_from]:
        print(name + " moved to " + str(move_to) + " from " + str(move_from))
    else:
        print(name + " captured on " + str(move_to) + " from " + str(move_from))
        print("Take that!")
    time.sleep(3)
