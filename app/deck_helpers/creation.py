from PIL import Image
from ..card_helpers import creation as card_creation

# the pdf image's positions for the top left corner of a given card index
positions = {
    0: (30, 45),
    1: (795, 45),
    2: (1560, 45),
    3: (30, 1090),
    4: (795, 1090),
    5: (1560, 1090),
    6: (104, 2145),
    7: (1208, 2145),
}

cards_on_page = 8


def get_position(photo_index):
    """
    Returns the corner position for a given index for an image
    :param photo_index: int
    :return: tuple (x,y)
    """
    return positions.get(photo_index, (0, 0))


def create_pdf(cards):
    """
    Creates a page images for a list of cards
    :param cards: array of cards
    :return: array of images
    """
    pages = []
    all_cards = []

    for c in cards:
        # get card background and associated font color from card
        card_art, font_color = card_creation.get_art(c['art'].split('/'))
        # create card with art as background
        card_creation.create_card(c, card_art, font_color)
        # add the correct qty of the card to the list of all cards
        for i in range(int(c['qty'])):
            all_cards.append(card_art)

    # put each card art on a page
    for index, card_art in enumerate(all_cards):
        # mod the index to by the max number of cards on a page to get what number card on a page it is
        card_index = index % cards_on_page

        # if it's the first card on a page, create a new page first
        if (card_index == 0):
            pages.append(Image.new('RGB', (2312, 2992), (255, 255, 255)))

        # get the correct page for the card
        page = pages[index // cards_on_page]

        # rotate card 6 and 7 side ways to maximize cards on a piece of paper (woohoo, saving the planet!)
        if (card_index > 5):
            card_art = card_art.rotate(90, expand=1)

        # put card in specified spot onto the page
        page.paste(card_art, get_position(card_index))
    return pages
