import itertools
import os
import string
from platform import system
from random import randint


class Game:
    """
    Base game class.
    Start with start() method.
    Call move() method to make a move.
    Finish when is_open attribute is not None.
    Game result is is_open value: True - won, False - lost.

    Should work the same on each of Linux, Windows and Mac system.
    """
    clear_command = 'cls' if system() == 'Windows' else 'clear'

    def __init__(self, width, height, n_bombs):
        if width > 23 or height > 23:
            raise ValueError('Maximum size is 23x23.')
        self.width = width
        self.height = height
        self.n_bombs = n_bombs
        self.won = None
        self.progress = 0
        self._bombs = self._generate_bombs()
        self._moves = 0
        self._matrix = self._generate_matrix()
        self._full_width = (self.width + 1) * 4 - 3
        self._ruler = self._get_ruler()

    def start(self):
        """Starts the game"""
        self._show(False)

    def win(self):
        """Finishes the game with won status"""
        self._show(True)
        printc(f'You won in {self._moves} moves.', Colors.GREEN)
        self.won = True

    def lose(self):
        """Finishes the game with lost status"""
        self._show(True)
        printc(f'You lost in {self._moves} move.', Colors.RED)
        self.won = False

    def move(self):
        """Asks user for cords and performs user's guess"""
        text = input('Move: ').lower()
        if text in ['stop', 'exit']:
            exit(0)
        if text == 'show':
            self._show(True)
            return
        if text == 'hide':
            self._show(False)
            return
        if text.count('x') != 1:
            printc('Use format like: <W>x<H>', Colors.RED)
            return
        x, y = text.split('x')
        if not x or not y:
            printc('Use format like: <W>x<H>', Colors.RED)
            return
        try:
            self._make_move(string.ascii_lowercase.index(x), string.ascii_lowercase.index(y))
        except ValueError:
            printc('Only letters ale allowed!', Colors.RED)

    def _make_move(self, x, y):
        """Performs user's guess"""
        self._moves += 1
        self._make_island(x, y)
        cell = self.get_cell(x, y)
        if not cell:
            printc(f'Maximum size is {self.width} x {self.height}!', Colors.RED)
            return
        is_bomb = cell.shoot()
        if is_bomb:
            self.lose()
        elif self._check_win():
            self.win()
        else:
            self._show(False)

    def _make_island(self, x, y):
        """Recursively uncovers all 0 and 1 fields nearby x and y"""
        cell = self.get_cell(x, y)
        if cell and not cell.uncovered and cell.reveal():
            for nx, ny in self._get_neighbours(cell.x, cell.y, corners=False):
                self._make_island(nx, ny)

    def _check_win(self):
        """Calculates the progress. Returns won status"""
        total = self.width * self.height
        bombs = sum(1 for cell in itertools.chain(*self._matrix) if isinstance(cell, Bomb))
        uncovered = sum(1 for cell in itertools.chain(*self._matrix) if cell.uncovered)
        self.progress = uncovered / (total - bombs)
        return self.progress == 1

    def _generate_bombs(self):
        """Generates bombs in random positions"""
        return (Bomb(randint(0, self.width-1), randint(0, self.height-1)) for _ in range(self.n_bombs))

    def _show_matrix(self, expose=False):
        """Displays game's matrix in current state to user"""
        print(f'\n{"_" * self._full_width}\n'.join([' | '.join([c.show(expose) for c in [Ruler(i-1)]+r]) for i, r in enumerate([self._ruler] + self._matrix)]))

    def _get_ruler(self):
        """Returns alphabetical ruler"""
        return [Ruler(i) for i in range(self.width)]

    def _get_neighbours(self, start_x=0, start_y=0, corners=True):
        """Generates direct neighbours' x and y positions"""
        for x in range(-1, 2):
            for y in range(-1, 2):
                dest_x, dest_y = start_x + x, start_y + y
                if ((corners and (x or y)) or abs(x + y) == 1) and (dest_x >= 0 and dest_y >= 0):
                    yield dest_x, dest_y

    def _generate_matrix(self):
        """Generates game matrix with bombs"""
        matrix = [[Field(w, h) for w in range(self.width)] for h in range(self.height)]

        for bomb in self._bombs:
            matrix[bomb.y][bomb.x] = bomb
        for h, row in enumerate(matrix):
            for w, field in enumerate(row):
                value = 0
                for nh, nw in self._get_neighbours(w, h, corners=True):
                    try:
                        if isinstance(matrix[nw][nh], Bomb):
                            value += 1
                    except IndexError:
                        pass
                field.value = value

        return matrix

    def _show_stats(self):
        """Shows game statistics"""
        print(f'{"Moves:":{int(2*self._full_width/3)}}{self._moves:>{int(self._full_width/3)}}')
        print(f'{"Progress:":{int(2*self._full_width/3)-1}}{self.progress * 100:>{int(self._full_width/3)}.0f}%')

    def _show(self, expose=False):
        """Displays all game data (name, matrix, stats)"""
        os.system(self.clear_command)
        printc('='*self._full_width)
        printc(f'{"Saper":{int(2*self._full_width/3)}} {"v1.2":>{int(self._full_width/3 - 1)}}', Colors.BLUE)
        printc('='*self._full_width)
        self._show_matrix(expose)
        printc('='*self._full_width)
        self._show_stats()

    def get_cell(self, x, y):
        """Returns cell or None"""
        try:
            return self._matrix[y][x]
        except IndexError:
            return None

    @property
    def is_open(self):
        """Game status"""
        return self.won is None


class Ruler:
    def __init__(self, i):
        self.sign = string.ascii_uppercase[i] if i >= 0 else ' '

    def show(self, *args, **kwargs):
        return color(self.sign, Colors.CYAN)


class Field:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.uncovered = False
        self.value = 0

    def _get_color(self):
        """Returns proper color based on cell value"""
        colors = (Colors.BLUE, Colors.CYAN, Colors.GREEN, Colors.YELLOW, Colors.RED)
        return colors[self.value-1 if self.value <= 4 else 4]

    def show(self, reveal=False):
        """Returns representative sign based on cell value and uncovered status"""
        return color(str(self.value or ' '), self._get_color()) if self.uncovered or reveal else '#'

    def shoot(self, recursive=True):
        """Uncovers cell. Returns False as it is not a bomb"""
        self.uncovered = True
        return False

    def reveal(self):
        """Reveals cell if it is allowed. Returns permission for next searching"""
        if self.value in [0, 1] and not self.uncovered:
            self.uncovered = True
            return True
        return False

    def __str__(self):
        return f'f[{self.x}, {self.y}]'

    def __repr__(self):
        return f'Field({self.x}, {self.y})'


class Bomb(Field):
    def show(self, reveal=False):
        """Returns representative sign based on cell uncovered status"""
        return color('*', Colors.RED) if reveal else '#'

    def shoot(self, *args, **kwargs):
        """Returns True as it is a bomb. Game should stop now"""
        return True

    def reveal(self):
        """Revealing bombs is not allowed. No permission for next searching"""
        return False

    def __str__(self):
        return f'b[{self.x}, {self.y}]'

    def __repr__(self):
        return f'Bomb({self.x}, {self.y})'


class Colors:
    """Colors for colorful output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END_COLOR = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def printc(text, c=''):
    """Prints with color"""
    print(color(text, c))


def color(text, c=''):
    """Returns colorful text"""
    return f'{c}{text}{Colors.END_COLOR}'


if __name__ == '__main__':
    game = Game(20, 10, 30)
    game.start()

    while game.is_open:
        game.move()
