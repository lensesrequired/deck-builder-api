import io
import os
from PIL import Image, ImageDraw, ImageFont
import requests
import textwrap


def get_photo(photo_type, name):
    return requests.get('https://deck-builder-cards.now.sh/' + photo_type + '/' + name)


def get_art(art):
    """
    returns tuple containing PIL_image, font_color
    given a list of two strings, a photo type and photo name, returns a card background with that photo
    otherwise returns a white background
    """
    img = Image.new('RGB', (715, 1000), (255, 255, 255))
    font_color = "black"
    if (len(art) == 2):
        photo = get_photo(art[0], art[1])
        if (photo.status_code == 200):
            font_color = "white"
            img = Image.open(io.BytesIO(photo.content))
        else:
            print('ERROR: err retrieving art for card', photo.content)
    return img, font_color


def create_text(text, draw, width, height, font, font_color):
    w, h = font.getsize(text)
    draw.text(((width - w) / 2, height), text, font=font, fill=font_color)
    return h


def create_card(card, background, font_color):
    # TODO: use dict.get to set default values for all items
    width, height = background.size
    draw = ImageDraw.Draw(background)
    title_font = ImageFont.truetype(os.path.abspath("app/fonts/RobotoSlab-ExtraBold.ttf"), 64)
    reg_font = ImageFont.truetype(os.path.abspath("app/fonts/RobotoSlab-Regular.ttf"), 40)

    title = card['name']
    para = textwrap.wrap(title, width=21)
    pad = 0
    for line in para:
        w, h = title_font.getsize(line)
        draw.text(((width - w) / 2, (height / 20) + pad), line, font=title_font, fill=font_color)
        pad += h

    points = 'VP: ' + str(card['victoryPoints'])
    w, h = title_font.getsize(points)
    draw.text((width - (w / 2) - 40, 20), points, font=reg_font, fill=font_color)

    cost = 'Cost: ' + str(card['costBuy'])
    draw.text((25, 20), cost, font=reg_font, fill=font_color)

    actions = card["actions"]
    height = height * 3 / 4
    discard = actions["discardQty"]
    destroy = actions["destroyQty"]
    additions = actions["additions"]
    buying_power = actions["buyingPower"]
    if (discard):
        discard = str(discard)
        text = ("Discard " if actions["discardRequired"] else "You may discard ") + discard + " card"
        height += create_text(text, draw, width, height, reg_font, font_color)
    if (destroy):
        destroy = str(destroy)
        text = ("Destroy " if actions["destroyRequired"] else "You may destroy ") + destroy + " card"
        height += create_text(text, draw, width, height, reg_font, font_color)
    for addition in additions:
        additionQty = str(addition['qty'])
        additionType = str(addition['type'])
        text = additionType + ' +' + additionQty
        height += create_text(text, draw, width, height, reg_font, font_color)
    if (buying_power):
        buying_power = str(buying_power)
        text = buying_power + ' coins'
        height += create_text(text, draw, width, height, reg_font, font_color)
