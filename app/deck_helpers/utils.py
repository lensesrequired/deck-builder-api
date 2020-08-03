from random import randint

"""
The various utilities needed to act on a deck
"""


def shuffle(cards, n):
    """
    Shuffle an array of cards
    :param cards: array of cards
    :param n: number of cards
    :return: shuffled array of cards
    """
    for i in range(n - 1, 0, -1):
        # Pick a random index from 0 to i
        j = randint(0, i + 1)

        # Swap arr[i] with the element at random index
        cards[i], cards[j] = cards[j], cards[i]
    return cards
