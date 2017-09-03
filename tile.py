import libtcodpy as libtcod


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
