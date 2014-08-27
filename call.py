import os
import pickle

from callbreak_card import Player, CallBreak
import probab

def win_chance_for_card(card, cards_count, other_players_count=3):
    same_suit_remaining_cards = 13 - cards_count
    min_cards_to_exist = 15 - card.face.value

    if cards_count < min_cards_to_exist:
        return 0

    generator = lambda: probab.get_heart_distribution(same_suit_remaining_cards, other_players_count)
    predicate = lambda dist: probab.contains_min(dist, min_cards_to_exist)
    return probab.get_prob(generator, predicate, repeat=1000, count=2)


def can_win(cards):
    """
    Probability that each card can lead on same suit
    """
    chance = 0
    for suit_cards in cards:
        for card in suit_cards:
            p = win_chance_for_card(card, len(suit_cards), other_players_count=3)
            print card, '=', p
            chance += p
    return chance


def suggest_call(cards):
    chance = can_win(cards)
    return chance


if __name__ == '__main__':
    card_storage = 'cards.pkl'
    if os.path.exists(card_storage):
        with open(card_storage, 'rb') as f:
            players = pickle.load(f)
    else:
        sujan = Player('Sujan')
        sudeep = Player('Sudeep')
        santosh = Player('Santosh')
        rupa = Player('Rupa')

        # add players in clockwise direction
        players = [sujan, sudeep, santosh, rupa]

        game = CallBreak(players)
        game.ready()

        with open(card_storage, 'wb') as f:
            pickle.dump(players, f, pickle.HIGHEST_PROTOCOL)

    total = 0
    for player in players:
        cards = player.cards
        print cards
        call = suggest_call(cards)
        total += call
        print call
    print total
