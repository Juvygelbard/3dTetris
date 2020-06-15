from engine import GUI, GUIText, GUIRect, Color


class Menu(GUI):
    # returns next menu or None for no menu
    def key_press(self, key):
        raise NotImplementedError


class Pause(Menu):
    def draw(self, canvas, **kwargs):
        w, h = canvas.winfo_width(), canvas.winfo_height()
        wf, hf = 240, 80
        frame = GUIRect((w - wf) * 0.5, (h - hf) * 0.5, wf, hf, Color(250, 150, 150))
        frame.draw(canvas, **kwargs)
        text = GUIText("Pause", w * 0.5, h * 0.5, 50, Color(100, 100, 100))
        text.draw(canvas, **kwargs)

    def key_press(self, key):
        if key == 'p':
            return None
        else:
            return self


class GameOver(Menu):
    def __init__(self, next_menu):
        self._next_menu = next_menu

    def draw(self, canvas, **kwargs):
        w, h = canvas.winfo_width(), canvas.winfo_height()
        wf, hf = 450, 110
        frame = GUIRect((w - wf) * 0.5, (h - hf) * 0.5, wf, hf, Color(250, 150, 150))
        frame.draw(canvas, **kwargs)
        head = GUIText("Game Over", w * 0.5, (h - hf) * 0.5 + 35, 40, Color(100, 100, 100))
        head.draw(canvas, **kwargs)
        cont = GUIText("<ENTER> to continue...", w * 0.5, (h - hf) * 0.5 + 85, 15, Color(100, 100, 100))
        cont.draw(canvas, **kwargs)

    def key_press(self, key):
        if ord(key) == 13:
            return self._next_menu
        return self


class NewHighScore(Menu):
    def __init__(self, hs_menu, score, table):
        self._score = score
        self._table = table
        self._next_menu = hs_menu
        self._text = ""

    def draw(self, canvas, **kwargs):
        w, h = canvas.winfo_width(), canvas.winfo_height()
        fw, fh = 500, 200
        frame = GUIRect((w - fw) * 0.5, (h - fh) * 0.5, fw, fh, Color(250, 150, 150))
        frame.draw(canvas, **kwargs)

        head_space = 35
        head = GUIText("New High Score!", w * 0.5, (h - fh) * 0.5 + head_space, 30, Color(100, 100, 100))
        head.draw(canvas, **kwargs)

        time_l = GUIText(self._text, w * 0.5, h * 0.5, 20, Color(100, 100, 100), GUIText.CENTER)
        time_l.draw(canvas, **kwargs)

        cont_space = 35
        cont = GUIText("Enter your name and then <ENTER> to continue...", w * 0.5, (h + fh) * 0.5 - cont_space, 15, Color(100, 100, 100))
        cont.draw(canvas, **kwargs)

    def key_press(self, key):
        if ord(key) == 13:
            print("ENTER")
            self._table.add_score(self._score, self._text)
            return self._next_menu

        if ('A' <= key <= 'Z' or
            'a' <= key <= 'z' or
            '0' <= key <= '9' or
            key == " ") and len(self._text) <= 10:
            self._text += key

        if key == '\b':
            self._text = self._text[:-1]
        return self


class HighScore(Menu):
    def __init__(self, table, next_menu):
        self._next_menu = next_menu
        self._table = table

    def draw(self, canvas, **kwargs):
        w, h = canvas.winfo_width(), canvas.winfo_height()
        fw, fh = 500, 400
        frame = GUIRect((w - fw) * 0.5, (h - fh) * 0.5, fw, fh, Color(250, 150, 150))
        frame.draw(canvas, **kwargs)

        head_space = 35
        head = GUIText("High Scores", w * 0.5, (h - fh) * 0.5 + head_space, 30, Color(100, 100, 100))
        head.draw(canvas, **kwargs)

        table_space = 205
        rank = "\n".join(str(i) for i in range(1, 11))
        names = "\n".join(self._table.names())
        time = "\n".join(self._table.times())
        score = "\n".join(str(s) for s in self._table.scores())
        rank_l = GUIText(rank, (w - fw) * 0.5 + 30, (h - fh) * 0.5 + table_space, 18, Color(100, 100, 100), GUIText.RIGHT)
        names_l = GUIText(names, (w - fw) * 0.5 + 115, (h - fh) * 0.5 + table_space, 18, Color(100, 100, 100), GUIText.LEFT)
        time_l = GUIText(time, w * 0.5, (h - fh) * 0.5 + table_space, 18, Color(100, 100, 100), GUIText.CENTER)
        score_l = GUIText(score, (w + fw) * 0.5 - 30, (h - fh) * 0.5 + table_space, 18, Color(100, 100, 100), GUIText.RIGHT)
        rank_l.draw(canvas, **kwargs)
        names_l.draw(canvas, **kwargs)
        time_l.draw(canvas, **kwargs)
        score_l.draw(canvas, **kwargs)

        cont_space = 35
        cont = GUIText("<ENTER> to continue...", w * 0.5, (h + fh) * 0.5 - cont_space, 15, Color(100, 100, 100))
        cont.draw(canvas, **kwargs)

    def key_press(self, key):
        if ord(key) == 13:
            return self._next_menu
        return self


