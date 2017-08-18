import libtcodpy as libtcod


class Entity(object):

    def __init__(self, battleground, x, y, char, color=libtcod.white):
        self.bg = battleground
        self.char = char
        self.color = color
        self.x = x
        self.y = y
        self.speed = 5
        battleground.add_worker(self)

    def move(self, x, y):
        self.bg.tiles[(self.x, self.y)].entity = None
        (self.x, self.y) = (x, y)
        self.bg.tiles[(x, y)].entity = self

    def movement_reachable_tiles(self, tiles=None, remaining_speed=None):
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
                if tile and tile.passable:
                    tiles.add(tile)
        return self.movement_reachable_tiles(tiles, remaining_speed-1)
