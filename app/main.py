import io
import traceback
from flask import Flask, send_file, request, jsonify, after_this_request
from PIL import Image
from flask_restx import Resource, Api
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from .models import card
from .card_helpers import creation as card_creator
from .card_helpers import art_files
from .deck_helpers import creation as deck_creator
import pymongo
from bson.objectid import ObjectId
import base64
import os

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app,
          version='0.1',
          title='Deck Builder API',
          description='This is API'
          )

CardModel = card.model(api)

try:
    client = pymongo.MongoClient(
        "mongodb+srv://dbUser:some-password@deckbuilder-crpyz.mongodb.net/deckbuilder?retryWrites=true&w=majority")
    db = client.deckbuilder
    decksCollection = db.decks
except Exception as error:
    print('error', error)
    traceback.print_tb(error.__traceback__)


@api.route('/photo/<path:photo_type>')
class Photo(Resource):
    @api.doc(params={'name': 'photo name'})
    def get(self, photo_type):
        photo_name = request.args.get('name')
        if (photo_name is not None):
            img_io = io.BytesIO()
            try:
                photo = card_creator.get_photo(photo_type, photo_name)
                img = Image.open(io.BytesIO(photo.content))
                img.save(img_io, 'PNG', quality=70)
                img_io.seek(0)
            except Exception as error:
                print('error', error)
                traceback.print_tb(error.__traceback__)
            return send_file(img_io, mimetype='image/png')
        # TODO: Return all file names of type (this is for ui photo selector)
        return jsonify(art_files.card_types.get(photo_type, []))


@api.route('/deck')
class Deck(Resource):
    def post(self):
        new_deck = {
            'cards': []
        }
        deck_id = decksCollection.insert_one(new_deck).inserted_id
        return str(deck_id)


@api.route('/deck/<path:deck_id>')
class Deck(Resource):
    def get(self, deck_id):
        deck = decksCollection.find_one({'_id': ObjectId(deck_id)})
        if (deck is not None):
            deck['_id'] = str(deck['_id'])
            for card_data in deck.get('cards', []):
                img, font_color = card_creator.get_art(card_data.get('art', '').split('/'))
                img_io = io.BytesIO()

                card_creator.create_card(card_data, img, font_color)

                img.save(img_io, format='PNG')
                card_data['image'] = base64.encodebytes(img_io.getvalue()).decode('ascii')
            return jsonify(deck)
        # TODO: Return 404


@api.route('/deck/<path:deck_id>/pdf/<path:download_id>')
class Deck(Resource):
    def get(self, deck_id, download_id):
        deck = decksCollection.find_one({'_id': ObjectId(deck_id)})
        if (deck is not None):
            @after_this_request
            def remove_file(response):
                os.remove(
                    os.path.dirname(
                        os.path.abspath(__file__)) + "/../pdfs/deck_" + deck_id + "_" + download_id + ".pdf")
                return response

            pdf_pages = deck_creator.create_pdf(deck.get('cards', []))
            for page in pdf_pages:
                page.convert('RGB')
            if (len(pdf_pages)):
                pdf_pages[0].save("pdfs/deck_" + deck_id + "_" + download_id + ".pdf", save_all=True,
                                  append_images=pdf_pages[1:])
            return send_file("../pdfs/deck_" + deck_id + "_" + download_id + ".pdf", mimetype='application/pdf')
        # TODO: Return 404


@api.route('/cards/<path:deck_id>')
class Card(Resource):
    @api.expect([CardModel])
    def put(self, deck_id):
        deck = decksCollection.find_one({'_id': ObjectId(deck_id)})
        if (deck is not None):
            deck['_id'] = str(deck['_id'])
            decksCollection.update_one({'_id': ObjectId(deck_id)}, {"$set": {"cards": api.payload}})
            return "OK"
        # TODO: Return 404
        return "Not OK"


if __name__ == '__main__':
    app.run(debug=True)
