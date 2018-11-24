#!/usr/bin/python
from collections import deque
import heapq
import copy
import os

INPUT_FILE_PATH = os.path.join("input.txt")
OUTPUT_FILE_PATH = os.path.join("output.txt")


class InputParameters(object):
    SEARCH_TYPES = {1: "IDS", 2: "BFS", 3: "A*"}

    def __init__(self, input_file):
        self._input_file = input_file
        self.search_type = None
        self.board_size = None
        self.init_state_raw = None
        self._parse_input_file()

    def _parse_input_file(self):
        self.search_type = self.SEARCH_TYPES[int(self._input_file.readline())]
        self.board_size = int(self._input_file.readline())
        self.init_state_raw = [int(x) for x in self._input_file.readline().split("-")]


class PriorityQueue(object):
    def __init__(self, elements=None):
        self._next_item_id = 0
        if not elements:
            self._elements = []
        else:
            self._elements = elements

    def push(self, item, priority):
        heapq.heappush(self._elements, (priority, self._next_item_id, item))
        self._next_item_id += 1

    def pop(self):
        return heapq.heappop(self._elements)[2]


class Search(object):
    def __init__(self, problem):
        self._problem = problem
        self.opened_node_count = None
        self._nodes = None

    def search(self):
        raise NotImplementedError()

    def _init_nodes(self):
        raise NotImplementedError()

    def _open_node(self):
        raise NotImplementedError()

    def _add_node(self, parent, operator):
        raise NotImplementedError()

    def _create_node(self, parent, operator):
        return ProblemNode(self._problem.operate(parent.state, operator), parent, operator)


class Bfs(Search):
    def __init__(self, problem):
        super(Bfs, self).__init__(problem)
        self._init_nodes()

    def search(self):
        node = self._open_node()
        while not node.state.is_goal():
            for operator in self._problem.operators:
                self._add_node(node, operator)
            node = self._open_node()

        return node

    def _init_nodes(self):
        self.opened_node_count = 0
        self._nodes = deque([self._problem.root_node])

    def _open_node(self):
        self.opened_node_count += 1
        return self._nodes.popleft()

    def _add_node(self, parent, operator):
        try:
            self._nodes.append(self._create_node(parent, operator))
        except Exception:
            pass


class Ids(Search):
    def __init__(self, problem):
        super(Ids, self).__init__(problem)
        self._init_nodes()
        self.depth = 0

    def search(self):
        while True:
            goal_node = self._search_current_depth()
            if goal_node:
                return goal_node
            self.depth += 1
            self._init_nodes()

    def _search_current_depth(self):
        node = self._open_node()
        while not node.state.is_goal():
            if node.depth < self.depth:
                for operator in reversed(self._problem.operators):
                    self._add_node(node, operator)
            if len(self._nodes) == 0:
                return None
            node = self._open_node()

        return node

    def _init_nodes(self):
        self.opened_node_count = 0
        self._nodes = deque([self._problem.root_node])

    def _open_node(self):
        self.opened_node_count += 1
        return self._nodes.popleft()

    def _add_node(self, parent, operator):
        try:
            self._nodes.appendleft(self._create_node(parent, operator))
        except Exception:
            pass


class AStar(Search):
    def __init__(self, problem):
        super(AStar, self).__init__(problem)
        self._init_nodes()

    def search(self):
        node = self._open_node()
        while not node.state.is_goal():
            for operator in self._problem.operators:
                self._add_node(node, operator)
            node = self._open_node()
        return node

    def _init_nodes(self):
        self.opened_node_count = 0
        self._nodes = PriorityQueue()
        self._nodes.push(self._problem.root_node, self._problem.root_node.cost)

    def _open_node(self):
        self.opened_node_count += 1
        return self._nodes.pop()

    def _add_node(self, parent, operator):
        try:
            node = self._create_node(parent, operator)
        except Exception:
            return
        self._nodes.push(node, node.cost)


class ProblemNode(object):
    def __init__(self, state, parent, operator):
        self.parent = parent
        self.operator = operator
        self.state = state

    def __repr__(self):
        return repr(self.state) + " " + self.path

    @property
    def depth(self):
        depth = 0
        node = self
        while node.parent:
            depth += 1
            node = node.parent
        return depth

    @property
    def path(self):
        path = ""
        node = self
        while node.parent:
            path = node.operator + path
            node = node.parent
        return path

    @property
    def cost(self):
        return self.state.heuristic + self.depth


