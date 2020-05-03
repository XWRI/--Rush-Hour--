import queue
from queue import PriorityQueue
import sys
import copy


# Sets the default recursion limit to satisfy the search
sys.setrecursionlimit(10**6)

# An object storing all the relevant information about the state,
#   game board: stored as a single string
#   g_n: the number of steps taken from the start to the current state
#   h_n: the minimum number of steps needed to reach the goal state
#   f_n: sum of g_n and h_n
#   parent: the parent state which the current state derived from
class BoardState(object):
    def __init__(self, board, g_n, h_n, f_n, parent):
        self.board = board
        self.g_n = g_n
        self.h_n = h_n
        self.f_n = f_n
        self.parent = parent

    # Overloads the less than comparator
    # in order for the PriorityQueue to sort this class object
    def __lt__(self, other):
        return self.f_n < other.f_n








# This function provides an overall structure on the steps taken to solve
# the game Rush Hour
#   @param:
#   heuristic: the choice to heuristic to use in solve the game
#   state: the initial state of the gameboard
def rushhour(heuristic, state):
    # Converts the list of string into a single string for the initial board
    initial_board = ""
    for row in state:
        initial_board += row

    # Finds the h(n) of the initial state
    cur_h_n = 0
    if heuristic == 0:
        cur_h_n = blocking_heuristic(initial_board)
    else :
        cur_h_n = custome_heuristic(initial_board)

    # Creates the first state
    initial_state = BoardState(initial_board, 0, cur_h_n, cur_h_n + 0, None)

    # Creates a PriorityQueue to store all the states in order
    frontier = PriorityQueue()
    frontier.put(initial_state)

    # Creates two lists to store the explored and unexplored states
    explored_states = []
    unexplored = []

    # Uses the given choice of heuristics to determine the optimal solution
    # Gets the end state
    end_state = state_search(frontier,
                             heuristic,
                             explored_states,
                             unexplored)

    # Creates a list to store the result gameboard in sequence
    answer = []

    # Fills up the list by getting the parent board repeatedly until reach the
    # initial board
    while end_state != initial_state:
        answer.append(construct_board(end_state.board))
        end_state = end_state.parent
    answer.append(construct_board(initial_state.board))
    answer = reverse(answer)
    answer = complete_exit_move(answer) # In case it has not reach the exit

    # Prints out the result of the game
    for board in answer:
        print_board(board)
    print ('Total moves: ' + str(len(answer) - 1))
    print ("Total states explored: " + str(len(explored_states)))








# This function performs a state search
# It follows the idea of A* algorithm
#   @param:
#   frontier: a PriorityQueue storing all the newly generated states
#   heuristic: determine which heuristics to be used in the search
#   explored_states: a list of explored_states
#                    (cannot iterator through PriorityQueue)
#   unexplored: a list of unexplored states
#
#   ***** returns only the end goal state *****
def state_search(frontier, heuristic, explored_states, unexplored):
    if frontier.empty():
        return []

    curr_head = frontier.get()
    if reach_goal(curr_head):
        return curr_head
    else:
        new_boards = generate_new_boards(curr_head)
        explored_states.append(curr_head)

        # Adds the appropriate new states to the queue
        for board in new_boards:
            cur_h_n = compute_heuristic(heuristic, board)
            cur_g_n = curr_head.g_n + 1
            cur_f_n = cur_h_n + cur_g_n
            state = BoardState(board, cur_g_n, cur_h_n, cur_f_n, curr_head)

            if check_repeatition(state, unexplored) == True:
                del state
            elif check_repeatition(state, explored_states) == True:
                del state
            else:
                frontier.put(state)
                unexplored.append(state)

    return state_search(frontier,
                        heuristic,
                        explored_states,
                        unexplored)




