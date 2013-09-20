import os
import time

import pygame
from pygame.locals import *

from callbreak_card import CallBreak, Card, Deck, GameTurn, Player

WHITE = (255, 255, 255)
FPS = 10
clock = pygame.time.Clock()

try:
    import android
except ImportError:
    android = None

def get_front_image(card):
    suit_name = card.suit.name[0].lower()
    face_name = card.face.name.lower()
    if face_name == '10':
        face_name = 't'
    img = '%s%s.gif' % (face_name, suit_name)
    return img

def get_back_image():
    return 'b.gif'

def load_image(path):
    fullpath = os.path.join('data/img', path)
    image = pygame.image.load(fullpath)
    image = image.convert()
    return image

class CardUI:
    def __init__(self, card, screen):
        card.ui = self

        self.card = card
        self.screen = screen

        self.image = load_image(get_front_image(self.card))
        self.back_image = load_image(get_back_image())

    def display(self, position, hide=False):
        if hide:
            image = self.back_image
        else:
            image = self.image
        self.rect = self.screen.blit(image, position)
        return self.rect


class PlayerUI:
    cards_v_spacing = 20
    cards_h_spacing = 35

    __player_mappings = {}

    def __init__(self, player, screen, center_position, orientation, hide=False):
        self.player = player
        self.screen = screen
        self.center_position = center_position
        self.orientation = orientation

        if orientation in ('top', 'bottom'):
            self.horizontally = True
        elif orientation in ('left', 'right'):
            self.horizontally = False
        else:
            raise Exception("Orientation %r is not supported." % orientation)

        self.hide = hide
        self.dirty_rects = []
        self.throw_rect = self.calculate_throw_rect()

        PlayerUI.__player_mappings[player] = self

        if not hide:
            self.cards_v_spacing = 25
            self.cards_h_spacing = 35

    @classmethod
    def for_player(cls, player):
        return cls.__player_mappings[player]

    def calculate_throw_rect(self):
        h_offset = 150
        v_offset = 200
        offsets = {
            'left': (h_offset, 0),
            'top': (0, v_offset),
            'right': (-h_offset, 0),
            'bottom': (0, -v_offset)
        }
        card_rect = load_image(get_back_image()).get_rect()
        position = map(sum, zip(self.center_position, offsets[self.orientation]))
        card_rect.x, card_rect.y = position
        return card_rect

    def throw(self, card):
        position = self.throw_rect.x, self.throw_rect.y
        CardUI(card, self.screen).display(position, hide=False)

    def clear_thrown(self):
        card_rect = load_image(get_back_image()).get_rect()
        card_rect.x, card_rect.y = self.throw_position
        self.screen.fill(WHITE, card_rect)
        return card_rect

    def display(self):
        self.dirty_rects[:] = []
        total_cards = len(self.player.all_cards)
        if self.horizontally:
            x = self.center_position[0] - (total_cards - 1) / 2.0 * self.cards_h_spacing
            y = self.center_position[1]
        else:
            x = self.center_position[0]
            y = self.center_position[1] - (total_cards - 1) / 2.0 * self.cards_v_spacing

        for card_set in self.player.cards:
            for card in card_set:
                cardui = CardUI(card, self.screen)
                rect = cardui.display((x, y), hide=self.hide)
                self.dirty_rects.append(rect)

                if self.horizontally:
                    x += self.cards_h_spacing
                else:
                    y += self.cards_v_spacing

def get_device_resolution():
    resolutions = pygame.display.list_modes()
    return resolutions[0]

def unionall_rects(rects):
    return pygame.Rect(rects[0]).unionall(rects[1:])


Player_play = Player.play
def play(self, turn):
    playerui = PlayerUI.for_player(self)
    dirty_rects = playerui.dirty_rects
    big_rect = unionall_rects(dirty_rects)
    playerui.screen.fill(WHITE, big_rect)

    card = Player_play(self, turn)
    playerui.display()
    playerui.throw(card)

    pygame.display.update(big_rect)
    time.sleep(2)
    return card
Player.play = play


def wait_until_human_plays(self, turn, legal_cards):
    while True:
        for event in pygame.event.get():
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


GameTurn_start = GameTurn.start
def start(self):
    winning_card = GameTurn_start(self)

    dirty_rects = []
    for player in self.players:
        playerui = PlayerUI.for_player(player)
        dirty_rects.append(playerui.throw_rect)

    throw_area = unionall_rects(dirty_rects)
    playerui.screen.fill(WHITE, throw_area)
    pygame.display.update(throw_area)
    return winning_card
GameTurn.start = start


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
        pygame.time.set_timer(pygame.USEREVENT, 1000 / FPS)

        self.screen = pygame.display.set_mode(self.resolution)
        self.screen.fill(WHITE)
        pygame.display.set_caption('CallBreak')

        icon = load_image("icon.png")
        pygame.display.set_icon(icon)

    def MainLoop(self):
        player1 = Player('Sujan', is_bot=True)
        player2 = Player('Sudeep', is_bot=True)
        player3 = Player('Santosh', is_bot=True)
        player4 = Player('Rupa', is_bot=False)

        card_rect = load_image(get_back_image()).get_rect()
        padding = {'left': 20, 'top': 20, 'right': 20, 'bottom': 20}  # top, right, bottom, left

        position = (padding['left'], (self.board[1] - card_rect.height)/2.0)
        player1_ui = PlayerUI(player1, self.screen, position, 'left', hide=False)

        position = ((self.board[0] - card_rect.width)/2.0, padding['top'])
        player2_ui = PlayerUI(player2, self.screen, position, 'top', hide=False)

        position = (self.board[0] - padding['right'] - card_rect.width, (self.board[1] - card_rect.height)/2.0)
        player3_ui = PlayerUI(player3, self.screen, position, 'right', hide=False)

        position = ((self.board[0] - card_rect.width)/2.0, self.board[1] - padding['bottom'] - card_rect.height)
        player4_ui = PlayerUI(player4, self.screen, position, 'bottom', hide=False)

        players = [player1_ui, player2_ui, player3_ui, player4_ui]
        game = CallBreak([ui.player for ui in players])
        game.ready()

        for player in players:
            player.display()

        pygame.display.update()

        game.start()

        clock = pygame.time.Clock()
        while True:
             clock.tick(FPS)

            # Android-specific:
            #if android:
            #    if android.check_pause():
            #        android.wait_for_resume()

def main():
    cb_ui = CallBreakUI()
    cb_ui.MainLoop()


if __name__ == '__main__':
    main()