class ProblemState(object):

    @property
    def heuristic(self):
        raise NotImplementedError()

    def is_goal(self):
        """
        :return: return true if the state is a goal state
        """
        raise NotImplementedError()


class TilesGameState(ProblemState):
    def __init__(self, raw, board_size):
        super(TilesGameState, self).__init__()
        self._board_size = board_size
        self.raw = raw

    def __str__(self):
        return "-".join([str(x) for x in self.raw])

    def __repr__(self):
        return str(self) + " (h=%d)" % self.heuristic

    @property
    def heuristic(self):
        return self._calculate_manhattan_distance()

    def is_goal(self):
        return self.heuristic == 0

    def move_up(self):
        empty_index = self.raw.index(0)
        tile_index = empty_index + self._board_size
        if tile_index >= len(self.raw):
            raise Exception("Cannot move up")
        self.raw[empty_index], self.raw[tile_index] = self.raw[tile_index], self.raw[empty_index]

    def move_down(self):
        empty_index = self.raw.index(0)
        tile_index = empty_index - self._board_size
        if tile_index < 0:
            raise Exception("Cannot move down")
        self.raw[empty_index], self.raw[tile_index] = self.raw[tile_index], self.raw[empty_index]

    def move_left(self):
        empty_index = self.raw.index(0)
        tile_index = empty_index + 1
        if tile_index % self._board_size == 0:
            raise Exception("Cannot move left")
        self.raw[empty_index], self.raw[tile_index] = self.raw[tile_index], self.raw[empty_index]

    def move_right(self):
        empty_index = self.raw.index(0)
        tile_index = empty_index - 1
        if empty_index % self._board_size == 0:
            raise Exception("Cannot move right")
        self.raw[empty_index], self.raw[tile_index] = self.raw[tile_index], self.raw[empty_index]

    def _calculate_manhattan_distance(self):
        distance_sum = 0
        for i in xrange(1, self._board_size ** 2):
            i_index = self.raw.index(i)
            y1 = i_index / self._board_size
            x1 = i_index % self._board_size
            y2 = (i - 1) / self._board_size
            x2 = (i - 1) % self._board_size
            distance_sum += abs(x2 - x1) + abs(y2 - y1)
        return distance_sum


class Problem(object):
    def __init__(self, root_node, operators):
        """
        :param root_node: the root node of the problem graph
        :param operators: list which should be sorted by the search priority
        """
        self.operators = operators
        self.root_node = root_node

    def operate(self, state, operator):
        """
        :param state: the source state we want to apply the operator on
        :param operator: the operator we want to apply
        :return: a state which was crafted from the source state by using the selected operator
        """
        raise NotImplementedError()


class TilesGame(Problem):
    MOVES = ["U", "D", "L", "R"]

    def __init__(self, init_state_raw, board_size):
        super(TilesGame, self).__init__(ProblemNode(TilesGameState(init_state_raw, board_size), None, None),
                                        self.MOVES)
        self._board_size = board_size

    def operate(self, state, operator):
        new_state = TilesGameState(copy.copy(state.raw), self._board_size)
        if operator == "U":
            new_state.move_up()
        elif operator == "D":
            new_state.move_down()
        elif operator == "L":
            new_state.move_left()
        elif operator == "R":
            new_state.move_right()
        return new_state


def create_output(*args):
    with open(OUTPUT_FILE_PATH, "w") as output_file:
        output_file.write(" ".join(map(lambda x: str(x), args)))


def main():
    with open(INPUT_FILE_PATH, "r") as input_file:
        input_parameters = InputParameters(input_file)

    game = TilesGame(input_parameters.init_state_raw, input_parameters.board_size)

    if input_parameters.search_type == "IDS":
        search = Ids(game)
        goal_node = search.search()
        create_output(goal_node.path, search.opened_node_count, search.depth)
    elif input_parameters.search_type == "BFS":
        search = Bfs(game)
        goal_node = search.search()
        create_output(goal_node.path, search.opened_node_count, 0)
    elif input_parameters.search_type == "A*":
        search = AStar(game)
        goal_node = search.search()
        create_output(goal_node.path, search.opened_node_count, goal_node.cost)


if __name__ == "__main__":
    main()
