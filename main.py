from __future__ import division
import collections
import os
import time
import sys
import pygame
from callbreak_card import CallBreak, GameTurn, Player

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
FPS = 30
clock = pygame.time.Clock()

class MenuItem(pygame.font.Font):
    def __init__(self, text, font=None, font_size=30,
                 font_color=BLACK, (pos_x, pos_y)=(0, 0)):
        pygame.font.Font.__init__(self, font, font_size)
        self.text = text
        self.font_size = font_size
        self.font_color = font_color
        self.label = self.render(self.text, 1, self.font_color)
        self.width = self.label.get_rect().width
        self.height = self.label.get_rect().height
        self.dimensions = (self.width, self.height)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.position = pos_x, pos_y
 
    def set_position(self, x, y):
        self.position = (x, y)
        self.pos_x = x
        self.pos_y = y
 
    def set_font_color(self, rgb_tuple):
        self.font_color = rgb_tuple
        self.label = self.render(self.text, 1, self.font_color)
 
    def is_mouse_selection(self, (posx, posy)):
        if (posx >= self.pos_x and posx <= self.pos_x + self.width) and \
            (posy >= self.pos_y and posy <= self.pos_y + self.height):
                return True
        return False

class GameMenu:
    
    def __init__(self, screen, items, funcs, bg_color=WHITE, font=None, font_size=30,
                    font_color=BLACK):
        pygame.init()
        self.screen = screen
        self.scr_width = self.screen.get_rect().width
        self.scr_height = self.screen.get_rect().height
 
        self.bg_color = bg_color
        self.clock = pygame.time.Clock()
        self.funcs = funcs
        self.items = []

        for index, item in enumerate(items):
            menu_item = MenuItem(item, font, font_size, font_color)
            t_h = len(items) * menu_item.height
            pos_x = (self.scr_width / 2) - (menu_item.width / 2)
            pos_y = (self.scr_height / 2) - (t_h / 2) + (index * menu_item.height)
 
            menu_item.set_position(pos_x, pos_y)
            self.items.append(menu_item)
        self.mouse_is_visible = True
        self.cur_item = None

    def set_mouse_visibility(self):
        if self.mouse_is_visible:
            pygame.mouse.set_visible(True)
        else:
            pygame.mouse.set_visible(False)

    def set_keyboard_selection(self, key):
        """
        Marks the MenuItem chosen via up and down keys.
        """
        for item in self.items:
            # Return all to neutral
            item.set_italic(False)
            item.set_font_color(WHITE)
 
        if self.cur_item is None:
            self.cur_item = 0
        else:
            # Find the chosen item
            if key == pygame.K_UP and \
                    self.cur_item > 0:
                self.cur_item -= 1
            elif key == pygame.K_UP and \
                    self.cur_item == 0:
                self.cur_item = len(self.items) - 1
            elif key == pygame.K_DOWN and \
                    self.cur_item < len(self.items) - 1:
                self.cur_item += 1
            elif key == pygame.K_DOWN and \
                    self.cur_item == len(self.items) - 1:
                self.cur_item = 0
 
        self.items[self.cur_item].set_italic(True)
        self.items[self.cur_item].set_font_color(RED)
 
        # Finally check if Enter or Space is pressed
        if key == pygame.K_SPACE or key == pygame.K_RETURN:
            text = self.items[self.cur_item].text
            self.funcs[text]()
 
    def set_mouse_selection(self, item, mpos):
        """Marks the MenuItem the mouse cursor hovers on."""
        if item.is_mouse_selection(mpos):
            item.set_font_color(RED)
            item.set_italic(True)
        else:
            item.set_font_color(BLACK)
            item.set_italic(False)
 
    def run(self):
        mainloop = True
        while mainloop:
            self.clock.tick(50)
            mpos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    mainloop = False
                if event.type == pygame.KEYDOWN:
                        self.mouse_is_visible = False
                        self.set_keyboard_selection(event.key)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for item in self.items:
                        if item.is_mouse_selection(mpos):
                            self.funcs[item.text]()
 
            if pygame.mouse.get_rel() != (0, 0):
                self.mouse_is_visible = True
                self.cur_item = None
 
            self.set_mouse_visibility()
 
            # Redraw the background
            self.screen.fill(self.bg_color)
 
            for item in self.items:
                if self.mouse_is_visible:
                    self.set_mouse_selection(item, mpos)
                self.screen.blit(item.label, item.position)
 
            pygame.display.flip()
            self.screen.fill((255,255,255))


