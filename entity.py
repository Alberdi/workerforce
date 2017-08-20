import itertools
import libtcodpy as libtcod


class Entity(object):

    def __init__(self, battleground, x, y, char, color=libtcod.white):
        self.bg = battleground
        self.char = char
        self.color = color
        self.x = x
        self.y = y
        self.shoot_range = 8
        self.speed = 5
        self.did_act = False
        self.did_move = False

    def end_turn(self):
        self.did_act = False
        self.did_move = False

    def move(self, x, y):
        self.bg.tiles[(self.x, self.y)].entity = None
        (self.x, self.y) = (x, y)
        self.bg.tiles[(x, y)].entity = self
        self.did_move = True

    def path_movement(self, x, y):
        def path_cost(from_x, from_y, to_x, to_y, userdata):
            tile = self.bg.tiles.get((to_x, to_y))
            return 1.0 if tile and tile.is_passable() else 0.0
        path = libtcod.path_new_using_function(self.bg.width, self.bg.height,
                                               path_cost, 0, 0.0)
        libtcod.path_compute(path, self.x, self.y, x, y)
        if libtcod.path_size(path) > self.speed:
            return []
        return self.tiles_for_path(path)

    def path_shoot(self, x, y):
        def path_cost(from_x, from_y, to_x, to_y, userdata):
            tile = self.bg.tiles.get((to_x, to_y))
            return 1.0 if tile and tile.passable else 0.0
        path = libtcod.path_new_using_function(self.bg.width, self.bg.height,
                                               path_cost, 0, 1.0)
        libtcod.path_compute(path, self.x, self.y, x, y)
        if libtcod.path_size(path) > self.shoot_range:
            return []
        return self.tiles_for_path(path)

    def reachable_movement_tiles(self, tiles=None, remaining_speed=None):
        if remaining_speed == 0:
            return tiles
        if not remaining_speed:
            remaining_speed = self.speed
        if not tiles:
            tiles = set()
            tiles.add(self.bg.tiles[(self.x, self.y)])
        for t in tiles.copy():
            for (dx, dy) in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                tile = self.bg.tiles.get((t.x+dx, t.y+dy))
                if tile and tile.is_passable():
                    tiles.add(tile)
        return self.reachable_movement_tiles(tiles, remaining_speed-1)

    def reachable_shoot_tiles(self):
        tiles = set()
        directions = [-1, 0, 1]
        for dx, dy in itertools.product(directions, directions):
            if (dx, dy) == (0, 0):
                continue
            for z in range(1, self.shoot_range+1):
                tile = self.bg.tiles.get((self.x+dx*z, self.y+dy*z))
                if tile and tile.is_passable():
                    tiles.add(tile)
                else:
                    if tile.entity:
                        tiles.add(tile)
                    break
        return tiles

    def shoot(self, x, y):
        self.did_act = True

    def tiles_for_path(self, path):
        tiles = []
        while not libtcod.path_is_empty(path):
            x, y = libtcod.path_walk(path, False)
            tiles.append(self.bg.tiles[(x, y)])
        return tiles


class Effect(Entity):

    def move(self, x, y):
        self.bg.tiles[(self.x, self.y)].effects.remove(self)
        (self.x, self.y) = (x, y)
        self.bg.tiles[(x, y)].effects.append(self)

    def remove(self):
        self.bg.tiles[(self.x, self.y)].effects.remove(self)
