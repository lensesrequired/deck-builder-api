import io
import os
from PIL import Image, ImageDraw, ImageFont
import requests
import textwrap

"""
The various utilities needed to create a card
"""


def get_photo(photo_type, name):
    """
    Gets a card art from art server
    :param photo_type: string
    :param name: string
    :return: image
    """
    return requests.get('https://deck-builder-cards.now.sh/' + photo_type + '/' + name)


def get_art(art):
    """
    Creates PIL_image and specifies font_color
    where the image is a specified background (or white background if no image is specified)
    :param art: array containing photo type and photo name
    :return: card image and font color
    """
    # create blank image of certain size
    img = Image.new('RGB', (715, 1000), (255, 255, 255))
    font_color = "black"

    # check if specified art
    if (len(art) == 2):
        # get art
        photo = get_photo(art[0], art[1])
        # check for successful retrieval
        if (photo.status_code == 200):
            # set correct font color and create PIL Image from art
            font_color = "white"
            img = Image.open(io.BytesIO(photo.content))
        else:
            print('ERROR: err retrieving art for card', photo.content)
    return img, font_color


def create_center_text(text, draw, width, height, font, font_color):
    """
    Put centered text on a pil image with specified qualities
    :param text: string
    :param draw: PIL Draw object
    :param width: int, background width
    :param height: int, how far down the background to put text
    :param font: font to use
    :param font_color: string
    :return: height of the text
    """
    w, h = font.getsize(text)
    # put text on card
    draw.text(((width - w) / 2, height), text, font=font, fill=font_color)
    return h


def create_card(card, background, font_color):
    """
    Create a card image
    :param card: card hash
    :param background: image
    :param font_color: string
    :return: None
    """
    # TODO: use dict.get to set default values for all items
    width, height = background.size
    draw = ImageDraw.Draw(background)
    title_font = ImageFont.truetype(os.path.abspath("app/fonts/RobotoSlab-ExtraBold.ttf"), 64)
    reg_font = ImageFont.truetype(os.path.abspath("app/fonts/RobotoSlab-Regular.ttf"), 40)

    # put title on card
    title = card['name']
    para = textwrap.wrap(title, width=21)  # break title into multiple lines if it's too wide
    pad = 5
    for line in para:
        h = create_center_text(line, draw, width, (height / 20) + pad, title_font, font_color)
        pad += h

    # put victory points on card
    points = 'VP: ' + str(card['victoryPoints'])
    w, h = title_font.getsize(points)
    draw.text((width - (w / 2) - 40, 20), points, font=reg_font, fill=font_color)

    # put card cost on card
    cost = 'Cost: ' + str(card['costBuy'])
    draw.text((25, 20), cost, font=reg_font, fill=font_color)

    # put actions and buying power on card
    actions = card["actions"]
    height = height * 3 / 4
    buying_power = card["buyingPower"]
    for action in actions:
        action_type = action['type']
        qty = action['qty']
        required = action['required']
        # specify whether card is required or optional in the text
        text = ("required " if required else "optional ") + action_type + " " + qty
        # increase height to ensure next line doesn't cover this one
        height += create_center_text(text, draw, width, height, reg_font, font_color)
    if (buying_power):
        buying_power = str(buying_power)
        text = buying_power + ' coins'
        # increase height to ensure next line doesn't cover this one
        height += create_center_text(text, draw, width, height, reg_font, font_color)