class StartGame(Menu):
    LEVEL_STR = ("easy", "medium", "hard")

    def __init__(self, game):
        self._game = game
        self._help = Help(self)

    def draw(self, canvas, **kwargs):
        w, h = canvas.winfo_width(), canvas.winfo_height()
        fw, fh = 440, 305
        frame = GUIRect((w - fw) * 0.5, (h - fh) * 0.5, fw, fh, Color(250, 150, 150))
        frame.draw(canvas, **kwargs)
        head = GUIText("Welcome to 3d Tetris!", w * 0.5, (h - fh) * 0.5 + 30, 30, Color(100, 100, 100))
        head.draw(canvas, **kwargs)
        text = GUIText("Current game level is %d (%s).\n\n"
                       "<S> Start the game\n"
                       "<1> Change game level to 1\n"
                       "<2> Change game level to 2\n"
                       "<3> Change game level to 3\n"
                       "<H> Display help (please read if\n"
                       "       it's your first time playing!)"
                       % (self._game.level()+1, StartGame.LEVEL_STR[self._game.level()])
                       ,w * 0.5, (h - fh) * 0.5 + 180, 18, Color(100, 100, 100))
        text.draw(canvas, **kwargs)

    def key_press(self, key):
        if key == 's':
            self._game.reset_game()
            return None
        if key == '1':
            self._game.set_level(0)
        if key == '2':
            self._game.set_level(1)
        if key == '3':
            self._game.set_level(2)
        if key == 'h':
            return self._help
        return self


class Help(Menu):
    def __init__(self, next_menu):
        self._next_menu = next_menu

    def draw(self, canvas, **kwargs):
        w, h = canvas.winfo_width(), canvas.winfo_height()
        fw, fh = 500, 650
        frame = GUIRect((w - fw) * 0.5, (h - fh) * 0.5, fw, fh, Color(250, 150, 150))
        frame.draw(canvas, **kwargs)
        head = GUIText("Help", w * 0.5, (h - fh) * 0.5 + 30, 30, Color(100, 100, 100))
        head.draw(canvas, **kwargs)
        text = GUIText("Welcome to 3d Tetris! This game is all about\n"
                       "procrastination, so please don't play it if there is\n"
                       "something you really needs to get done.\n\n"
                       
                       "If somehow this is your first Tetris experience\n"
                       "then you're probably an alien, so welcome to earth!\n"
                       "The game rules are simple: you earn points by filling\n"
                       "up surfaces. When a surface is completely full, the\n"
                       "blocks of this surface will disappear, and you will earn\n"
                       "points. If you fill up 2 or more surfaces with a single\n"
                       "block, you'll get even more points. The game difficulty\n"
                       "level also affects the amount of points you'll get.\n\n"
                       
                       "> Use the arrow keys to move blocks around.\n"
                       "> Use the w, s keys to rotate blocks in the pitch axis.\n"
                       "> Use the a, d keys to rotate blocks in the yaw axis.\n"
                       "> Use the q, e keys to rotate blocks in the roll axis.\n"
                       "> Use the z, x keys to rotate the cameras.\n"
                       "> Use the space key to speed up the falling blocks\n"
                       "> Use the p key to pause the game.\n\n"
                       
                       "TIP1: motion and rotation are always relative to\n"
                       "current camera angle.\n"
                       "TIP2: rotate the camera A LOT, it's really useful!\n\n"
                       
                       "<ENTER> to return..."
                       , w * 0.5, (h + fh) * 0.5 - 300, 14, Color(100, 100, 100))
        text.draw(canvas, **kwargs)

    def key_press(self, key):
        if ord(key) == 13:
            return self._next_menu
        return self