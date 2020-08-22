import io
from datetime import datetime
from flask import Flask, send_file, request, jsonify, after_this_request
from flask_restx import Resource, Api, abort
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from .models import card
from .card_helpers import creation as card_creator
from .deck_helpers import creation as deck_creator
import base64
import os

# create flask app
app = Flask(__name__)
cors = CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app,
          version='0.1',
          title='Deck Builder API',
          description='This is API'
          )

# create models
CardModel = card.model(api)


@api.route('/deck/images/<path:download_id>')
class DeckImages(Resource):
    @api.expect([CardModel])
    def post(self, download_id):
        """
        returns array of all the card images
        :param download_id: string
        :return: list of image objects (objects contain image itself, card id, and the last time it was modified)
        :raises: 400 (Bad Request), 404 (Not found)
        """
        # look up deck and return 404 if it doesn't exist
        if (api.payload is not None):
            cards = api.payload
            images = []

            for card_data in cards:
                # if there wasn't a card id, always create and add card image
                # or if there is a card id only create an image for the card with that id
                # get the background art and font color based on that
                img, font_color = card_creator.get_art(card_data.get('art', '').split('/'))

                # put the card data on the art
                card_creator.create_card(card_data, img, font_color)

                # create an image object with the PIL image
                img_io = io.BytesIO()
                img.save(img_io, format='PNG')
                images.append({'_id': card_data.get('_id', ''),
                               'data': base64.encodebytes(img_io.getvalue()).decode('ascii'),
                               'modifiedAt': datetime.strptime(card_data['modifiedAt'][:-5],
                                                               "%Y-%m-%dT%H:%M:%S")})
            return jsonify(images)
        raise abort(404, "Deck could not be found")


@api.route('/deck/pdf/<path:download_id>')
class DeckPDF(Resource):
    @api.expect([CardModel])
    def post(self, download_id):
        """
        Creates a pdf file of all the cards from a user created deck in the correct quantities
        :param download_id: string
        :return: pdf file of all card images from deck
        :raises: 400 (Bad Request), 404 (Not found)
        """
        # look up deck and return 404 if it doesn't exist
        if (api.payload is not None):
            cards = api.payload
            download_id = request.args.get('download_id', 'download_id')

            # specify an action to take after ever request
            @after_this_request
            def remove_file(response):
                """
                Removes the pdf from server storage to avoid bloating of unnecessary files
                :param response: response to the http request
                :return: response
                """
                os.remove(
                    os.path.dirname(
                        os.path.abspath(__file__)) + "/../pdfs/deck_" + download_id + ".pdf")
                return response

            # create images out of cards from the deck
            pdf_pages = deck_creator.create_pdf(cards)

            # convert the images which are paper size and contain up to 8 cards each to something pdf-like
            for page in pdf_pages:
                page.convert('RGB')

            # if there's actual pages save them off into a file on the server 
            # (using save_all will create a duplicate of the first page in this case so we splice it off)
            if (len(pdf_pages)):
                pdf_pages[0].save("pdfs/deck_" + download_id + ".pdf", save_all=True,
                                  append_images=pdf_pages[1:])

            return send_file("../pdfs/deck_" + download_id + ".pdf", mimetype='application/pdf')
        raise abort(404, "Deck could not be found")


if __name__ == '__main__':
    app.run(debug=True)
