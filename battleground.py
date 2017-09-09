from entity import Effect
import libtcodpy as libtcod


class Battleground(object):

    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.enemies = []
        self.workers = []
        self.tiles = {}
        self.actionable_tiles = set()
        self.mouse_hovered = []
        self.animations = None
        self.animations_wait = 0
        self.scenario = None
        self.ai_turn = False

    def add_effect(self, effect):
        self.tiles[(effect.x, effect.y)].append_effect(effect)

    def add_enemy(self, enemy):
        self.enemies.append(enemy)
        self.tiles[(enemy.x, enemy.y)].entity = enemy

    def add_worker(self, worker):
        self.workers.append(worker)
        self.tiles[(worker.x, worker.y)].entity = worker

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
        if not self.animations and hovered_tile in self.actionable_tiles:
            if not self.workers[0].did_move:
                self.mouse_hovered = self.workers[0].movement_path_to(x, y)
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
            self.animations_wait = 0.2
            return True
        self.animations = move_animations

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
        effect = Effect(self, '*', path[0].x, path[0].y)
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
            self.animations_wait = 0.05
            return True
        self.animations = shoot_animations

    def show_current_options(self):
        w = self.workers[0]
        if not w.did_move:
            self.actionable_tiles = w.reachable_movement_tiles()
            [t.hover(libtcod.blue) for t in self.actionable_tiles]
        elif not w.did_act:
            self.actionable_tiles = w.reachable_shoot_tiles()
            [t.hover(libtcod.orange) for t in self.actionable_tiles]
        else:
            self.actionable_tiles = set()

    def update(self, x, y, key, mouse):
        self.unhover_all()
        if self.animations:
            self.animations_wait =\
                self.animations_wait - libtcod.sys_get_last_frame_length()
            if self.animations_wait <= 0:
                if not self.animations():
                    self.animations = None
            return
        if self.ai_turn:
            self.ai_turn = self.scenario.process_ai_turn()
        else:
            if len(self.workers) > 0:
                self.show_current_options()
            self.hover_mouse(x, y)
            self.process_action(x, y, key, mouse)

    def unhover_all(self):
        [t.unhover() for t in self.actionable_tiles]
        [t.unhover() for t in self.mouse_hovered]
