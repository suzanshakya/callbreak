import os
import itertools

import pygame
from pygame.locals import *

from callbreak_card import Card, Deck, CallBreak, Player

FPS = 30

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
        self.card = card
        self.screen = screen

        self.image = load_image(get_front_image(self.card))
        self.back_image = load_image(get_back_image())

    def display(self, position, hide=True):
        if hide:
            image = self.back_image
        else:
            image = self.image
        self.screen.blit(image, position)


class PlayerUI:
    cards_v_spacing = 20
    cards_h_spacing = 35

    def __init__(self, player, screen, center_position, horizontally, hide=True):
        self.player = player
        self.screen = screen
        self.center_position = center_position
        self.horizontally = horizontally
        self.hide = hide

        if not hide:
            self.cards_v_spacing = 25
            self.cards_h_spacing = 35

    def display(self):
        total_cards = len(list(itertools.chain.from_iterable(self.player.cards)))
        if self.horizontally:
            x = self.center_position[0] - (total_cards - 1) / 2.0 * self.cards_h_spacing
            y = self.center_position[1]
        else:
            x = self.center_position[0]
            y = self.center_position[1] - (total_cards - 1) / 2.0 * self.cards_v_spacing

        for card_set in self.player.cards:
            for card in card_set:
                CardUI(card, self.screen).display((x, y), hide=self.hide)
                if self.horizontally:
                    x += self.cards_h_spacing
                else:
                    y += self.cards_v_spacing

def get_device_resolution():
    resolutions = pygame.display.list_modes()
    return resolutions[0]

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
        pygame.display.set_caption('CallBreak')

        icon = load_image("icon.png")
        pygame.display.set_icon(icon)

    def MainLoop(self):
        player1 = Player('Sujan', is_bot=True)
        player2 = Player('Sudeep', is_bot=True)
        player3 = Player('Santosh', is_bot=True)
        player4 = Player('Rupa', is_bot=True)

        card_rect = load_image(get_back_image()).get_rect()
        padding = [20, 20, 20, 20]  # top, right, bottom, left

        position = (padding[3], (self.board[1] - card_rect.height)/2.0)
        player1_ui = PlayerUI(player1, self.screen, position, False)

        position = ((self.board[0] - card_rect.width)/2.0, padding[0])
        player2_ui = PlayerUI(player2, self.screen, position, True)

        position = (self.board[0] - padding[1] - card_rect.width, (self.board[1] - card_rect.height)/2.0)
        player3_ui = PlayerUI(player3, self.screen, position, False)

        position = ((self.board[0] - card_rect.width)/2.0, self.board[1] - padding[2] - card_rect.height)
        player4_ui = PlayerUI(player4, self.screen, position, True, hide=False)

        players = [player1_ui, player2_ui, player3_ui, player4_ui]
        game = CallBreak([ui.player for ui in players])

        game.shuffle()
        game.distribute()

        for player in players:
            player.display()

        pygame.display.flip()

        while True:
            event = pygame.event.wait()

            # Android-specific:
            #if android:
            #    if android.check_pause():
            #        android.wait_for_resume()

            if event.type == pygame.QUIT:
                raise SystemExit

def main():
    cb_ui = CallBreakUI()
    cb_ui.MainLoop()


if __name__ == '__main__':
    main()
