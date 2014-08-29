from __future__ import division
import random

def get_spade_distribution(cards_count, players_count, random_gen, _extra=False):
    counts = []
    _cards_count = cards_count
    for i in xrange(players_count-1):
        args = [0, _cards_count]
        if _extra:
            args.append(_cards_count/(players_count-i))
        players_card_count = _cards_count and _normalize(random_gen(*args))
        counts.append(players_card_count)
        _cards_count -= players_card_count
    counts.append(_cards_count)
    return counts

def _normalize(f):
    return int(round(f))

def contains_min(dist, count):
    return min(dist) >= count

def contains_max(dist, count):
    return max(dist) >= count

def get_prob(generator, predicate, repeat=1000, count=3):
    return min(sum(predicate(generator()) for i in xrange(repeat))/repeat*100 for j in xrange(count))/100

def shuffle(cards):
    return random.shuffle(cards)
    # sattoloCycle
    randrange = random.randrange

    for i in xrange(len(cards)-1, 0, -1):
        j = randrange(i)  # 0 <= j <= i-1
        cards[j], cards[i] = cards[i], cards[j]

def get_heart_distribution(cards_count, players_count):
    cards = [1]*cards_count + [0]*(cards_count*(players_count-1))
    shuffle(cards)
    cards_distribution = [cards[i*cards_count:(i+1)*cards_count] for i in xrange(players_count)]
    return map(sum, cards_distribution)

def main():
#    generator = lambda: get_spade_distribution(10, 3, random.triangular, _extra=True)
    generator = lambda: get_heart_distribution(13-5, 3)
    predicate = lambda dist: contains_min(dist, 15-13)
    print get_prob(generator, predicate)


if __name__ == '__main__':
    main()
