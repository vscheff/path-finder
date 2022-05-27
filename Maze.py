from random import randint


class Maze:

    # @ param   height - number of rows in the maze
    # @ param    width - number of columns in the maze
    # @ param   engine - graphics engine object
    # @ param max_path - maximum number of paths the algorithm will advance on each iteration
    # @  attr     maze - 2D array containing ints representing the Maze
    # @  attr    start - coordinates of the start point
    # @  attr      end - coordinates of the end point
    # @  attr solution - list of the coordinates used to traverse the shortest path
    # @  attr  checked - list of coordinates checked while solving the maze
    # @  attr    paths - list of each active path being checked while solving the maze
    def __init__(self, height, width, engine, max_path=16):
        self.height = height
        self.width = width
        self.engine = engine
        self.max_paths = max_path
        self.maze = []
        self.start = (0, 0)
        self.end = (0, 0)
        self.solution = []
        self.checked = []
        self.paths = []

    # Updates the dimensions of the maze
    # @ param height - number of desired rows in the maze
    # @ param  width - number of desired columns in the maze
    def set_dimensions(self, height, width):
        self.height = height
        self.width = width

    # Clears memory involved in solving the maze
    def clear_solution(self):
        self.solution = []
        self.checked = [self.start]
        # Start one path at the starting coordinate
        self.paths = [[self.distance(self.start), [self.start]]]

    # Constructs a new randomly generated maze
    # @ return self.maze - newly constructed maze
    def build_maze(self):
        # Each cell in the maze has a 2/3 chance of being a clear spot, and 1/3 chance of being a wall
        self.maze = [[0 if randint(0, 2) else 1 for _ in range(self.width)] for _ in range(self.height)]
        # Chose a random cell to start in and place an 'S' there
        self.start = i, j = self.get_rand()
        self.maze[i][j] = 'S'
        # Chose a random cell to end in and place an 'E' there

        self.end = i, j = self.get_rand(False)
        self.maze[i][j] = 'E'
        # New maze requires a clear memory
        self.clear_solution()
        return self.maze

    # Get a random coordinate pair from the maze
    # @  param start - pass False if you need a coordinate pair that isn't adjacent to the start coordinate
    # @ return  rand - tuple of ints representing a random coordinate pair in the maze
    def get_rand(self, start=True):
        if start:
            return randint(0, self.height - 1), randint(0, self.width - 1)
        else:
            # Loop until the recursive call returns good coordinates
            rand = self.get_rand()
            while bad_coords(self.start, rand):
                rand = self.get_rand()
            return rand

    # Solve the maze by finding the shortest path from start to end
    # return  True - if a solution to the maze is found
    # return False - if no solution is found
    def solve(self):
        # Loop as long as there are valid paths to check
        while self.paths:
            # Only allow the algorithm to advance a number of paths <= self.max_paths
            num_paths = min(len(self.paths), self.max_paths)
            # Sort the paths by their distance from the end position
            self.paths = sorted(self.paths, key=lambda lst: lst[0])
            for _ in range(num_paths):
                self.engine.event_loop()
                path = self.paths.pop(0)[1]
                i, j = path[-1]
                # Loop for each valid move from the most recent move on the path
                for row, col in self.get_directions(i, j):
                    if self.maze[row][col] == 'E':
                        # Only use coordinates beyond the starting point to prevent that cell from turning gold
                        self.solution = path[1:]
                        self.engine.draw_solution(self.solution)
                        return True
                    # Create a new path consisting of this move and the rest of the path
                    self.paths.append([self.distance((row, col)), path + [(row, col)]])
                    self.checked.append((row, col))
                    # Turn this square blue
                    self.engine.update_square(row, col)
        return False

    # Generates valid moves from a given coordinate pair
    # param        i - row value of coordinate pair
    # param        j - col value of coordinate pair
    # yield row, col - Coordinate pair of a valid move from the given coordinates
    def get_directions(self, i, j):
        # Use min and max to ensure we only get valid indexes in each direction
        move = ((i, min(j + 1, self.width - 1)),   # East
                (min(i + 1, self.height - 1), j),  # South
                (i, max(j - 1, 0)),                # West
                (max(i - 1, 0), j))                # North
        for row, col in move:
            # Verifies this cell hasn't already been checked, and isn't a wall
            if (row, col) not in self.checked and self.maze[row][col] != 1:
                yield row, col

    # Calculates the Manhattan distance between given coordinates and the end coordinate
    # @  param coords - coordinate pair to be checked
    # @ return        - Manhattan distance
    def distance(self, coords):
        x1, y1 = coords
        x2, y2 = self.end
        return abs(x1 - x2) + abs(y1 - y2)


# Determines if two given coordinate pairs are the same cell, or adjacent cells
# @  param known - coordinate pair being checked against
# @  param check - coordinate pair being verified
# @ return  True - if the check coordinates are found to be 'bad'
def bad_coords(known, check):
    if known == check:
        return True
    if any(known == (check[0] + i, check[1]) for i in (-1, 1)):
        return True
    if any(known == (check[0], check[1] + i) for i in (-1, 1)):
        return True
