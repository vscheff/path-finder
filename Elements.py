

# Represents an object on the display screen, superclass for all other display objects
class Element:

    # @ param  rect - pygame Rect object
    # @ param color - tuple containing RGB values of the element's color
    def __init__(self, rect, color):
        self.__rect = rect
        self.__color = color

    def get_rect(self):
        return self.__rect

    def get_color(self):
        return self.__color

    # Updates the color of the element
    # @ param color - tuple containing RGB values of the element's color
    def set_color(self, color):
        self.__color = color


# Represents an individual cell of the maze on the display
class Square(Element):

    # @ param  rect - pygame Rect object
    # @ param color - tuple containing RGB values of the element's color
    # @ param     i - ordinal row value of the cell
    # @ param     j - ordinal column value of the cell
    def __init__(self, rect, color, i, j):
        super().__init__(rect, color)
        self.__i = i
        self.__j = j

    # @ return - tuple containing the coordinate pair of the cell
    def get_position(self):
        return self.__i, self.__j


# Represents a text box on the display
class TextBox(Element):

    # @ param  rect - pygame Rect object
    # @ param color - tuple containing RGB values of the element's color
    # @ param  text - string to display on the screen
    def __init__(self, rect, color, text):
        super().__init__(rect, color)
        self.__text = text

    # Updates the element's display text
    def set_text(self, text):
        self.__text = text

    def __str__(self):
        return self.__text

    def __len__(self):
        return len(self.__text)


# Represents a clickable button on the display
class Button(TextBox):

    # @ param  rect - pygame Rect object
    # @ param color - tuple containing RGB values of the element's color
    # @ param  text - string to display on the screen
    # @ param  func - function that will be executed when the button is clicked
    def __init__(self, rect, color, text, func):
        super().__init__(rect, color, text)
        self.__func = func

    # Executes the callback function with given arguments
    def press(self, *args, **kwargs):
        self.__func(*args, **kwargs)


# Represents an element that toggles between two states
class ToggleButton(Button):

    # @ param           rect - pygame Rect object
    # @ param   active_color - color of the object when it's active
    # @ param inactive_color - color of the object when it's inactive
    # @ param           text - string to display on the screen
    # @ param         active - whether or not this object is active upon creation
    def __init__(self, rect, active_color, inactive_color, text, func, active=False):
        color = active_color if active else inactive_color
        super().__init__(rect, color, text, func)
        self.__active = active
        self.__active_color = active_color
        self.__inactive_color = inactive_color

    def is_active(self):
        return self.__active

    # Toggles the object from from active-to-inactive or vice-versa
    def toggle(self):
        self.__active = not self.__active
        super().set_color(self.__active_color if self.is_active() else self.__inactive_color)


# Represents the buttons for selecting render speed
class SpeedBut(ToggleButton):

    # @ param           rect - pygame Rect object
    # @ param   active_color - color of the object when it's active
    # @ param inactive_color - color of the object when it's inactive
    # @ param           text - string to display on the screen
    # @ param           func - function that will be executed when the button is clicked
    def __init__(self, rect, active_color, inactive_color, text, func, active, speed):
        super().__init__(rect, active_color, inactive_color, text, func, active)
        self.__speed = speed

    # Executes the callback function and toggles the object to active
    def press(self):
        super().press(self.__speed)
        super().toggle()


# Represents the input boxes for selecting number of rows and columns
class InputBox(ToggleButton):

    # @ param           rect - pygame Rect object
    # @ param   active_color - color of the object when it's active
    # @ param inactive_color - color of the object when it's inactive
    # @ param           text - string to display on the screen
    # @ param           func - function that will be executed when the button is clicked
    def __init__(self, rect, active_color, inactive_color, text, func):
        super().__init__(rect, active_color, inactive_color, text, func)

    # Toggles the object from from active-to-inactive or vice-versa
    def toggle(self):
        # If the object was active, ensure its value is in the acceptable range and press it
        if self.is_active():
            # If the box isn't empty, verify its value. Else, set its value to 2
            if val := str(self):
                val = int(val)
                if val < 2:
                    val = 2
                    self.set_text('2')
                elif val > 670:
                    val = 670
                    self.set_text('670')
            else:
                val = 2
                self.set_text('2')
            super().press(val)
        super().toggle()

    # Activates the object if it's clicked while inactive
    def press(self):
        if not self.is_active():
            self.toggle()

    # Handles text input while the object is active
    # @ param character - unicode representation of the key pressed
    def handle_key(self, character: str):
        if len(self) == 3:
            return
        if character.isnumeric():
            self.set_text(str(self) + character)

    # Handles the back space key while the object is active
    def handle_backspace(self):
        self.set_text(str(self)[:-1])
