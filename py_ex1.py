#!/usr/bin/python
from collections import deque
import os

INPUT_FILE_PATH = os.path.join("input.txt")
OUTPUT_FILE_PATH = os.path.join("output.txt")


class InputParameters(object):
    SEARCH_TYPES = {1: "IDS", 2: "BFS", 3: "A*"}

    def __init__(self, input_file):
        self._input_file = input_file
        self.search_type = None
        self.board_size = None
        self.init_state_string = None
        self._parse_input_file()

    def _parse_input_file(self):
        self.search_type = self.SEARCH_TYPES[int(self._input_file.readline())]
        self.board_size = int(self._input_file.readline())
        self.init_state_string = self._input_file.readline()


class Search(object):
    def __init__(self, problem):
        self._problem = problem
        self.opened_node_count = None
        self._nodes = None
        self._init_nodes()

    def search(self):
        raise NotImplementedError()

    def _init_nodes(self):
        self._nodes = deque([self._problem.root_node])
        self.opened_node_count = 0

    def _open_node(self):
        self.opened_node_count += 1
        return self._nodes.popleft()

    def _create_node(self, parent, operator):
        return ProblemNode(self._problem.operate(parent.state, operator), parent, operator)


class Bfs(Search):
    def __init__(self, problem):
        super(Bfs, self).__init__(problem)

    def search(self):
        node = self._open_node()
        while not node.state.is_goal():
            for operator in self._problem.operators:
                self._add_node(node, operator)
            node = self._open_node()

        return node

    def _add_node(self, parent, operator):
        try:
            self._nodes.append(self._create_node(parent, operator))
        except Exception:
            pass


class Ids(Search):
    def __init__(self, problem):
        super(Ids, self).__init__(problem)
        self.depth = 0

    def search(self):
        while True:
            goal_node = self._search_current_depth()
            if goal_node:
                return goal_node
            self.depth += 1
            self._init_nodes()

    def _add_children(self, parent):
        for operator in reversed(self._problem.operators):
            try:
                self._nodes.appendleft(self._create_node(parent, operator))
            except Exception:
                pass

    def _search_current_depth(self):
        node = self._open_node()
        while not node.state.is_goal():
            if node.depth < self.depth:
                self._add_children(node)
            if len(self._nodes) == 0:
                return None
            node = self._open_node()

        return node


class AStar(Search):
    def __init__(self, problem):
        super(AStar, self).__init__(problem)

    def search(self):
        node = self._open_node()
        i = 0
        while not node.state.is_goal():
            print i, node, node.cost
            i += 1
            for operator in self._problem.operators:
                self._add_node(node, operator)
            node = self._open_node()
        return node

    def _add_node(self, parent, operator):
        try:
            self._nodes.append(self._create_node(parent, operator))
        except Exception:
            return
        self._nodes = deque(sorted(self._nodes, key=lambda x: x.cost))


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
        return self.state.manhattan_distance + self.depth


class ProblemState(object):
    @property
    def manhattan_distance(self):
        raise NotImplementedError()

    def is_goal(self):
        raise NotImplementedError()


class TilesGameState(ProblemState):
    def __init__(self, state, board_size):
        super(TilesGameState, self).__init__()
        self._board_size = board_size
        self._list = [int(x) for x in state.split("-")]

    def __str__(self):
        return "-".join([str(x) for x in self._list])

    def __repr__(self):
        return str(self) + " (md=%d)" % self.manhattan_distance

    @property
    def manhattan_distance(self):
        distance_sum = 0
        for i in xrange(1, self._board_size ** 2):
            y1 = self._list.index(i) / self._board_size
            x1 = self._list.index(i) % self._board_size
            y2 = (i - 1) / self._board_size
            x2 = (i - 1) % self._board_size
            distance_sum += abs(x2 - x1) + abs(y2 - y1)
        return distance_sum

    def is_goal(self):
        return self.manhattan_distance == 0

    def move_up(self):
        empty_index = self._list.index(0)
        tile_index = empty_index + self._board_size
        if tile_index >= len(self._list):
            raise Exception("Cannot move up")
        self._list[empty_index], self._list[tile_index] = self._list[tile_index], self._list[empty_index]

    def move_down(self):
        empty_index = self._list.index(0)
        tile_index = empty_index - self._board_size
        if tile_index < 0:
            raise Exception("Cannot move down")
        self._list[empty_index], self._list[tile_index] = self._list[tile_index], self._list[empty_index]

    def move_left(self):
        empty_index = self._list.index(0)
        tile_index = empty_index + 1
        if tile_index % self._board_size == 0:
            raise Exception("Cannot move left")
        self._list[empty_index], self._list[tile_index] = self._list[tile_index], self._list[empty_index]

    def move_right(self):
        empty_index = self._list.index(0)
        tile_index = empty_index - 1
        if empty_index % self._board_size == 0:
            raise Exception("Cannot move right")
        self._list[empty_index], self._list[tile_index] = self._list[tile_index], self._list[empty_index]


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
        :return: a state which was crafted from the source state by using operator
        """
        raise NotImplementedError()


class TilesGame(Problem):
    MOVES = ["U", "D", "L", "R"]

    def __init__(self, init_state_string, board_size):
        super(TilesGame, self).__init__(ProblemNode(TilesGameState(init_state_string, board_size), None, None),
                                        self.MOVES)
        self._board_size = board_size

    def operate(self, state, operator):
        state = TilesGameState(str(state), self._board_size)
        if operator == "U":
            state.move_up()
        elif operator == "D":
            state.move_down()
        elif operator == "L":
            state.move_left()
        elif operator == "R":
            state.move_right()
        return state


def create_output(*args):
    with open(OUTPUT_FILE_PATH, "w") as output_file:
        output_file.write(" ".join(map(lambda x: str(x), args)))


def main():
    with open(INPUT_FILE_PATH, "r") as input_file:
        input_parameters = InputParameters(input_file)

    game = TilesGame(input_parameters.init_state_string, input_parameters.board_size)

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
