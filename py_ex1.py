#!/usr/bin/python
from collections import deque
import os

INPUT_FILE_PATH = os.path.join("input.txt")
OUTPUT_FILE_PATH = os.path.join("output.txt")


class Search(object):
    def __init__(self, problem):
        self._problem = problem
        self._nodes = deque([self._problem.root_node])
        self._opened_node_count = 0

    def _open_node(self):
        self._opened_node_count += 1
        return self._nodes.popleft()

    def _add_node(self, parent, operator):
        node_state = self._problem.operate(parent.state, operator)
        self._nodes.append(ProblemNode(node_state, parent, operator))

    @property
    def open_node_count(self):
        return self._opened_node_count

    def search(self):
        pass


class Bfs(Search):
    def __init__(self, problem):
        super(Bfs, self).__init__(problem)

    def search(self):
        node = self._open_node()
        while not node.is_goal():
            for operator in self._problem.operators:
                try:
                    self._add_node(node, operator)
                except Exception:
                    continue
            node = self._open_node()
        return node


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


class ProblemNode(object):
    def __init__(self, state, parent, operator):
        self._parent = parent
        self._operator = operator
        self._state = state

    def is_goal(self):
        return self._state.is_goal()

    @property
    def state(self):
        return self._state

    @property
    def parent(self):
        return self._parent

    @property
    def operator(self):
        return self._operator


class ProblemState(object):
    def __init__(self):
        pass

    def is_goal(self):
        pass


class GameState(ProblemState):
    def __init__(self, state, matrix_size):
        super(GameState, self).__init__()
        self._matrix_size = matrix_size
        state_list = [int(x) for x in state.split("-")]
        self._matrix = self.list_to_matrix(state_list, self._matrix_size)

    def __str__(self):
        state_list = self.matrix_to_list(self._matrix)
        return "-".join([str(x) for x in state_list])

    def is_goal(self):
        state_list = self.matrix_to_list(self._matrix)
        if state_list[-1] != 0:
            return False

        for i in range(0, len(state_list) - 2):
            if state_list[i] > state_list[i + 1]:
                return False

        return True

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


class Problem(object):
    def __init__(self, root_node, operators):
        self._operators = operators
        self._root_node = root_node

    @property
    def operators(self):
        return self._operators

    @property
    def root_node(self):
        return self._root_node

    def operate(self, state, operator):
        pass

    def get_path(self, node):
        pass


class Game(Problem):
    MOVE_UP = 1
    MOVE_DOWN = 2
    MOVE_LEFT = 3
    MOVE_RIGHT = 4

    def __init__(self, init_state_string, board_size):
        super(Game, self).__init__(ProblemNode(GameState(init_state_string, board_size), None, None),
                                   [self.MOVE_UP, self.MOVE_DOWN, self.MOVE_LEFT, self.MOVE_RIGHT])
        self._board_size = board_size

    def operate(self, state, operator):
        state = GameState(str(state), self._board_size)
        if operator == self.MOVE_UP:
            state.move_up()
        elif operator == self.MOVE_DOWN:
            state.move_down()
        elif operator == self.MOVE_LEFT:
            state.move_left()
        elif operator == self.MOVE_RIGHT:
            state.move_right()
        return state

    def _operator_to_character(self, operator):
        if operator == self.MOVE_UP:
            return "U"
        elif operator == self.MOVE_DOWN:
            return "D"
        elif operator == self.MOVE_LEFT:
            return "L"
        elif operator == self.MOVE_RIGHT:
            return "R"

    def get_path(self, node):
        path = ""
        while node.parent:
            path = self._operator_to_character(node.operator) + path
            node = node.parent
        return path


def create_output(*args):
    with open(OUTPUT_FILE_PATH, "w") as output_file:
        output_file.write(" ".join(map(lambda x: str(x), args)))


def main():
    with open(INPUT_FILE_PATH, "r") as input_file:
        input_parameters = InputParameters(input_file)

    game = Game(input_parameters.init_state_string, input_parameters.board_size)

    if input_parameters.search_type == "IDS":
        pass
    elif input_parameters.search_type == "BFS":
        search = Bfs(game)
        goal_node = search.search()
        create_output(game.get_path(goal_node), search.open_node_count, 0)
    elif input_parameters.search_type == "A*":
        pass


if __name__ == "__main__":
    main()