try:
    import android 
except ImportError:
    android = None

def get_animation_positions(pos1, pos2, fps, delay):
    if hasattr(pos1, 'x'):
        x1, y1 = pos1.x, pos1.y
    else:
        x1, y1 = pos1
    if hasattr(pos2, 'x'):
        x2, y2 = pos2.x, pos2.y
    else:
        x2, y2 = pos2
    num = int(fps * delay)

    delta_x = (x2 - x1)/num
    delta_y = (y2 - y1)/num
    points = []
    x, y = x1, y1
    for i in xrange(num):
        x += delta_x
        y += delta_y
        points.append((x, y))
    return points

def get_front_image(card):
    suit_name = card.suit.name[0].upper()
    face_name = card.face.name.upper()
    img = '%s%s.gif' % (face_name, suit_name)
    return img

def get_back_image():
#    return 'BlueBack.gif'
    return 'RedBack.gif'

def get_card_image():
    return '2C.gif'

def make_rect(surface, position):
    rect = surface.get_rect()
    rect.x, rect.y = position
    return rect

def load_image(path):
    fullpath = os.path.join('data/img', path)
    image = pygame.image.load(fullpath)
    image = image.convert_alpha()
    return image

def get_device_resolution():
    resolutions = pygame.display.list_modes()
    return resolutions[0]

def unionall_rects(rects):
    if len(rects) > 0:
        return pygame.Rect(rects[0]).unionall(rects[1:])


GameTurn_start = GameTurn.start
def start(self):
    winning_card = GameTurn_start(self)
    winner = winning_card.owner
    time.sleep(1)

    winner.ui.collect(self.cards)

    return winning_card
GameTurn.start = start


Player_play = Player.play
def play(self, turn):
    if self.is_bot:
        time.sleep(1)
    playerui = self.ui
    playerui.screen.fill(WHITE, playerui.rect)

    card = Player_play(self, turn)
    playerui.throw(card, turn)
    playerui.unfold_cards()
    return card
Player.play = play


def wait_until_human_plays(self, turn, legal_cards):
    while True:
        for event in pygame.event.get():
            # Android-specific:
            if android:
                if android.check_pause():
                    android.wait_for_resume()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for card in self.all_cards[::-1]:
                    if card.ui.rect.collidepoint(x, y):
                        if card in legal_cards:
                            pygame.event.clear()
                            return card
                        else:
                            break
        clock.tick(FPS)
Player.wait_until_human_plays = wait_until_human_plays


class CardUI:
    def __init__(self, card, screen, hide=False):
        card.ui = self

        self.card = card
        self.screen = screen
        self.hide = hide
        self.rect = None

        self.image = load_image(get_front_image(self.card))
        self.back_image = load_image(get_back_image())

    def display(self, position):
        """renders the card at given position
        """
        if self.hide:
            image = self.back_image
        else:
            image = self.image
        self.rect = self.screen.blit(image, position)
        return self.rect

    def show(self, _show=True):
        """show front face of the card
        """
        self.hide = False if _show else True
        self.redraw()

    def redraw(self):
        # only once displayed cards can be moved
        self.display(self.rect)

    def move(self, new_pos, before_callback=None, after_callback=None, disappear=False, delay=0.2):
        return CardUI.move_simultaneously([self.card], [new_pos], before_callback, after_callback, disappear, delay)

    @staticmethod
    def move_simultaneously(cards, all_new_pos, before_callback=None, after_callback=None, disappear=False, delay=0.2):
        def _callback(c):
            if c:
                if isinstance(c, collections.Iterable):
                    [each() for each in c]
                else:
                    c()
        last_sprite_rects = [card.ui.rect for card in cards]
        all_positions = [get_animation_positions(card.ui.rect, new_pos, FPS, delay) for card, new_pos in zip(cards, all_new_pos)]
        for i, positions in enumerate(zip(*all_positions)):
            [card.ui.screen.fill(WHITE, rect) for rect in last_sprite_rects]

            _callback(before_callback)
            if not (disappear and i == len(all_positions[0]) - 1):
                last_sprite_rects = [card.ui.display(positions[j]) for j, card in enumerate(cards)]
            _callback(after_callback)

            pygame.display.update()
            clock.tick(FPS)
        return last_sprite_rects


