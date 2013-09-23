from __future__ import division
import os
import time

import pygame
from pygame.locals import *

from callbreak_card import CallBreak, GameTurn, Player

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
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

def load_image(path):
    fullpath = os.path.join('data/out', path)
    image = pygame.image.load(fullpath)
    image = image.convert_alpha()
    return image

class CardUI:
    def __init__(self, card, screen):
        card.ui = self

        self.card = card
        self.screen = screen
        self.rect = None

        self.image = load_image(get_front_image(self.card))
        self.back_image = load_image(get_back_image())

    def display(self, position, hide=False):
        if hide:
            image = self.back_image
        else:
            image = self.image
        self.rect = self.screen.blit(image, position)
        return self.rect

    def move(self, new_pos, callback=None, delay=0.1):
        # only once displayed cards can be moved
        last_sprite_rect = self.rect
        for position in get_animation_positions(self.rect, new_pos, FPS, delay):
            self.screen.fill(WHITE, last_sprite_rect)
            last_sprite_rect = self.display(position)
            if callback:
                callback()
            pygame.display.update()
            clock.tick(FPS)
        return last_sprite_rect


class PlayerUI:
    cards_v_spacing = 30
    cards_h_spacing = 35

    def __init__(self, player, screen, board, center_position, orientation, hide=False):
        player.ui = self

        self.player = player
        self.screen = screen
        self.board = board
        self.center_position = center_position
        self.orientation = orientation

        if orientation in ('top', 'bottom'):
            self.horizontally = True
        elif orientation in ('left', 'right'):
            self.horizontally = False
        else:
            raise Exception("Orientation %r is not supported." % orientation)

        self.hide = hide
        self.card_rect = load_image(get_back_image()).get_rect()  # used for its dimension
        self.throw_rect = self.calculate_throw_rect()
        self.dirty_rects = []
        self.rect = None  # set by display(), union rect of this players card

        if not hide:
            self.cards_v_spacing = 30
            self.cards_h_spacing = 35

    def calculate_throw_rect(self):
        offsets = {
            'left': (self.board[0]/2 - self.card_rect.width, 0),
            'top': (0, self.board[1]/2 - self.card_rect.height),
            'right': (self.card_rect.width  - self.board[0]/2, 0),
            'bottom': (0, self.card_rect.height - self.board[1]/2)
        }
        position = map(sum, zip(self.center_position, offsets[self.orientation]))
        self.card_rect.x, self.card_rect.y = position
        return self.card_rect

    def collidepoint(x, y):
        return self.rect.collidepoint(x, y)

    def colliderect(self, rect):
        return self.rect.colliderect(rect)

    def throw(self, card):
        card.ui.move(self.throw_rect, callback=self.display, delay=0.1)

    def collect(self, cards):
        for card in cards:
            card.ui.move(self.center_position, callback=self.display, delay=0.1)

    def clear_thrown(self):
        self.card_rect.x, self.card_rect.y = self.throw_position
        self.screen.fill(WHITE, card_rect)
        return card_rect

    def display(self):
        self.dirty_rects[:] = []
        total_cards = len(self.player.all_cards)
        if self.horizontally:
            x = self.center_position[0] - (total_cards - 1) / 2 * self.cards_h_spacing
            y = self.center_position[1]
        else:
            x = self.center_position[0]
            y = self.center_position[1] - (total_cards - 1) / 2 * self.cards_v_spacing

        for card in self.player.all_cards:
            cardui = hasattr(card, 'ui') and card.ui or CardUI(card, self.screen)
            rect = cardui.display((x, y), hide=self.hide)
            self.dirty_rects.append(rect)

            if self.horizontally:
                x += self.cards_h_spacing
            else:
                y += self.cards_v_spacing
        self.rect = unionall_rects(self.dirty_rects)

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
    playerui.throw(card)
    return card
Player.play = play


def wait_until_human_plays(self, turn, legal_cards):
    while True:
        for event in pygame.event.get():
            # Android-specific:
            if android:
                if android.check_pause():
                    android.wait_for_resume()

                    for player in turn.players:
                        player.ui.display()

                    pygame.display.update()

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


class CallBreakUI:
    def __init__(self):
        pygame.init()

        if android:
            android.init()
            self.resolution = get_device_resolution()
        else:
            self.resolution = (800, 600)
            self.resolution = (540, 960)

        self.board = self.resolution[0], self.resolution[1] * 0.8
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

        card_rect = load_image(get_back_image()).get_rect()
        padding = {'left': 20, 'top': 20, 'right': 20, 'bottom': 20}  # top, right, bottom, left

        position = (padding['left'], (self.board[1] - card_rect.height)/2)
        player1_ui = PlayerUI(player1, self.screen, self.board, position, 'left', hide=True)

        position = ((self.board[0] - card_rect.width)/2, padding['top'])
        player2_ui = PlayerUI(player2, self.screen, self.board, position, 'top', hide=True)

        position = (self.board[0] - padding['right'] - card_rect.width, (self.board[1] - card_rect.height)/2)
        player3_ui = PlayerUI(player3, self.screen, self.board, position, 'right', hide=True)

        position = ((self.board[0] - card_rect.width)/2, self.board[1] - padding['bottom'] - card_rect.height)
        player4_ui = PlayerUI(player4, self.screen, self.board, position, 'bottom', hide=False)

        players = [player1_ui, player2_ui, player3_ui, player4_ui]
        game = CallBreak([ui.player for ui in players])

        while True:
            game.ready()

            for player in players:
                player.display()

            pygame.display.update()

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