# This function determines whether the input state has reached the goal state
#      ***** Here we think that as long as there is no
#            blocking vehicles on the third row blocking
#            the car X, it has reached the goal state.   *****
#   @param:
#   curr_head: the state of the game to be determined
#
#   returns True/False on whether it has reached the goal state
def reach_goal(curr_head):
    cur_board = construct_board(curr_head.board)
    if cur_board[2][4] == 'X' and cur_board[2][5] == 'X': return True
    for char in cur_board[2]:
        if char != 'X' and char != '-':
            return False
    return True




# This function checks for repeatition and eliminates redundant search
#   @param:
#   cur_state: the state to be checked for repeatitions
#   states: a list of states to be searched
#
#   returns True/False on whether it has repeatitions
def check_repeatition(cur_state, states):
    for state in states:
        if cur_state.board == state.board:
            return True
    return False




# This function compute the h_n of the given gameboard
#   @param:
#   heuristic: the choice of heuristic to adopt
#   board: the current gameboard
#
#   returns the computed h_n value
def compute_heuristic(heuristic, board):
    if heuristic == 0:
        return blocking_heuristic(board)
    else:
        return custome_heuristic(board)




# This function computes the customized heuristic
#   ***** The central idea of this heuristic is to consider *****
#   ***** the state of the blocking vehicles.               *****
#         First, find the information about the blocking vehicles
#         Then, check whether these blocking vehicles have been blocked
#         If they are blocked, compute the minimum steps needed to unblock
#         so that they can move out of the way of the blocking vehicles
#         so that the blocking vehicles can move out of the way of car X
#   ***** In this heuristic, we also consider the exact number *****
#   ***** of steps needed for car X to reach the exit, since X *****
#   ***** could be very close but with more blocking vehicles  *****
#   ***** or could be far but with less blocking vehicles, and *****
#   ***** former may be the optimal solution.                  *****
#
#   @param:
#   board: the current gameboard
#
#   returns the h_n value
def custome_heuristic(board):
    num_of_steps = 0
    # This variable helps eliminate the vehicles before the X car
    foundX = False
    for i in range(12, 18):
        if board[i] == 'X':
            foundX = True
            # Adds the number of steps needed to reach the exit
            num_of_steps += 18 - i - 2
        # If a vehicle is found, determine the type of the vehicle and
        # whether the vehicle has been blocked by other vehicles
        if (foundX == True and board[i] != 'X' and board[i] != '-'):
            pos = find_vehicle_vertical(i, board)
            # If the vehicle found is a truck
            if pos[2] - pos[0] == 2:
                num_of_steps += check_truck(pos, board)
            # If the vehicle found is a car
            else:
                num_of_steps += check_car(pos, board)
    return num_of_steps

# This function determines the minimum number of steps needed to move a
# vertical truck out of car X's way
#   @param:
#   pos: the coordinates of the truck
#        in the form of [x_start, y_start, x_end, y_end]
#   board: the current gameboard
#
#   returns the minimum number of steps needed to move a vertical truck out
#   of car X's way
def check_truck(pos, board):
    steps = 0
    # If it is positioned from the first row to the third row,
    # the only choice to move it away is to move down 3 times
    if pos[0] == 0:
        steps += 3
        # Check whether the spaces below the truck is empty
        steps += check_space_below_truck(3-pos[0], board, pos)
    # If it is positioned from the second row to the fourth row,
    # the only choice to move it away is to move down 2 times
    elif pos[0] == 1:
        steps += 2
        # Check whether the spaces below the truck is empty
        steps += check_space_below_truck(3-pos[0], board, pos)
    # If it is positioned from the third row to the fifth row,
    # the only choice to move it away is to move down 1 time
    else:
        steps += 1
        # Check whether the spaces below the truck is empty
        steps += check_space_below_truck(3-pos[0], board, pos)

    return steps

# This function checks whether the spaces below the truck are empty
# If not, how many steps minimum are needed to empty the spaces
#   @param:
#   space: the number of spaces to be checked
#   board: the current gameboard
#   pos: the coordinates of the truck
#        in the form of [x_start, y_start, x_end, y_end]
#
#   returns the minimum number of steps needed to empty the spaces
def check_space_below_truck(space, board, pos):
    steps = 0
    for i in range(1, space+1):
        if board[(pos[2]+i)*6 + pos[1]] != '-':
            steps += 1
            # It the space is not empty,
            # finds the position of the blocking vehicle
            block_pos = find_vehicle_horizontal((pos[2]+i)*6 + pos[1], board)
            steps += blocked_blocking_vehicle(pos, block_pos, board)
    return steps