class PlayerUI:
    def __init__(self, player, screen, board, orientation, hide=False):
        player.ui = self

        self.player = player
        self.screen = screen
        self.board = board
        self.orientation = orientation
        self.hide = hide

        self.dirty_rects = []  # set by unfold_cards()
        self.rect = None  # set by unfold_cards(), union rect of this players card

        # set by set_dimensions()
        self.corner_position = None
        self.throw_position = None
        self.name_position = None

        font = pygame.font.SysFont("monospace", 18)
        self.name = font.render(self.player.name, 1, (0, 0, 0))

        self.hidden_card_rect = load_image(get_back_image()).get_rect()  # used for its dimension
        self.visible_card_rect = load_image(get_card_image()).get_rect()  # used for its dimension
        self.set_dimensions()

    @property
    def card_rect(self):
        if self.hide:
            return self.hidden_card_rect
        else:
            return self.visible_card_rect

    def ready(self):
        # this is also a flag that resets its cards upon unfold_cards call
        self.rect = None

    def set_dimensions(self):
        padding = 20

        self.cards_v_spacing = 15 if self.hide else 30
        self.cards_h_spacing = 20 if self.hide else min(60,
            (self.board[0] - 2*padding - self.card_rect.width)/(13 - 1))

        if self.orientation == 'left':
            position = padding, (self.board[1] - self.visible_card_rect.height - self.card_rect.height)/2
            throw_position = self.board[0]/2 - self.visible_card_rect.width + 10, (
                                self.board[1] + self.hidden_card_rect.height)/2 - self.visible_card_rect.height
            name_position = 0, position[1]
        elif self.orientation == 'top':
            position = (self.board[0] - self.card_rect.width)/2, padding
            throw_position = (self.board[0] - self.visible_card_rect.width)/2, (self.board[1] + self.card_rect.height - 3*self.visible_card_rect.height)/2 + 10
            name_position = position[0], 0
        elif self.orientation == 'right':
            position = self.board[0] - padding - self.card_rect.width - 10, \
                        (self.board[1] - self.visible_card_rect.height - self.card_rect.height)/2
            throw_position = self.board[0]/2, (
                                self.board[1] + self.hidden_card_rect.height)/2 - self.visible_card_rect.height
            name_position = self.board[0]-20, position[1]
        elif self.orientation == 'bottom':
            position = (self.board[0] - self.card_rect.width)/2, self.board[1] - padding - self.card_rect.height
            throw_position = (self.board[0] - self.visible_card_rect.width)/2, (self.board[1] - self.card_rect.height + self.hidden_card_rect.height)/2 - 10
            name_position = position[0], self.board[1]-20
        else:
            raise Exception("Orientation %r is not supported." % self.orientation)
        self.corner_position = position
        self.throw_position = throw_position
        self.name_position = name_position

    def collidepoint(self, point):
        return self.rect.collidepoint(point)

    def colliderect(self, rect):
        return self.rect.colliderect(rect)

    def throw(self, card, turn):
        before_callback = []
        after_callback = []

        # redraw this players' cards
        before_callback.append(lambda: self.redraw(to=card.index))
        after_callback.append(lambda: self.redraw(_from=card.index))

        # redraw all thrown cards to prevent loss of some pixels due to overlapping betn cards
        before_callback.append(lambda: [card.ui.redraw() for card in turn.cards])

        card.ui.show()
        card.ui.move(self.throw_position, before_callback, after_callback, delay=0.1)

        pygame.display.update()

    def collect(self, cards):
        # TODO fix: this can be confused with Player.collect() which is for collecting cards at the beginning
        # collect cards after winning a turn
        before_callback = None
        after_callback = self.redraw

        CardUI.move_simultaneously(cards, [self.corner_position]*len(cards), before_callback, after_callback, disappear=True)

    def redraw(self, _from=0, to=-1):
        """ _from and to both inclusive
        """
        # find positive value for to
        if to < 0:
           to += 13
        for card in self.player.all_cards:
            if _from <= card.index <= to:
                card.ui.redraw()

    def unfold_cards(self):
        self.dirty_rects[:] = []
        total_cards = len(self.player.all_cards)
        if self.orientation in ('top', 'bottom'):
            x = self.corner_position[0] - (total_cards - 1) / 2 * self.cards_h_spacing
            y = self.corner_position[1]
            name = self.name
        else:
            x = self.corner_position[0]
            y = self.corner_position[1] - (total_cards - 1) / 2 * self.cards_v_spacing
            name = pygame.transform.rotate(self.name, 90)

        self.screen.fill(WHITE, make_rect(name, self.name_position))
        self.screen.blit(name, self.name_position)
        all_new_positions = []
        for card in self.player.all_cards:
            if self.rect is None:
                CardUI(card, self.screen, hide=self.hide)
                rect = card.ui.display((x, y))
                self.dirty_rects.append(rect)
            else:
                all_new_positions.append((x, y))

            if self.orientation in ('top', 'bottom'):
                x += self.cards_h_spacing
            else:
                y += self.cards_v_spacing

        if all_new_positions:
            self.dirty_rects[:] = CardUI.move_simultaneously(self.player.all_cards, all_new_positions, delay=0.2)
        else:
            pygame.display.update()

        self.rect = unionall_rects(self.dirty_rects)


