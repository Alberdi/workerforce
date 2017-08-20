import libtcodpy as libtcod


class Battleground(object):

    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.workers = []
        self.tiles = {}
        self.default_tiles()
        self.current_move = set()
        self.mouse_hovered = []
        self.pending_animations = None

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

    def end_turn(self):
        [w.end_turn() for w in self.workers]
        self.select_active_worker()

    def hover_mouse(self, x, y):
        hovered_tile = self.tiles.get((x, y))
        if not hovered_tile:
            self.mouse_hovered = []
            return
        if hovered_tile in self.current_move:
            self.mouse_hovered = self.workers[0].movement_path(x, y)
            color = libtcod.green
        else:
            self.mouse_hovered = [hovered_tile]
            color = libtcod.red
        [t.hover(color) for t in self.mouse_hovered]

    def is_inside(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def move(self, x, y):
        t = self.tiles.get((x, y))
        if t in self.current_move:
            def move_animations():
                if len(self.mouse_hovered) == 0:
                    self.select_active_worker_or_end_turn()
                    return False
                next_tile = self.mouse_hovered.pop(0)
                self.workers[0].move(next_tile.x, next_tile.y)
                return True
            self.pending_animations = move_animations

    def process_action(self, x, y, key, mouse):
        if mouse.lbutton_pressed:
            self.select_worker(x, y)
        elif mouse.rbutton_pressed:
            self.move(x, y)
        elif key.vk == libtcod.KEY_TAB and key.pressed:
            self.select_active_worker()
        elif key.vk == libtcod.KEY_SHIFT and key.pressed:
            # Select previous worker
            self.select_active_worker(True)

    def select_active_worker(self, previous=False):
        for i in range(len(self.workers)):
            if previous:
                self.workers.insert(0, self.workers.pop())
            else:
                self.workers.append(self.workers.pop(0))
            if not self.workers[0].did_act:
                return self.workers[0]
        return None

    def select_active_worker_or_end_turn(self):
        if not self.select_active_worker():
            self.end_turn()

    def select_worker(self, x, y):
        t = self.tiles[(x, y)]
        if t and t.entity:
            for i in range(len(self.workers)):
                if t.entity == self.workers[0] and not self.workers[0].did_act:
                    return
                self.workers.append(self.workers.pop(0))

    def show_current_move(self):
        if self.workers.count == 0:
            return
        self.current_move = self.workers[0].movement_reachable_tiles()
        [t.hover(libtcod.blue) for t in self.current_move]

    def update(self, x, y, key, mouse):
        self.unhover_all()
        self.process_action(x, y, key, mouse)
        if self.pending_animations and self.pending_animations():
            return
        self.pending_animations = None
        self.show_current_move()
        self.hover_mouse(x, y)

    def unhover_all(self):
        [t.unhover() for t in self.current_move]
        [t.unhover() for t in self.mouse_hovered]


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

    def is_passable(self):
        return self.passable and self.entity is None

    def hover(self, color=libtcod.blue):
        self.bg_color = color

    def unhover(self):
        self.bg_color = self.bg_original_color
