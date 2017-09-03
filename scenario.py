from entity import Entity
from tile import Tile
import random


class Scenario(object):

    def __init__(self, battleground, workers):
        self.bg = battleground
        self.bg.scenario = self
        self.setup_scenario(workers)

    def process_ai_turn(self):
        for e in self.bg.enemies:
            if not e.did_move:
                target = random.choice(tuple(e.reachable_movement_tiles()))
                self.bg.move(e, e.path_movement(target.x, target.y))
                return True
            elif not e.did_act:
                target = random.choice(tuple(e.reachable_shoot_tiles()))
                self.bg.shoot(e, e.path_shoot(target.x, target.y))
                return True
        return False

    def setup_scenario(self, workers):
        self.setup_tiles()
        self.setup_workers(workers)
        self.setup_enemies()

    def setup_enemies(self):
        enemy = Entity(self.bg, 'E', 50, 30)
        self.bg.add_enemy(enemy)

    def setup_tiles(self):
        for x in range(self.bg.width):
            for y in range(self.bg.height):
                if x in [0, self.bg.width - 1] or y in [0, self.bg.height - 1]:
                    # Walls
                    self.bg.tiles[(x, y)] = Tile(x, y, "#", False)
                else:
                    # Floor
                    self.bg.tiles[(x, y)] = Tile(x, y)

    def setup_workers(self, workers):
        for x in range(0, len(workers)):
            w = workers[x]
            (w.x, w.y) = (1, round(self.bg.height/2) - len(workers)*2 + x*4)
            self.bg.add_worker(w)