class CallBreakUI:
    def __init__(self):
        pygame.init()
        if android:
            android.init()
            self.resolution = get_device_resolution()
        else:
            self.resolution = (800, 600)
            self.resolution = (960, 540)

        self.board = self.resolution[0], self.resolution[1]
        pygame.time.set_timer(pygame.USEREVENT, int(1000 / FPS))

        self.screen = pygame.display.set_mode(self.resolution)
        self.screen.fill(WHITE)
        pygame.display.set_caption('CallBreak')

#        icon = load_image("icon.png")
#        pygame.display.set_icon(icon)

    def MainLoop(self):
        player1 = Player('Sujan', is_bot=True)
        player2 = Player('Sudeep', is_bot=True)
        player3 = Player('Santosh', is_bot=True)
        player4 = Player('Rupa', is_bot=False)

        player1_ui = PlayerUI(player1, self.screen, self.board, 'left', hide=True)
        player2_ui = PlayerUI(player2, self.screen, self.board, 'top', hide=True)
        player3_ui = PlayerUI(player3, self.screen, self.board, 'right', hide=True)
        player4_ui = PlayerUI(player4, self.screen, self.board, 'bottom', hide=False)

        players = [player1_ui, player2_ui, player3_ui, player4_ui]
        game = CallBreak([ui.player for ui in players])

        while True:
            game.ready()

            for player in players:
                player.ready()
                player.unfold_cards()

            game.start()


            # Android-specific:
            #if android:
            #    if android.check_pause():
            #        android.wait_for_resume()




def main():
    screen = pygame.display.set_mode((640, 480), 0, 32)
    cb_ui = CallBreakUI()
    funcs = {'Start': cb_ui.MainLoop,
             'Quit': sys.exit }
    gm = GameMenu(screen,  funcs.keys(), funcs)
    
    gm.run()


if __name__ == '__main__':
    main()