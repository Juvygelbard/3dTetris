import sys, tkinter
from time import process_time
from random import choice, shuffle
from engine import Engine, Surface, HBox, HGrid
from assets import SHAPES, COLORS
from highscore import HighScoreTable
from menu import *
from utils import *


class Game:
    BORAD_SIZE = 4
    BOARD_HEIGHT = 14

    LEVEL_TICK_TIME = (0.7, 0.5, 0.2)
    LEVEL_SCORE_FACT = (1, 2, 3)

    CAM_DIST = 22
    CAM_HEIGHT = 18
    CAM_PITCH = 0.5

    HS_FILE = "hs.csv"

    MOVE_MAP = ((-1, 0), (0, -1), (1, 0), (0, 1))
    PITCH_ROLL_MAP = ((1, -1), (0, -1), (1, 1), (0, 1))

    def __init__(self, width, height):
        self.init_screen(width, height)
        self.init_control()
        self.init_board()
        self.init_game()
        self.init_menus()

    def init_screen(self, width, height):
        # tkinter stuff
        self._root = tkinter.Tk()
        self._root.minsize(width, height)
        self._root.title("Tetris, FPS: 0")
        self._frame = tkinter.Frame()
        self._frame.pack(fill=tkinter.BOTH, expand=True)
        self._canvas = tkinter.Canvas(self._frame)
        self._canvas.pack(fill=tkinter.BOTH, expand=True)

        # engine stuff
        self._engine = Engine(self._canvas)

        # cam stuff
        self._board_center_X = np.floor(Game.BORAD_SIZE * 0.5)
        self._board_center_Z = np.floor(Game.BORAD_SIZE * 0.5)
        self._dir = 0
        self.set_cam_angle(0.15)
        self._target_cam_angle = self._cam_angle
        self._interactive = True
        self._t = 0.0

    def init_control(self):
        self._mouse_x = np.nan
        self._mouse_y = np.nan
        self._root.bind('<B1-Motion>', self.click_motion_event)
        self._root.bind('<ButtonRelease-1>', self.click_release_event)
        self._root.bind('<KeyPress>', self.key_press)
        self._root.bind('<KeyRelease>', self.key_release)

    def init_board(self):
        # build board
        self._board = np.zeros((Game.BORAD_SIZE, Game.BOARD_HEIGHT, Game.BORAD_SIZE))
        self._elements = list()

        # build floor
        color = Color(120, 120, 120)
        self._floor = list()
        for i in range(Game.BORAD_SIZE):
            self._floor.append(list())
            for j in range(Game.BORAD_SIZE):
                pos = Position(i + 0.5, -0.5, j + 0.5, 0.0, 0.0, 0.0)
                self._floor[i].append(Surface(pos, 1.0, 1.0, color))

        # build walls
        self._walls = HBox(Position(Game.BORAD_SIZE * 0.5, Game.BOARD_HEIGHT * 0.5 - 0.5, Game.BORAD_SIZE * 0.5, 0, 0, 0), Game.BORAD_SIZE, Game.BOARD_HEIGHT, Game.BORAD_SIZE)
        self._ceiling = HGrid(Position(Game.BORAD_SIZE * 0.5 + 0.5, Game.BOARD_HEIGHT-0.5, Game.BORAD_SIZE * 0.5 + 0.5, 0, 0, 0), 1.0, 1.0, Game.BORAD_SIZE+1, Game.BORAD_SIZE+1)

    def init_game(self):
        self.set_level(1)
        self._fast = False
        self._running = False
        self._highscore = HighScoreTable(Game.HS_FILE)

    def init_menus(self):
        self._pause_menu = Pause()
        self._start_menu = StartGame(self)
        self._hs_menu = HighScore(self._highscore, self._start_menu)
        self._show_menu = True
        self._menu = self._start_menu

    def reset_game(self):
        self._board = np.zeros((Game.BORAD_SIZE, Game.BOARD_HEIGHT, Game.BORAD_SIZE))
        self._elements.clear()
        self._score = 0
        self.generate_shape()
        self._running = True

    def click_motion_event(self, event):
        if not np.isnan(self._mouse_x) and not np.isnan(self._mouse_y):
            dy = (self._mouse_x - event.x) * self._t * np.pi * 0.02
            dp = (self._mouse_y - event.y) * self._t * np.pi * 0.02
            self._engine.move_cam(0.0, 0.0, 0.0, dy, dp, 0.0)
        self._mouse_x = event.x
        self._mouse_y = event.y

    def click_release_event(self, event):
        self._mouse_x = np.nan
        self._mouse_y = np.nan

    def key_press(self, key):
        # menu keys
        if self._show_menu:
            self._menu = self._menu.key_press(key.char)
            self._show_menu = self._menu is not None
            return

        # show menu keys
        if key.char == 'p':
            self._menu = self._pause_menu
            self._show_menu = True

        # cam keys
        if key.char == 'z':
            self.rotate_cam(-1)
        elif key.char == 'c':
            self.rotate_cam(1)

        if not self._interactive:
            return

        # game translation keys
        if key.keysym == "space":
            self._fast = True
        if key.keysym == "Left":
            dX, dZ = Game.MOVE_MAP[(self._dir + 0) % 4]
            self.move(dX, 0, dZ)
        if key.keysym == "Down":
            dX, dZ = Game.MOVE_MAP[(self._dir + 1) % 4]
            self.move(dX, 0, dZ)
        if key.keysym == "Right":
            dX, dZ = Game.MOVE_MAP[(self._dir + 2) % 4]
            self.move(dX, 0, dZ)
        if key.keysym == "Up":
            dX, dZ = Game.MOVE_MAP[(self._dir + 3) % 4]
            self.move(dX, 0, dZ)

        # game rotation keys
        elif key.char == 's':
            ax, dr = Game.PITCH_ROLL_MAP[(self._dir + 0) % 4]
            self.rotate(ax, dr)
        if key.char == 'w':
            ax, dr = Game.PITCH_ROLL_MAP[(self._dir + 2) % 4]
            self.rotate(ax, dr)
        elif key.char == 'a':
            self.rotate(2, -1)
        elif key.char == 'd':
            self.rotate(2, 1)
        if key.char == 'q':
            ax, dr = Game.PITCH_ROLL_MAP[(self._dir + 3) % 4]
            self.rotate(ax, dr)
        elif key.char == 'e':
            ax, dr = Game.PITCH_ROLL_MAP[(self._dir + 1) % 4]
            self.rotate(ax, dr)

        # if key.char == 'w':
        #     self._engine.move_cam_relative(0.0, 0.0, 0.2)
        # elif key.char == 's':
        #     self._engine.move_cam_relative(0.0, 0.0, -0.2)
        # elif key.char == 'a':
        #     self._engine.move_cam_relative(-0.2, 0.0, 0.0)
        # elif key.char == 'd':
        #     self._engine.move_cam_relative(0.2, 0.0, 0.0)

    def key_release(self, key):
        if key.keysym == "space":
            self._fast = False

    def set_cam_angle(self, a):
        cam_X = Game.CAM_DIST * np.cos(a - 0.5 * np.pi) + self._board_center_X
        cam_Z = Game.CAM_DIST * np.sin(a - 0.5 * np.pi) + self._board_center_Z
        self._engine.set_cam(cam_X, Game.CAM_HEIGHT, cam_Z, -a, Game.CAM_PITCH, 0.0)
        self._cam_angle = a

    def animate_cam(self, t):
        if abs(self._cam_angle - self._target_cam_angle) < 0.05:
            self._dir %= 4
            final_angle = self._dir * np.pi * 0.5 + 0.1
            self._cam_angle = final_angle
            self._target_cam_angle = final_angle
            self._interactive = True
        else:
            temp_angle = self._cam_angle + (self._target_cam_angle - self._cam_angle) * t * np.pi * 1.0
            self.set_cam_angle(temp_angle)

    def rotate_cam(self, diff_idx):
        self._interactive = False
        self._dir += diff_idx
        self._target_cam_angle = self._dir * np.pi * 0.5 + 0.1

    def set_level(self, level):
        self._level = level
        self._tick_time = Game.LEVEL_TICK_TIME[self._level]
        self._score_fact = Game.LEVEL_SCORE_FACT[self._level]

    def level(self):
        return self._level

    def render_elements(self):
        for e in self._elements:
            # render only visible sides
            D = e.Y > 0 and self._board[e.X, e.Y - 1, e.Z] == 0
            U = e.Y == Game.BOARD_HEIGHT - 1 or self._board[e.X, e.Y + 1, e.Z] == 0
            N = e.Z == Game.BORAD_SIZE - 1 or self._board[e.X, e.Y, e.Z + 1] == 0
            S = e.Z == 0 or self._board[e.X, e.Y, e.Z - 1] == 0
            E = e.X == Game.BORAD_SIZE - 1 or self._board[e.X + 1, e.Y, e.Z] == 0
            W = e.X == 0 or self._board[e.X - 1, e.Y, e.Z] == 0

            # shade shape projection on floor
            shadow = 1.0
            for x, y, z in self._shape.iterate():
                if x == e.X and z == e.Z:
                    shadow = 0.5
                    break
            self._engine.render(e.box, DOWN=D, UP=U, NORTH=N, SOUTH=S, EAST=E, WEST=W, SUP=shadow)

    def render_floor(self):
        for i in range(Game.BORAD_SIZE):
            for j in range(Game.BORAD_SIZE):
                shadow = 1.0
                if self._running:
                    for x, y, z in self._shape.iterate():
                        if x == i and z == j:
                            shadow = 0.5
                            break
                self._engine.render(self._floor[i][j], S=shadow)

        self._engine.render(self._walls)
        self._engine.render(self._ceiling)

    def render_gui(self):
        # display score
        if self._running:
            frame = GUIRect(50, 35, 100, 30, Color(200, 200, 200))
            self._engine.render_gui(frame)
            text = GUIText("Score: %d" % self._score, 100, 50, 14, Color(0, 0, 0))
            self._engine.render_gui(text)

        # display menus
        if self._show_menu:
            self._engine.render_gui(self._menu)

    def rotate(self, axis, n):
        self.remove_shape()
        self._shape.rotate(axis, n)
        can = True
        for x, y, z in self._shape.iterate():
            if not Game.in_board(x, y, z) or self._board[x, y, z] == 1:
                self._shape.rotate(axis, -n)
                can = False
                break
        self.add_shape()
        return can

    @staticmethod
    def in_board(x, y, z):
        return 0 <= x < Game.BORAD_SIZE and \
               0 <= y < Game.BOARD_HEIGHT and \
               0 <= z < Game.BORAD_SIZE

    def move(self, dX, dY, dZ):
        self.remove_shape()
        self._shape.move(dX, dY, dZ)
        can = True
        for x, y, z in self._shape.iterate():
            if not Game.in_board(x, y, z) or self._board[x, y, z] == 1:
                self._shape.move(-dX, -dY, -dZ)
                can = False
                break
        self.add_shape()
        return can

    def add_shape(self):
        for x, y, z in self._shape.iterate():
            if Game.in_board(x, y, z):
                self._board[x, y, z] = 1

    def remove_shape(self):
        for x, y, z in self._shape.iterate():
            if Game.in_board(x, y, z):
                self._board[x, y, z] = 0

    def update_score(self):
        # find which surfaces we should remove
        remove = list()
        surface = Game.BORAD_SIZE * Game.BORAD_SIZE
        for s in range(Game.BOARD_HEIGHT):
            if np.sum(self._board[:, s, :]) == surface:
                remove.append(s)

        # update score
        n = len(remove)
        self._score += self._score_fact * n * n

        # remove surfaces
        while remove:
            s = remove.pop(0)
            for x, y, z in product_idx((Game.BORAD_SIZE, Game.BOARD_HEIGHT - s - 1, Game.BORAD_SIZE)):
                self._board[x, s + y, z] = self._board[x, s + y + 1, z]
            self._board[:, Game.BOARD_HEIGHT - 1, :] = np.zeros((Game.BORAD_SIZE, Game.BORAD_SIZE))
            n_elements = list()
            for e in self._elements:
                if e.Y != s:
                    if e.Y > s:
                        e.move(0, -1, 0)
                    n_elements.append(e)
            self._elements = n_elements
            for i in range(len(remove)):
                remove[i] -= 1

    # find a shape that can fit current head space
    def generate_shape(self):
        color = choice(COLORS)
        shapes = list(SHAPES)
        shuffle(shapes)
        while shapes:
            s = shapes.pop()
            s_y = Game.BOARD_HEIGHT - s.shape[1]
            self._shape = Shape(s, color, 1, s_y, 1)
            collision = False
            for x, y, z in self._shape.iterate():
                if not Game.in_board(x, y, z) or self._board[x, y, z] == 1:
                    collision = True
                    break
            if collision:
                continue
            self.add_shape()
            self._elements += self._shape.elements()
            return True
        return False

    def tick(self):
        if not self.move(0, -1, 0):
            self.update_score()
            if not self.generate_shape():
                next_menu = NewHighScore(self._hs_menu, self._score, self._highscore) \
                    if self._highscore.is_high_score(self._score) \
                    else self._hs_menu
                self._menu = GameOver(next_menu)
                self._show_menu = True
                self._running = False

    def start(self):
        fps = 0
        t_acc = 0.0
        t_tick = 0.0
        t_p = process_time()
        while True:
            # handle timing
            t_c = process_time()
            self._t = t_c - t_p
            t_p = t_c

            # frame count
            t_tick += self._t
            if t_acc >= 1.0:
                self._root.title("Tetris, FPS: %d" % fps)
                t_acc = 0.0
                fps = 0

            # tick count
            t_acc += self._t
            tt_fact = 0.1 if self._fast else 1
            if t_tick >= self._tick_time * tt_fact:
                if not self._show_menu:
                    self.tick()
                t_tick = 0.0

            # draw stuff
            try:
                self.render_elements()
                self.render_floor()
                self.render_gui()
                self.animate_cam(self._t)

                self._engine.draw()
                self._root.update()
            except tkinter.TclError:
                break
            fps += 1


def run():
    game = Game(550, 700)
    game.start()
    return 0

if __name__ == "__main__":
    sys.exit(run())