# This function detemines the minimum number of steps needed to move the
#  blocking vehicle
#   @param:
#   pos: the coordinates of the truck (the blocking vehicle)
#        in the form of [x_start, y_start, x_end, y_end]
#   block_pos: the coordinates of the vehicle blocks the blocking vehicle
#        in the form of [x_start, y_start, x_end, y_end]
#   board: the current gameboard
#
#   returns the minimum number of steps needed to move the blocking vehicle
def blocked_blocking_vehicle(pos, block_pos, board):
    steps = 0
    # If both sides of the blocking vehicle has been blocked or
    # one side is blocked and the other side hits the wall
    if ((block_pos[1] == 0 or board[block_pos[0]*6 + block_pos[1] - 1] == '-')
        and (block_pos[3] == 5 or board[block_pos[2]*6 + block_pos[3] + 1] == '-')):
        steps += 1
    # Check how many steps needed to move the blocking vehicle
    # if the blocking vehicle blocks the truck in the middle,
    # then an extra step is needed
    if (block_pos[1] < pos[1] and block_pos[3] > pos[1]):
        steps += 1
    # If one side of the vehicle hits the wall and it blocks the truck
    # at some other position, an extra step is also needed
    elif (block_pos[3] == 5 and pos[3] != 5):
        steps += 1
    return steps


# This function determines the minimum number of steps needed to move a
# vertical car out of car X's way
#   @param:
#   pos: the coordinates of the car
#        in the form of [x_start, y_start, x_end, y_end]
#   board: the current gameboard
#
#   returns the minimum number of steps needed to move a vertical car out
#   of car X's way
def check_car(pos, board):
    steps = 1
    # If the car is placed on the second and third row, and there is a
    # vehicle blocking the car on top (the first row),
    # then, an extra step is needed
    if (pos[0] == 1 and board[pos[1]] != '-'):
        steps += 1
        # Finds the position of the vehicle blocking the car
        block_pos = find_vehicle_horizontal(pos[1], board)
        # If both sides of that vehicle has been blocked or
        # one side is blocked and the other side hits the wall,
        # then, an extra step is needed
        if ((block_pos[1] == 0 or board[block_pos[1] - 1] != '-') and
        (block_pos[3] == 5 or board[block_pos[3] + 1] != '-')):
            steps += 1
    # If the car is placed on the third and fourth row, and there is a
    # vehicle blocking the car on the bottom (the fifth row)
    # then, an extra step is needed
    elif (pos[2] == 3 and board[(pos[2]+1)*6 + pos[3]] != '-'):
        steps += 1
        # Finds the position of the vehicle blocking the car
        block_pos = find_vehicle_horizontal(pos[1], board)
        # If both sides of that vehicle has been blocked or
        # one side is blocked and the other side hits the wall,
        # then, an extra step is needed
        if ((block_pos[1] == 0 or board[block_pos[0]*6 + block_pos[1] - 1] != '-') and
        (block_pos[3] == 5 or board[block_pos[2]*6 + block_pos[3] + 1] != '-')):
            steps += 1
    return steps




# This function computes the blocking heuristic
#   @param:
#   board: the current gameboard
#
#   returns the computed h_n value
def blocking_heuristic(board):
    num_of_vehicle_blocking = 0

    # check the third row for the number of vehicles blocking the path
    foundX = False
    for i in range(12, 18):
        if board[i] == 'X': foundX = True
        if (foundX == True and board[i] != 'X' and board[i] != '-'):
            num_of_vehicle_blocking += 1
    if num_of_vehicle_blocking == 0: return 0
    return 1 + num_of_vehicle_blocking





