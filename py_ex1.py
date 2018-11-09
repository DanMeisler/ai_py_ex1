#!/usr/bin/python
from collections import deque
import os

INPUT_FILE_PATH = os.path.join("input.txt")
OUTPUT_FILE_PATH = os.path.join("output.txt")


class Search(object):
    def __init__(self, board):
        self._route = []
        self._board = board
        self._opened_node_count = 0

    @property
    def route(self):
        return self._route

    @property
    def board(self):
        return self._board

    def search(self):
        pass


class Bfs(Search):
    def __init__(self, board):
        super(Bfs, self).__init__(board)
        self.open_nodes = deque()

    def search(self):
        pass


class State(object):
    def __init__(self, state_string, matrix_size):
        self._matrix_size = matrix_size
        state_list = [int(x) for x in state_string.split("-")]
        self._matrix = self.list_to_matrix(state_list, self._matrix_size)

    def __str__(self):
        state_list = self.matrix_to_list(self._matrix)
        return "-".join([str(x) for x in state_list])

    def move_up(self):
        empty_y, empty_x = self._locate(0)
        if empty_y == self._matrix_size - 1:
            raise Exception("Cannot move up")

        self._matrix[empty_y][empty_x] = self._matrix[empty_y + 1][empty_x]
        self._matrix[empty_y + 1][empty_x] = 0

    def move_down(self):
        empty_y, empty_x = self._locate(0)
        if empty_y == 0:
            raise Exception("Cannot move down")

        self._matrix[empty_y][empty_x] = self._matrix[empty_y - 1][empty_x]
        self._matrix[empty_y - 1][empty_x] = 0

    def move_left(self):
        empty_y, empty_x = self._locate(0)
        if empty_x == self._matrix_size - 1:
            raise Exception("Cannot move left")

        self._matrix[empty_y][empty_x] = self._matrix[empty_y][empty_x + 1]
        self._matrix[empty_y][empty_x + 1] = 0

    def move_right(self):
        empty_y, empty_x = self._locate(0)
        if empty_x == 0:
            raise Exception("Cannot move right")

        self._matrix[empty_y][empty_x] = self._matrix[empty_y][empty_x - 1]
        self._matrix[empty_y][empty_x - 1] = 0

    def is_goal_state(self):
        state_list = self.matrix_to_list(self._matrix)

        if state_list[-1] != 0:
            return False

        for i in range(0, len(state_list) - 2):
            if state_list[i] > state_list[i + 1]:
                return False

        return True

    def _locate(self, value):
        for row in range(self._matrix_size):
            for column in range(self._matrix_size):
                if self._matrix[row][column] == value:
                    return row, column

    @staticmethod
    def list_to_matrix(state_list, matrix_size):
        return [[state_list[y * matrix_size + x] for x in range(matrix_size)] for y in range(matrix_size)]

    @staticmethod
    def matrix_to_list(matrix):
        state_list = []
        for row in matrix:
            state_list.extend(row)
        return state_list


class InputParameters(object):
    SEARCH_TYPES = {1: "IDS", 2: "BFS", 3: "A*"}

    def __init__(self, input_file):
        self._input_file = input_file
        self._search_type = None
        self._board_size = None
        self._init_state_string = None
        self._parse_input_file()

    @property
    def search_type(self):
        return self._search_type

    @property
    def board_size(self):
        return self._board_size

    @property
    def init_state_string(self):
        return self._init_state_string

    def _parse_input_file(self):
        self._search_type = self.SEARCH_TYPES[int(self._input_file.readline())]
        self._board_size = int(self._input_file.readline())
        self._init_state_string = self._input_file.readline()


class Board(object):

    def __init__(self, init_state_string, board_size):
        self._board_size = board_size
        self._state = State(init_state_string, self._board_size)

    def __str__(self):
        return "board size is %dX%d, current state is \"%s\"" % (self._board_size, self._board_size, self._state)

    def move(self, direction):
        pass


def main():
    with open(INPUT_FILE_PATH, "r") as input_file:
        input_parameters = InputParameters(input_file)

    board = Board(input_parameters.init_state_string, input_parameters.board_size)

    if input_parameters.search_type == "IDS":
        pass
    elif input_parameters.search_type == "BFS":
        Bfs(board).search()
    elif input_parameters.search_type == "A*":
        pass


if __name__ == "__main__":
    main()
