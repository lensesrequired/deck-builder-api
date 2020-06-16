from PIL import Image
from ..card_helpers import creation as card_creation

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
    return positions[photo_index] if photo_index < cards_on_page else (0, 0)


def create_pdf(cards):
    pages = []
    all_cards = []
    for c in cards:
        for i in range(int(c['qty'])):
            all_cards.append(c)
    for index, card in enumerate(all_cards):
        photo_index = index % cards_on_page
        if (photo_index == 0):
            pages.append(Image.new('RGB', (2312, 2992), (255, 255, 255)))
        page = pages[index // cards_on_page]
        card_art, font_color = card_creation.get_art(card['art'].split('/'))
        card_creation.create_card(card, card_art, font_color)
        if (photo_index > 5):
            card_art = card_art.rotate(90, expand=1)
        page.paste(card_art, get_position(photo_index))
    return pages