# This function generate new boards from the given board input
# We check for all the possible moves with every vehicle on the board
#   @param:
#   state: the base state
#
#   returns a list of newly generated states
def generate_new_boards(state):
    new_boards = []
    visited = {}
    cur_board = state.board
    for i in range(0, len(cur_board)):
        if cur_board[i] not in visited:
            boards_moved = move_vehicle(i, cur_board)
            for board in boards_moved:
                new_boards.append(board)
            visited[cur_board[i]] = True
    return new_boards

# This function considers the movement possiblities for one specific vehicle
#   @param:
#   index: the index to detemine the specific vehicle
#   board: gameboard stored in a single string
#
#   returns a list of newly generated states for moving one vehicle
def move_vehicle(index, board):
    boards_moved = []
    # The vehicle is horizontal
    if ((index > 0 and board[index-1] == board[index]) or
        (index + 1 < len(board) and board[index+1] == board[index])):
        start_end_pos = find_vehicle_horizontal(index, board)
        # Checks for left and right with horizontal vehicle
        left = move_left(board, start_end_pos)
        if left != []:
            boards_moved.append(left)
        right = move_right(board, start_end_pos)
        if right != []:
            boards_moved.append(right)
    # The vehicle is vertical
    else:
        start_end_pos = find_vehicle_vertical(index, board)
        # Checks for up and down for vertical vehicle
        up = move_up(board, start_end_pos)
        if up != []:
            boards_moved.append(up)
        down = move_down(board, start_end_pos)
        if down != []:
            boards_moved.append(down)
    return boards_moved

# This function finds the start and end coordinates of vertical vehicles
#   @param:
#   index: the index to detemine the specific vehicle
#   board_string: gameboard stored in a single string
#
#   return the coordinates of the vehicle in the form of a lists
#   [x_start, y_start, x_end, y_end]
def find_vehicle_vertical(index, board_string):
    board = construct_board(board_string)
    row = int(index / 6)
    col = int(index % 6)
    # Creates a list storing the starting and ending position
    res_pos = []
    up = row
    down = row

    # Finds the starting position
    while (up >= 0 and board[up][col] == board[row][col]):
        up -= 1

    # Adding the starting coordinates of the vehicle
    if (up >= 0 and board[up][col] == board[row][col]):
        res_pos.append(up)
    else: res_pos.append(up+1)
    res_pos.append(col)

    # Finds the ending position
    while (down < len(board) and board[down][col] == board[row][col]):
        down += 1

    # Adding the ending coordinates of the vehicle
    if (down < len(board) and board[down][col] == board[row][col]):
        res_pos.append(down)
    else: res_pos.append(down-1)
    res_pos.append(col)

    return res_pos

# This function finds the start and end coordinates of horizontal vehicles
# and returns as list of [x_start, y_start, x_end, y_end]
#   @param:
#   index: the index to detemine the specific vehicle
#   board_string: gameboard stored in a single string
#
#   return the coordinates of the vehicle in the form of a lists
#   [x_start, y_start, x_end, y_end]
def find_vehicle_horizontal(index, board):
    row = int(index / 6)
    col = int(index % 6)
    # Creates a list storing the starting and ending position
    res_pos = []
    left = index
    right = index

    # Finds the starting position
    while (left >= 0 and board[left] == board[index]):
        left -= 1

    # Adding the starting coordinates of the vehicle
    res_pos.append(row)
    if (left >= 0 and board[left] == board[index]):
        res_pos.append(left % 6)
    else: res_pos.append((left+1) % 6)

    # Finds the ending position
    while (right < len(board) and board[right] == board[index]):
        right += 1

    # Adding the ending coordinates of the vehicle
    res_pos.append(row)
    if (right < len(board) and board[right] == board[index]):
        res_pos.append(right % 6)
    else: res_pos.append((right-1) % 6)

    return res_pos


