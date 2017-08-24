from battleground import Battleground
from entity import Entity
import libtcodpy as libtcod
import textwrap

BG_WIDTH = 60
BG_HEIGHT = 43
PANEL_WIDTH = 16
PANEL_HEIGHT = BG_HEIGHT
INFO_WIDTH = BG_WIDTH
INFO_HEIGHT = 1
MSG_WIDTH = BG_WIDTH - 2
MSG_HEIGHT = 6
SCREEN_WIDTH = BG_WIDTH + PANEL_WIDTH * 2
SCREEN_HEIGHT = BG_HEIGHT + INFO_HEIGHT + MSG_HEIGHT + 1

BG_OFFSET_X = PANEL_WIDTH
BG_OFFSET_Y = MSG_HEIGHT + 1
PANEL_OFFSET_X = 0
PANEL_OFFSET_Y = BG_OFFSET_Y + 3
MSG_OFFSET_X = BG_OFFSET_X
MSG_OFFSET_Y = 1
INFO_OFFSET_X = PANEL_WIDTH + 1
INFO_OFFSET_Y = BG_OFFSET_Y + BG_HEIGHT


class Window(object):

    def __init__(self, battleground):
        self.bg = battleground
        libtcod.console_set_custom_font('arial10x10.png',
                                        libtcod.FONT_TYPE_GREYSCALE |
                                        libtcod.FONT_LAYOUT_TCOD)
        libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Worker Force')

        self.con_root = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.con_bg = libtcod.console_new(BG_WIDTH, BG_HEIGHT)
        self.con_info = libtcod.console_new(INFO_WIDTH, INFO_HEIGHT)
        self.con_msgs = libtcod.console_new(MSG_WIDTH, MSG_HEIGHT)
        self.con_panels = [libtcod.console_new(PANEL_WIDTH, PANEL_HEIGHT),
                           libtcod.console_new(PANEL_WIDTH, PANEL_HEIGHT)]

        self.game_msgs = []
        self.game_over = False

    def message(self, new_msg, color=libtcod.white):
        # split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
        for line in new_msg_lines:
            # if the buffer is full, remove the first line to make room
            if len(self.game_msgs) == MSG_HEIGHT:
                del self.game_msgs[0]
                libtcod.console_clear(self.con_msgs)
            # add the new line as a tuple, with the text and the color
            self.game_msgs.append((line, color))

    def loop(self):
        key = libtcod.Key()
        mouse = libtcod.Mouse()
        while not self.game_over:
            libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, mouse)
            if key.vk == libtcod.KEY_ESCAPE:
                return None
            (x, y) = (mouse.cx - BG_OFFSET_X, mouse.cy - BG_OFFSET_Y)
            self.bg.update(x, y, key, mouse)
            self.render_all(x, y)

    def render_all(self, x, y):
        self.bg.draw(self.con_bg)
        self.render_info(x, y)
        self.render_msgs()
        self.render_panels()
        libtcod.console_blit(self.con_bg, 0, 0, BG_WIDTH, BG_HEIGHT,
                             self.con_root, BG_OFFSET_X, BG_OFFSET_Y)
        for i in [0, 1]:
            libtcod.console_blit(self.con_panels[i], 0, 0, PANEL_WIDTH,
                                 PANEL_HEIGHT, self.con_root,
                                 (PANEL_WIDTH + BG_WIDTH) * i, PANEL_OFFSET_Y)
        libtcod.console_blit(self.con_info, 0, 0, MSG_WIDTH,
                             MSG_HEIGHT, self.con_root,
                             INFO_OFFSET_X, INFO_OFFSET_Y)
        libtcod.console_blit(self.con_msgs, 0, 0, MSG_WIDTH,
                             MSG_HEIGHT, self.con_root,
                             MSG_OFFSET_X, MSG_OFFSET_Y)
        libtcod.console_blit(
            self.con_root, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
        libtcod.console_flush()

    def render_info(self, x, y):
        libtcod.console_print(self.con_info, 0, 0, " " * INFO_WIDTH)
        if self.bg.is_inside(x, y):
            libtcod.console_set_default_foreground(
                self.con_info, libtcod.white)
            libtcod.console_print(
                self.con_info, INFO_WIDTH - 7, 0, "%02d/%02d" % (x, y))

    def render_msgs(self):
        y = 0
        for (line, color) in self.game_msgs:
            libtcod.console_set_default_foreground(self.con_msgs, color)
            libtcod.console_print(self.con_msgs, 0, y, line)
            y += 1

    def render_panels(self):
        bar_length = 11
        bar_offset_x = 4
        for i in [0, 1]:
            self.render_side_panel(i, bar_length, bar_offset_x)

    def render_side_panel(self, i, bar_length, bar_offset_x):
        pass

    def render_side_panel_clear(self, i, bar_length=11, bar_offset_x=4):
        libtcod.console_set_default_background(
            self.con_panels[i], libtcod.black)
        libtcod.console_rect(self.con_panels[i], bar_offset_x - 1, 0,
                             bar_length + 1, 40, True, libtcod.BKGND_SET)


if __name__ == "__main__":
    libtcod.sys_set_fps(30)
    bg = Battleground(BG_WIDTH, BG_HEIGHT)
    worker = Entity(bg, 30, 15, '@')
    bg.add_worker(worker)
    enemy = Entity(bg, 50, 20, 'E')
    bg.add_enemy(enemy)
    enemy = Entity(bg, 50, 30, 'E')
    bg.add_enemy(enemy)
    enemy = Entity(bg, 50, 35, 'E')
    bg.add_enemy(enemy)
    window = Window(bg)
    window.loop()
