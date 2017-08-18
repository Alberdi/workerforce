import libtcodpy as libtcod
import os


class Battleground(object):

    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.workers = []
        self.tiles = {}
        self.default_tiles()
        self.current_move = set()
        self.mouse_hovered = None

    def add_worker(self, worker):
        self.workers.append(worker)
        self.tiles[(worker.x, worker.y)].entity = worker

    def default_tiles(self):
        for x in range(self.width):
            for y in range(self.height):
                if x in [0, self.width - 1] or y in [0, self.height - 1]:
                    # Walls
                    self.tiles[(x, y)] = Tile(x, y, "#", False)
                else:
                    # Floor
                    self.tiles[(x, y)] = Tile(x, y)

    def draw(self, con):
        for pos in self.tiles:
            self.tiles[pos].draw(con)

    def hover_mouse(self, x, y):
        if self.mouse_hovered and self.mouse_hovered not in self.current_move:
            self.mouse_hovered.unhover()
        self.mouse_hovered = self.tiles.get((x, y))
        if self.mouse_hovered:
            if self.mouse_hovered in self.current_move:
                color = libtcod.green
            else:
                color = libtcod.red
            self.mouse_hovered.hover(color)

    def is_inside(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def show_current_move(self):
        [t.unhover() for t in self.current_move]
        if self.workers.count == 0:
            return
        self.current_move = self.workers[0].movement_reachable_tiles()
        [t.hover(libtcod.blue) for t in self.current_move]

    def move(self, x, y):
        t = self.tiles.get((x, y))
        if t in self.current_move:
            self.workers[0].move(x, y)


class Tile(object):

    def __init__(self, x, y, char='.', passable=True):
        self.passable = passable
        self.char = char
        self.color = libtcod.Color(50, 50, 150)
        self.bg_original_color = libtcod.black
        self.bg_color = libtcod.black
        self.entity = None
        self.effects = []
        self.x = x
        self.y = y

    def get_char(self, x, y):
        return self.char

    def draw(self, con):
        if len(self.effects) > 0 and self.effects[-1].char:
            drawable = self.effects[-1]
        elif self.entity:
            drawable = self.entity
        else:
            drawable = self
        libtcod.console_put_char_ex(con, self.x, self.y, drawable.char,
                                    drawable.color, self.bg_color)

    def hover(self, color=libtcod.blue):
        self.bg_color = color

    def unhover(self):
        self.bg_color = self.bg_original_color
