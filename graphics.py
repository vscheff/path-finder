import pygame as pg
import Elements as El
from Maze import Maze
from math import floor
from time import sleep


class Engine:

    # @ param        height - height in pixels of the window
    # @ param         width - width in pixels of the window
    # @  attr   safe_height - max x value to be used when displaying the maze
    # @  attr    safe_width - max y value to be used when displaying the maze
    # @  attr        colors - dictionary of RGB color values
    # @  attr     font size - size of the font for text displayed on screen
    # @  attr          rows - number of rows in the maze
    # @  attr          cols - number of columns in the maze
    # @  attr         sleep - number of seconds to sleep after each square is updated
    # @  attr  border_width - width in pixels for border surrounding the display area for the maze
    # @  attr          font - pygame Font object
    # @  attr       display - pygame Surface object
    # @  attr       squares - dictionary of Square objects
    # @  attr   input_boxes - list of InputBox objects
    # @  attr speed_buttons - list of SpeedBut objects
    # @  attr          maze - 2D array of integers representing the maze
    # @  attr        solver - Maze solver object
    def __init__(self, height=720, width=1280):
        self.height = height
        self.width = width
        self.safe_height = self.height - 50
        self.safe_width = self.width - 230
        self.colors = {'wall':     (43,  43,  43),
                       'light_bg': (49,  51,  53),
                       'line':     (60,  63,  65),
                       'clear':    (175, 177, 179),
                       'text':     (200, 202, 204),
                       'start':    (145, 4,   4),
                       'end':      (7,   97,  4),
                       'path':     (4,   122, 145),
                       'solution': (163, 120, 2)}
        self.font_size = 25
        self.rows = 67
        self.cols = 105
        self.sleep = 0.001
        self.border_width = 10
        self.font = None
        self.display = None
        self.squares = {}
        self.buttons = []
        self.input_boxes = []
        self.speed_buttons = []
        self.maze = []
        self.solver = Maze(self.rows, self.cols, self)

    # Initializes the main display window
    def initialize(self):
        pg.init()
        # Set the title of the window
        pg.display.set_caption('Seeker of Paths')
        self.display = pg.display.set_mode(size=(self.width, self.height))
        self.display.fill(self.colors['line'])
        # Visually display the safe area for the maze
        x1y1 = 25 - self.border_width // 2
        rect = pg.Rect(x1y1, x1y1, self.safe_width + self.border_width, self.safe_height + self.border_width)
        self.update(El.Element(rect, self.colors['wall']))

        pg.display.flip()
        self.font = pg.font.Font(None, self.font_size)
        self.draw_menu()

    # Draws all of the UI elements on the screen
    def draw_menu(self):
        left_edge = self.width - 180
        top_edge = 25
        button_size = (100, 50)
        spacing = 15
        button_color = self.colors['light_bg']
        button_names = ('New Maze', 'Solve', 'Reset')
        button_funcs = (self.new_maze, self.solver.solve, self.draw_maze)

        # Create main control buttons
        for name, func in zip(button_names, button_funcs):
            rect = pg.Rect(left_edge, top_edge, *button_size)
            button = El.Button(rect, button_color, name, func)
            self.buttons.append(button)
            self.update(button)
            self.draw_font(button)
            top_edge += spacing + button_size[1]

        button_size = (60, 30)
        rect = pg.Rect(left_edge, top_edge, *button_size)
        self.draw_font(El.TextBox(rect, self.colors['text'], 'Speed'))
        top_edge += spacing * 2
        button_names = ('>', '>>', '>>>', '>>>>', '>>>>>')
        button_speed = (0.5, 0.1, 0.01, 0.001, 0)

        # Create speed buttons
        for name, speed in zip(button_names, button_speed):
            rect = pg.Rect(left_edge, top_edge, *button_size)
            active = name == button_names[-2]
            button = El.SpeedBut(rect, self.colors['clear'], button_color, name, self.set_sleep, active, speed)
            self.buttons.append(button)
            self.speed_buttons.append(button)
            self.update(button)
            color = self.colors['wall'] if active else None
            self.draw_font(button, color=color)
            top_edge += spacing + button_size[1]

        rect = pg.Rect(left_edge, top_edge, *button_size)
        self.draw_font(El.TextBox(rect, self.colors['text'], 'Rows'))
        rect = pg.Rect(left_edge + spacing + button_size[0], top_edge, *button_size)
        self.draw_font(El.TextBox(rect, self.colors['text'], 'Cols'))
        top_edge += spacing * 2
        row_data = self.solver.height, self.set_rows
        col_data = self.solver.width, self.set_cols

        # Create row/col inputs boxes
        for val, func in row_data, col_data:
            rect = pg.Rect(left_edge, top_edge, *button_size)
            button = El.InputBox(rect, self.colors['clear'], button_color, str(val), func)
            self.buttons.append(button)
            self.input_boxes.append(button)
            self.update(button)
            self.draw_font(button)
            left_edge += spacing + button_size[0]

    # Main loop of the engine, call to begin execution
    def main_loop(self):
        while True:
            self.event_loop()

    # Handles the OS event loop
    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit_screen()

            if event.type == pg.MOUSEBUTTONUP:
                button_pressed = False
                for button in self.input_boxes:
                    # Make this input box active if it was clicked, else make it inactive if it was active
                    if button.get_rect().collidepoint(*event.pos):
                        if not button.is_active():
                            button.toggle()
                            self.update_toggleable(button)
                        button_pressed = True
                    elif button.is_active():
                        button.toggle()
                        self.update_toggleable(button)
                # Already handled mouse click, don't need to check the rest of the buttons
                if button_pressed:
                    continue
                for button in self.buttons:
                    if button.get_rect().collidepoint(*event.pos):
                        button.press()
                        # If it was a speed button clicked, make that button active
                        if isinstance(button, El.SpeedBut):
                            self.update_toggleable(button)
                            # Find the previously active speed button and make it inactive
                            for speed_but in [i for i in self.speed_buttons if i is not button]:
                                if speed_but.is_active():
                                    speed_but.toggle()
                                    self.update_toggleable(speed_but)
                        break
            elif event.type == pg.KEYDOWN:
                tab_pressed = False
                for button in self.input_boxes:
                    # Only send key presses to the active input box
                    if button.is_active():
                        if event.key == pg.K_BACKSPACE:
                            button.handle_backspace()
                        elif event.key == pg.K_RETURN:
                            button.toggle()
                        elif event.key == pg.K_TAB:
                            button.toggle()
                            tab_pressed = True
                        else:
                            button.handle_key(event.unicode)
                        self.update_toggleable(button)
                    # Make active input boxes inactive if tab is pressed
                    elif tab_pressed:
                        button.toggle()
                        self.update_toggleable(button)
                        tab_pressed = False
                        break
                # This allows tab to move from the last input box, to the first input box
                if tab_pressed:
                    self.input_boxes[0].toggle()
                    self.update_toggleable(self.input_boxes[0])
            elif event.type == pg.VIDEOEXPOSE:
                pg.display.flip()

    # Generates a new maze
    def new_maze(self):
        self.solver.set_dimensions(self.rows, self.cols)
        self.maze = self.solver.build_maze()
        self.squares = {}
        self.draw_maze()

    # Draw the text of a given element on the screen
    # @ param element - Element object
    # @ param   color - desired color to render the text with
    def draw_font(self, element, color=None):
        if not color:
            color = self.colors['text']
        text = self.font.render(str(element), True, color)
        rect = text.get_rect(center=element.get_rect().center)
        self.display.blit(text, rect)

    # Displays the maze on the screen
    def draw_maze(self):
        self.solver.clear_solution()
        # Clear any previously drawn mazes from the maze area
        rect = pg.Rect(25, 25, self.safe_width, self.safe_height)
        self.update(El.Element(rect, self.colors['wall']))
        cell_size = floor(min(self.safe_height / self.rows, self.safe_width / self.cols))
        y = 25
        for i in range(self.rows):
            x = 25
            for j in range(self.cols):
                rect = pg.Rect(x, y, cell_size, cell_size)
                if isinstance(self.maze[i][j], int):
                    color = self.colors['wall'] if self.maze[i][j] else self.colors['clear']
                else:
                    color = self.colors['start'] if self.maze[i][j] == 'S' else self.colors['end']
                self.display.fill(color, rect)
                self.squares[(i, j)] = El.Square(rect, color, i, j)
                x += cell_size
            y += cell_size
        pg.display.flip()

    # Updates the display color of all cells contained in the solution
    # @ param solution - list of tuples containing the coordinate pairs of all cells from the solution
    def draw_solution(self, solution):
        for position in solution:
            square = self.squares[position]
            square.set_color(self.colors['solution'])
            self.update(square)

    # Updates an element on the display
    # @ param element - Element object to be updated
    # @ param    fill - whether or not the Element should be filled with its color before being updated
    def update(self, element, fill=True):
        if fill:
            self.display.fill(element.get_color(), element.get_rect())
        pg.display.update(element.get_rect())

    # Updates a ToggleButton object on the display
    # @ param element - ToggleButton object to be updated
    def update_toggleable(self, element):
        self.update(element)
        color = self.colors['wall'] if element.is_active() else None
        self.draw_font(element, color=color)
        self.update(element, fill=False)

    # Updates a Square object on the display
    # @ param i - ordinal row value of the square
    # @ param j - ordinal column value of the square
    def update_square(self, i, j):
        square = self.squares[(i, j)]
        square.set_color(self.colors['path'])
        self.update(square)
        sleep(self.sleep)

    # Updates number of rows in the maze
    # @ param rows - number of desired rows
    def set_rows(self, rows):
        self.rows = rows

    # Updates number of columns in the maze
    # @ param cols - number of desired columns
    def set_cols(self, cols):
        self.cols = cols

    # Set the delay time between updating squares
    # @ param time - number of seconds to set the delay to
    def set_sleep(self, time):
        self.sleep = time


def quit_screen():
    pg.quit()
    exit('\nProgram Quit... Good Bye!')
