from entity import Effect
import libtcodpy as libtcod
import random


class Battleground(object):

    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.enemies = []
        self.workers = []
        self.tiles = {}
        self.default_tiles()
        self.actionable_tiles = set()
        self.mouse_hovered = []
        self.pending_animations = None
        self.ai_turn = False

    def add_effect(self, effect):
        self.tiles[(effect.x, effect.y)].append_effect(effect)

    def add_enemy(self, enemy):
        self.enemies.append(enemy)
        self.tiles[(enemy.x, enemy.y)].entity = enemy

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
        [e.end_turn() for e in self.enemies]
        self.select_active_worker()

    def hover_mouse(self, x, y):
        hovered_tile = self.tiles.get((x, y))
        if not hovered_tile:
            self.mouse_hovered = []
            return
        if hovered_tile in self.actionable_tiles:
            if not self.workers[0].did_move:
                self.mouse_hovered = self.workers[0].path_movement(x, y)
            else:
                self.mouse_hovered = self.workers[0].path_shoot(x, y)
            color = libtcod.green
        else:
            self.mouse_hovered = [hovered_tile]
            color = libtcod.red
        [t.hover(color) for t in self.mouse_hovered]

    def is_inside(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def move(self, entity, path):
        if len(path) == 0:
            entity.move(entity.x, entity.y)
            return

        def move_animations():
            if len(path) == 0:
                return False
            next_tile = path.pop(0)
            entity.move(next_tile.x, next_tile.y)
            libtcod.sys_sleep_milli(200)
            return True
        self.pending_animations = move_animations

    def process_action(self, x, y, key, mouse):
        if mouse.lbutton_pressed:
            self.select_worker(x, y)
        elif mouse.rbutton_pressed:
            if self.tiles.get((x, y)) in self.actionable_tiles:
                if self.workers[0].did_move:
                    self.shoot(self.workers[0], self.mouse_hovered)
                else:
                    self.move(self.workers[0], self.mouse_hovered)
        elif key.vk == libtcod.KEY_TAB and key.pressed:
            self.select_active_worker()
        elif key.vk == libtcod.KEY_SHIFT and key.pressed:
            self.select_active_worker(True)

    def process_ai_turn(self):
        for e in self.enemies:
            if not e.did_move:
                target = random.choice(tuple(e.reachable_movement_tiles()))
                self.move(e, e.path_movement(target.x, target.y))
                return
            elif not e.did_act:
                target = random.choice(tuple(e.reachable_shoot_tiles()))
                self.shoot(e, e.path_shoot(target.x, target.y))
                return
        self.ai_turn = False

    def remove_entity(self, entity):
        if entity in self.enemies:
            self.enemies.remove(entity)
        if entity in self.workers:
            self.workers.remove(entity)
        self.tiles[(entity.x, entity.y)].entity = None

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
            self.ai_turn = True
            self.end_turn()

    def select_worker(self, x, y):
        t = self.tiles[(x, y)]
        if t and t.entity:
            for i in range(len(self.workers)):
                if t.entity == self.workers[0] and not self.workers[0].did_act:
                    return
                self.workers.append(self.workers.pop(0))

    def shoot(self, entity, path):
        effect = Effect(self, path[0].x, path[0].y, '*')
        self.add_effect(effect)

        def shoot_animations():
            if len(path) == 0:
                effect.remove()
                if not self.ai_turn:
                    self.select_active_worker_or_end_turn()
                return False
            next_tile = path.pop(0)
            effect.move(next_tile.x, next_tile.y)
            entity.shoot(next_tile.x, next_tile.y)
            libtcod.sys_sleep_milli(50)
            return True
        self.pending_animations = shoot_animations

    def show_current_options(self):
        w = self.workers[0]
        if not w.did_move:
            self.actionable_tiles = w.reachable_movement_tiles()
            [t.hover(libtcod.blue) for t in self.actionable_tiles]
        elif not w.did_act:
            self.actionable_tiles = w.reachable_shoot_tiles()
            [t.hover(libtcod.orange) for t in self.actionable_tiles]

    def update(self, x, y, key, mouse):
        self.unhover_all()
        if self.pending_animations and self.pending_animations():
            return
        self.pending_animations = None
        if self.ai_turn:
            self.process_ai_turn()
        else:
            self.process_action(x, y, key, mouse)
            if len(self.workers) > 0:
                self.show_current_options()
        self.hover_mouse(x, y)

    def unhover_all(self):
        [t.unhover() for t in self.actionable_tiles]
        [t.unhover() for t in self.mouse_hovered]


class Tile(object):

    def __init__(self, x, y, char='.', passable=True):
        self.passable = passable
        self.char = char
        self.color = libtcod.Color(50, 50, 150)
        self.bg_color = libtcod.black
        self.bg_original_color = self.bg_color
        self._entity = None
        self.effects = []
        self.x = x
        self.y = y
        self.should_draw = True

    @property
    def entity(self):
        return self._entity

    @entity.setter
    def entity(self, entity):
        self._entity = entity
        self.should_draw = True

    def append_effect(self, effect):
        self.effects.append(effect)
        self.should_draw = True

    def remove_effect(self, effect):
        self.effects.remove(effect)
        self.should_draw = True

    def draw(self, con):
        if not self.should_draw:
            if len(self.effects) > 0:
                print(self.effects, self.x, self.y)
            return
        self.should_draw = False
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
        self.should_draw = True

    def set_entity(self, entity):
        self.entity = entity
        self.should_draw = True

    def unhover(self):
        self.bg_color = self.bg_original_color
        self.should_draw = True
