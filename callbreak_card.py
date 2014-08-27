from collections import namedtuple
import logging
import random
import itertools

Face = namedtuple('Face', ('name', 'value'))
Faces = [Face('A', 14)]
for i in xrange(2, 10+1):
    Faces.append(Face(str(i), i))
Faces.extend([
    Face('J', 11),
    Face('Q', 12),
    Face('K', 13),
])

Suit = namedtuple('Suit', ('name', 'value', 'order', 'shape'))
Suits = [
    Suit('spade',   2, 0, u'\u2660'),
    Suit('heart',   1, 1, u'\u2661'),
    Suit('club',    1, 2, u'\u2663'),
    Suit('diamond', 1, 3, u'\u2662'),
]

def make_card(face, suit):
    face = face.upper()
    for f in Faces:
        if f.name == face:
            break
    else:
        raise Exception("Face name supports A, 2-10, J, Q, and K. (%r given)" % face)
    suit = suit.lower()
    for s in Suits:
        if s.name == suit:
            break
    else:
        raise Exception("Suit name accepts spade, heart, club and diamont. (%r given)" % suit)
    return Card(f, s)

class Card:
    def __init__(self, face, suit):
        self.face = face
        self.suit = suit

    def __lt__(self, other):
        if self.suit.name == other.suit.name:
            return self.face.value < other.face.value
        else:
            return self.suit.value < other.suit.value

    def __repr__(self):
        return '%s%s ' % (self.face.name, self.suit.shape.encode('utf-8'))


class Deck:
    def __init__(self):
        self.cards = []
        self.load()

    def load(self):
        self.cards[:] = [Card(f, s) for s in Suits for f in Faces]


class GameTurn:
    def __init__(self, starter, players):
        self.starter = starter
        self.players = players
        self.cards = []
        self.suit = None  # initialized after first card is played in this turn

    def start(self):
        for player in self.iterator():
            card = player.play(self)
            if self.suit is None:
                self.suit = card.suit
            self.cards.append(card)

        return self.get_winning_card()

    def get_winning_card(self):
        winning_card = max(self.cards)

        logging.warn("%s's %s wins this turn", winning_card.owner, winning_card)
        logging.debug("-----")
        return winning_card

    def iterator(self):
        turn = self.starter.turn
        while True:
            yield self.players[turn]
            turn = (turn + 1) % len(self.players)
            if turn == self.starter.turn:
                return


class CallBreak:
    round_count = 0

    def __init__(self, players):
        self.deck = Deck()
        self.players = players

        for i, player in enumerate(players):
            player.turn = i

        # TODO use different object for storing all cards when no_of_decks > 1
        self.cards = self.deck.cards

    def ready(self):
        self.shuffle()
        self.distribute()

    def start(self):
        starter = self.players[self.round_count]
        for i in xrange(13):
            turn = GameTurn(starter, self.players)
            winning_card = turn.start()
            starter = winning_card.owner

    def shuffle(self):
        random.shuffle(self.cards)

    def distribute(self):
        player_count = len(self.players)
        for i, card in enumerate(self.cards):
            player = self.players[i % player_count]
            player.collect(card)


class Player:
    def __init__(self, name, is_bot=True):
        self.name = name
        self.is_bot = is_bot
        self.turn = None  # overriden by int in CallBreak
        self.cards = [[], [], [], []]

    @property
    def all_cards(self):
        return list(itertools.chain.from_iterable(self.cards))

    def collect(self, card):
        card.owner = self
        self.cards[card.suit.order].append(card)

        if len(self.all_cards) == 13:
            [each.sort(key=lambda c: -c.face.value) for each in self.cards]
            for i, card in enumerate(self.all_cards):
                card.index = i

    def get_greater_cards(self, turn, cards):
        greater_cards = filter(lambda c: c > max(turn.cards) if turn.cards else True, cards)
        return greater_cards

    def get_legal_cards(self, turn):
        if turn.suit is None:
            pass
        # select same suit cards
        elif self.cards[turn.suit.order]:
            # select higher cards
            greater_cards = self.get_greater_cards(turn, self.cards[turn.suit.order])
            return (greater_cards, True) if greater_cards else (self.cards[turn.suit.order], False)
        # select spade cards to cut
        elif self.cards[0]:
            # select higher cards
            greater_cards = self.get_greater_cards(turn, self.cards[0])
            if greater_cards:
                return greater_cards, True

        return self.all_cards, False

    def think_to_play(self, turn, legal_cards, has_greater_card):
        if not self.is_bot:
            raise Exception('Humans cannot use machine brain.')

        if has_greater_card and len(turn.cards) < 3:
            return max(legal_cards)
        else:
            return min(legal_cards)

    def wait_until_human_plays(self, turn, legal_cards):
        raise NotImplementedError('coming soon ...')

    def play(self, turn):
        print "%s's cards:" % self.name, self.cards

        legal_cards, has_greater_card = self.get_legal_cards(turn)

        if self.is_bot:
            card = self.think_to_play(turn, legal_cards, has_greater_card)
        else:
            card = self.wait_until_human_plays(turn, legal_cards)

        self.cards[card.suit.order].remove(card)

        logging.warn('%r plays %s', self, card)
        return card

    def __repr__(self):
        return self.name


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    sujan = Player('Sujan', is_bot=True)
    sudeep = Player('Sudeep')
    santosh = Player('Santosh')
    rupa = Player('Rupa')

    # add players in clockwise direction
    players = [sujan, sudeep, santosh, rupa]

    game = CallBreak(players)
    game.ready()
    game.start()