# The following four functions move the vehicle in four different direcitons
# All the four functions have the same parameters
#   @param:
#   curr_board: a single string storing the current board state
#   pos: the coordinates of the moving vehicle in the form of
#        [x_start, y_start, x_end, y_end]
#
#   All four functions return the new gameboard in the form of a single string

def move_up(curr_board, pos):
    board = construct_board(curr_board)
    # If the starting position is already on the first row
    # or there is a vehicle blocking it moving up
    if pos[0] == 0 or board[pos[0] - 1][pos[1]] != '-':
        return []

    # Move up
    board[pos[0] - 1][pos[1]] = board[pos[0]][pos[1]]
    board[pos[2]][pos[3]] = '-'
    return board_to_string(board)

def move_down(curr_board, pos):
    board = construct_board(curr_board)
    # If the ending position is already on the last row
    # or there is a vehicle blocking it moving down
    if pos[2] >= len(board) - 1 or board[pos[2] + 1][pos[3]] != '-':
        return []

    # Move down
    board[pos[2] + 1][pos[3]] = board[pos[2]][pos[3]]
    board[pos[0]][pos[1]] = '-'
    return board_to_string(board)

def move_left(curr_board, pos):
    board = construct_board(curr_board)
    # If the starting position is already on the first col
    # or there is a vehicle blocking it moving left
    if pos[1] == 0 or board[pos[0]][pos[1] - 1] != '-':
        return []

    # Move left
    board[pos[0]][pos[1] - 1] = board[pos[0]][pos[1]]
    board[pos[2]][pos[3]] = '-'
    return board_to_string(board)

def move_right(curr_board, pos):
    board = construct_board(curr_board)
    # If the starting position is already on the last col
    # or there is a vehicle blocking it moving right
    if pos[3] == len(board) - 1 or board[pos[2]][pos[3] + 1] != '-':
        return []

    # Move right
    board[pos[2]][pos[3] + 1] = board[pos[2]][pos[3]]
    board[pos[0]][pos[1]] = '-'
    return board_to_string(board)




# The following two functions are helper functions to switch the gameboard
# between a single string and a 2D array of characters
#
# Converts the board to a single string
#   @param:
#   board: an 2D array storing the gameboard
#
#   returns the gameboard in the form of a single string
def board_to_string(board):
    string = ""
    for i in range(len(board)):
        for j in range(len(board[0])):
            string += board[i][j]
    return string

# Constructs the board from a single string
#   @param:
#   string: the gameboard in the form of a single string
#
#   returns an 2D array storing the gameboard
def construct_board(string):
    board = [] * 6
    for i in range(0, len(string)):
        if i % 6 == 0:
            new_row = [] * 6
            new_row.append(string[i])
        elif i % 6 == 5:
            new_row.append(string[i])
            board.append(new_row)
        else:
            new_row.append(string[i])
    return board




# This functions prints the game board
#   @param:
#   state: 2D array representing the game board to be printed
def print_board(board):
    for row in board:
        for element in row:
            print(element, end = ' ')
        print()
    print()
    return



# This function completes the move from the current position to the exit
# when there is not blocking vehicles on the way
# Since we consider any state with no blocking vehicles blocking car X the
# goal state, car X might not reach the exit as we return the goal state
# Thus, we need to check and make sure that it reaches the exit
#   @param:
#   ans: a list of gameboard from the initial state to the goal state
#
#   ***** we build on the last gameboard of the list to *****
#   ***** complete the move to the exit.                *****
#
#   returns a complete step by step solution of the game
def complete_exit_move(ans):
    cur_board = ans[len(ans) - 1]
    car_pos_end = 0
    for i in range(len(cur_board[2])):
        if cur_board[2][i] == 'X':
            car_pos_end = i + 1
            break
    for i in range(car_pos_end+1, len(cur_board[2])):
        board = copy.deepcopy(cur_board)
        board[2][i] = 'X'
        board[2][i-2] = '-'
        ans.append(board)
        cur_board = board
    return ans



# This helper function reverses the order of a list and is taken from
# professor's code on pegpuzzle
def reverse(st):
    return st[::-1]
