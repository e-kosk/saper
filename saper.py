import itertools
import os
from random import randint


class Game:
    def __init__(self, width, height, n_bombs):
        self.width = width
        self.height = height
        self.n_bombs = n_bombs
        self.won = None
        self.progress = 0
        self._bombs = self._generate_bombs()
        self._moves = 0
        self._matrix = self._generate_matrix()
        self._full_width = self.width * 4 - 3

    def start(self):
        self._show(True)

    def win(self):
        self._show(True)
        printc(f'You won in {self._moves} moves.', Colors.GREEN)
        self.won = True

    def lose(self):
        self._show(True)
        printc(f'You lost in {self._moves} move.', Colors.RED)
        self.won = False

    def move(self):
        text = input('Move: ').lower()
        if text.count('x') != 1:
            printc('Use format like: <W>x<H>', Colors.RED)
            return
        x, y = text.split('x')
        try:
            self._make_move(int(x)-1, int(y)-1)
        except ValueError:
            printc('Only numbers ale allowed!', Colors.RED)

    def _make_move(self, x, y):
        self._moves += 1
        self._shoot(x, y)
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

    def _shoot(self, x, y):
        cell = self.get_cell(x, y)
        if cell and not cell.uncovered and cell.reveal():
            for nx, ny in cell.get_neighbours():
                self._shoot(nx, ny)

    def _check_win(self):
        self.progress = sum(1 for cell in itertools.chain(*self._matrix) if cell.uncovered) / (self.width * self.height - self.n_bombs)
        return self.progress == 1

    def _generate_bombs(self):
        return (Bomb(randint(0, self.width-1), randint(0, self.height-1)) for _ in range(self.n_bombs))

    def _show_matrix(self, expose=False):
        print(f'\n{"_" * (self.width * 4 - 3)}\n'.join([' | '.join([c.show(expose) for c in r]) for r in self._matrix]))

    def _get_neighbours(self, start_x=0, start_y=0, corners=True):
        for x in range(-1, 2):
            for y in range(-1, 2):
                dest_x, dest_y = start_x + x, start_y + y
                if corners and (x or y) or (x ^ y) and (dest_x >= 0 and dest_y >= 0):
                    yield dest_x, dest_y

    def _generate_matrix(self):
        matrix = [[Field(w, h) for w in range(self.width)] for h in range(self.height)]

        for bomb in self._bombs:
            matrix[bomb.y][bomb.x] = bomb
        for h, row in enumerate(matrix):
            for w, field in enumerate(row):
                value = 0
                for nh, nw in self._get_neighbours(corners=True):
                    try:
                        m_x, m_y = h+nh, w+nw
                        if m_x >= 0 and m_y >= 0 and isinstance(matrix[m_x][m_y], Bomb):
                            value += 1
                    except IndexError:
                        pass
                field.value = value

        return matrix

    def _show_stats(self):
        print(f'{"Moves:":{int(2*self._full_width/3)}}{self._moves:>{int(self._full_width/3)}}')
        print(f'{"Progress:":{int(2*self._full_width/3)}}{self.progress * 100:>{int(self._full_width/3)}.0f}')
        # print(f'{self.progress=} {self.n_bombs=}')
        # print(f'total:{self.width*self.height}')
        # print(f'total-bombs:{self.width*self.height - self.n_bombs}')
        # print(f'uncovered: {sum(1 for cell in itertools.chain(*self._matrix) if cell.uncovered)}')
        # print(f'ratio: {sum(1 for cell in itertools.chain(*self._matrix) if cell.uncovered) / (self.width*self.height - self.n_bombs)}')

    def _show(self, expose=False):
        os.system('clear')
        printc('='*self._full_width)
        printc(f'{"Saper":{int(2*self._full_width/3)}} {"v1.0":>{int(self._full_width/3)}}', Colors.BLUE)
        printc('='*self._full_width)
        self._show_matrix(expose)
        printc('='*self._full_width)
        self._show_stats()

    def get_cell(self, x, y):
        try:
            return self._matrix[y][x]
        except IndexError:
            return None

    @property
    def is_open(self):
        return self.won is None


class Field:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.uncovered = False
        self.value = 0

    def _get_color(self):
        colors = (Colors.BLUE, Colors.CYAN, Colors.GREEN, Colors.YELLOW, Colors.RED)
        return colors[self.value-1 if self.value <= 4 else 4]

    def get_neighbours(self):
        for n in ((self.x-1, self.y), (self.x+1, self.y), (self.x, self.y-1), (self.x, self.y+1)):
            if n[0] >= 0 and n[1] >= 0:
                yield n

    def show(self, reveal=False):
        # return color(str(self.value or ' '), self._get_color()) if (self.uncovered or reveal) else '#'
        return color(str(self.value or ' '), self._get_color()) if self.uncovered else '#'

    def shoot(self, recursive=True):
        self.uncovered = True
        return False

    def reveal(self):
        if self.value in [0, 1]:
            self.uncovered = True
            return True
        return False

    def __str__(self):
        return f'f[{self.x}, {self.y}]'

    def __repr__(self):
        return f'Field({self.x}, {self.y})'


class Bomb(Field):
    def show(self, reveal=False):
        return color('*', Colors.RED) if reveal else '#'

    def shoot(self, *args, **kwargs):
        return True

    def __str__(self):
        return f'b[{self.x}, {self.y}]'

    def __repr__(self):
        return f'Bomb({self.x}, {self.y})'


class Colors:
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
    print(color(text, c))


def color(text, c=''):
    return f'{c}{text}{Colors.END_COLOR}'


if __name__ == '__main__':
    game = Game(20, 10, 30)
    game.start()

    while game.is_open:
        game.move()
