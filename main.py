from __future__ import division
import os
import time

import pygame
from pygame.locals import *

from callbreak_card import CallBreak, GameTurn, Player

WHITE = (255, 255, 255)
FPS = 30
clock = pygame.time.Clock()

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
    return 'Back.gif'

def get_card_image():
    return '2C.gif'

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
        if self.hide:
            image = self.back_image
        else:
            image = self.image
        self.rect = self.screen.blit(image, position)
        return self.rect

    def show(self, _show=True):
        self.hide = False if _show else True

    def redraw(self):
        # only once displayed cards can be moved
        self.display(self.rect)

    def move(self, new_pos, before_callback=None, after_callback=None, disappear=False, delay=0.2):
        return CardUI.move_simultaneously([self.card], [new_pos], before_callback, after_callback, disappear, delay)

    @staticmethod
    def move_simultaneously(cards, all_new_pos, before_callback=None, after_callback=None, disappear=False, delay=0.2):
        last_sprite_rects = [card.ui.rect for card in cards]
        all_positions = [get_animation_positions(card.ui.rect, new_pos, FPS, delay) for card, new_pos in zip(cards, all_new_pos)]
        for i, positions in enumerate(zip(*all_positions)):
            [card.ui.screen.fill(WHITE, rect) for rect in last_sprite_rects]
            if before_callback:
                before_callback()
            if not (disappear and i == len(all_positions[0]) - 1):
                last_sprite_rects = [card.ui.display(positions[j]) for j, card in enumerate(cards)]
            if after_callback:
                after_callback()
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
        self.corner_position = None  # set by set_dimensions()
        self.throw_position = None  # set by set_dimenstions()

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
        padding = 5

        self.cards_v_spacing = 15 if self.hide else 30
        self.cards_h_spacing = 20 if self.hide else (
            self.board[0] - 2*padding - self.card_rect.width)/(13 - 1)

        if self.orientation == 'left':
            position = padding, (self.board[1] - self.visible_card_rect.height - self.card_rect.height)/2
            throw_position = self.board[0]/2 - self.visible_card_rect.width, (
                                self.board[1] + self.hidden_card_rect.height)/2 - self.visible_card_rect.height
        elif self.orientation == 'top':
            position = (self.board[0] - self.card_rect.width)/2, padding
            throw_position = (self.board[0] - self.visible_card_rect.width)/2, (self.board[1] + self.card_rect.height - 3*self.visible_card_rect.height)/2
        elif self.orientation == 'right':
            position = self.board[0] - padding - self.card_rect.width, \
                        (self.board[1] - self.visible_card_rect.height - self.card_rect.height)/2
            throw_position = self.board[0]/2, (
                                self.board[1] + self.hidden_card_rect.height)/2 - self.visible_card_rect.height
        elif self.orientation == 'bottom':
            position = (self.board[0] - self.card_rect.width)/2, self.board[1] - padding - self.card_rect.height
            throw_position = (self.board[0] - self.visible_card_rect.width)/2, (self.board[1] - self.card_rect.height + self.hidden_card_rect.height)/2
        else:
            raise Exception("Orientation %r is not supported." % orientation)
        self.corner_position = position
        self.throw_position = throw_position

    def collidepoint(x, y):
        return self.rect.collidepoint(x, y)

    def colliderect(self, rect):
        return self.rect.colliderect(rect)

    def throw(self, card, turn):
        before_callback = after_callback = None
        if self.hide:
            after_callback = self.redraw
        else:
            before_callback = self.redraw

        card.ui.show()
        card.ui.move(self.throw_position, before_callback, after_callback, delay=0.1)
        # redraw because some overlapping motion loses some pixels
        for c in turn.cards:
            c.ui.redraw()
        # this card is not yet appended to turn.cards
        card.ui.redraw()
        pygame.display.update()

    def collect(self, cards):
        before_callback = None
        after_callback = self.redraw

        CardUI.move_simultaneously(cards, [self.corner_position]*len(cards), before_callback, after_callback, disappear=True)

    def redraw(self):
        for card in self.player.all_cards:
            card.ui.redraw()

    def unfold_cards(self):
        self.dirty_rects[:] = []
        total_cards = len(self.player.all_cards)
        if self.orientation in ('top', 'bottom'):
            x = self.corner_position[0] - (total_cards - 1) / 2 * self.cards_h_spacing
            y = self.corner_position[1]
        else:
            x = self.corner_position[0]
            y = self.corner_position[1] - (total_cards - 1) / 2 * self.cards_v_spacing

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
            self.dirty_rects[:] = CardUI.move_simultaneously(self.player.all_cards, all_new_positions, delay=0.1)
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

        self.board = self.resolution[0] * 0.8, self.resolution[1]
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
    cb_ui = CallBreakUI()
    cb_ui.MainLoop()


if __name__ == '__main__':
    main()
