import io
import traceback
from flask import Flask, send_file, request, jsonify, after_this_request
from PIL import Image
from flask_restx import Resource, Api
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from .models import card, game
from .card_helpers import creation as card_creator, utils as card_utils
from .card_helpers import art_files
from .deck_helpers import creation as deck_creator, utils as deck_utils
import pymongo
from bson.objectid import ObjectId
import base64
import os

app = Flask(__name__)
cors = CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app,
          version='0.1',
          title='Deck Builder API',
          description='This is API'
          )

CardModel = card.model(api)
GameModel = game.model(api)

try:
    client = pymongo.MongoClient(
        "mongodb+srv://dbUser:some-password@deckbuilder-crpyz.mongodb.net/deckbuilder?retryWrites=true&w=majority")
    db = client.deckbuilder
    decksCollection = db.decks
    gamesCollection = db.games
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


@api.route('/games/create/<path:deck_id>')
class Game(Resource):
    def post(self, deck_id):
        new_game = {
            'deck_id': deck_id,
            'settings': {
                'num_players': 0,
                'starting_deck': [],
                'starting_hand_size': 0,
                'turn': {
                    'pre': [],
                    'during': [],
                    'post': []
                }
            },
            'curr_player': -1,
            'players': [],
            'marketplace': [],
            'discard': [],
            'destroy': []
        }
        game_id = gamesCollection.insert_one(new_game).inserted_id
        return str(game_id)


@api.route('/games/<path:game_id>')
class Game(Resource):
    # @api.marshal_with(GameModel)
    def get(self, game_id):
        game = gamesCollection.find_one({'_id': ObjectId(game_id)})
        if (game is not None):
            game['_id'] = str(game['_id'])
            for card_data in game.get('marketplace', []):
                img, font_color = card_creator.get_art(card_data.get('art', '').split('/'))
                img_io = io.BytesIO()

                card_creator.create_card(card_data, img, font_color)

                img.save(img_io, format='PNG')
                card_data['image'] = base64.encodebytes(img_io.getvalue()).decode('ascii')
            if (game.get('curr_player', -1) > -1):
                for card_data in game.get('players', [])[game['curr_player']].get('hand', []):
                    img, font_color = card_creator.get_art(card_data.get('art', '').split('/'))
                    img_io = io.BytesIO()

                    card_creator.create_card(card_data, img, font_color)

                    img.save(img_io, format='PNG')
                    card_data['image'] = base64.encodebytes(img_io.getvalue()).decode('ascii')
            return jsonify(game)
        # TODO: Return 404
        return "Not OK"

    @api.expect(GameModel)
    def patch(self, game_id):
        game = gamesCollection.find_one({'_id': ObjectId(game_id)})
        if (game is not None):
            game['_id'] = str(game['_id'])
            settings = {
                'num_players': int(api.payload['numPlayers']),
                'starting_deck': api.payload['startingDeck'],
                'starting_hand_size': int(api.payload['handSize']),
                'turn': {
                    'pre': [],
                    'during': [{'type': 'action', 'qty': 1, 'required': False},
                               {'type': 'buy', 'qty': 1, 'required': False}],
                    'post': [{'type': 'discard', 'qty': -1, 'required': True},
                             {'type': 'draw', 'qty': int(api.payload['handSize']), 'required': True}]
                }
            }
            marketplace = api.payload['marketplace']
            gamesCollection.update_one({'_id': ObjectId(game_id)},
                                       {"$set": {"settings": settings,
                                                 "marketplace": marketplace}})
            return "OK"
        # TODO: Return 404
        return "Not OK"


@api.route('/games/<path:game_id>/start')
class Game(Resource):
    def setupPlayer(self, index, settings):
        player = {
            'name': 'Player ' + str(index + 1),
            'discard': [],
            'deck': [],
            'hand': [],
            'current_turn': None
        }
        player['deck'] = deck_utils.shuffle(
            [card for card in settings['starting_deck'] for i in range(int(card['qty']))],
            len(player['deck']))
        hand = []
        for i in range(settings['starting_hand_size']):
            hand.append(player['deck'].pop())
        player['hand'] = hand
        return player

    def post(self, game_id):
        game = gamesCollection.find_one({'_id': ObjectId(game_id)})
        if (game is not None):
            game['_id'] = str(game['_id'])
            players = [self.setupPlayer(i, game['settings']) for i in range(game['settings']['num_players'])]
            gamesCollection.update_one({'_id': ObjectId(game_id)},
                                       {"$set": {"curr_player": 0, 'players': players}})
            game = gamesCollection.find_one({'_id': ObjectId(game_id)})
            return jsonify(game)
        # TODO: Return 404
        return "Not OK"


@api.route('/games/<path:game_id>/player/start')
class Game(Resource):
    def start_turn(self, player, settings):
        player['current_turn'] = settings['turn']['during']
        player['current_turn'].append({'type': 'buying_power', 'qty': 0})
        return player

    def post(self, game_id):
        # TODO: Check and do pre-turn actions
        game = gamesCollection.find_one({'_id': ObjectId(game_id)})
        if (game is not None):
            game['_id'] = str(game['_id'])
            players = [game['players'][player_index] if player_index != game['curr_player']
                       else self.start_turn(game['players'][player_index], game['settings'])
                       for player_index in range(len(game['players']))]
            gamesCollection.update_one({'_id': ObjectId(game_id)},
                                       {"$set": {'players': players}})
            return "OK"
        # TODO: Return 404
        return "Not OK"


@api.route('/games/<path:game_id>/player/end')
class Game(Resource):
    def end_turn(self, player):
        player['current_turn'] = None
        player['discard'] += player['hand']
        new_cards = []
        deck = player['deck']
        for i in range(5):
            if (len(deck) == 0):
                deck = deck_utils.shuffle(player['discard'], len(player['discard']))
                player['discard'] = []
            if (len(deck) > 0):
                new_cards.append(deck.pop())
        player['hand'] = new_cards
        return player

    def post(self, game_id):
        # TODO: Check and do post-turn actions
        game = gamesCollection.find_one({'_id': ObjectId(game_id)})
        if (game is not None):
            game['_id'] = str(game['_id'])
            game['players'][game['curr_player']] = self.end_turn(game['players'][game['curr_player']])

            gamesCollection.update_one({'_id': ObjectId(game_id)},
                                       {"$set": {'players': game['players'],
                                                 'curr_player': (game['curr_player'] + 1) %
                                                                int(game['settings']['num_players'])}})
            return "OK"
        # TODO: Return 404
        return "Not OK"


@api.route('/games/<path:game_id>/player/card/play')
class Game(Resource):
    def play_card(self, player, index):
        actions = player['hand'][index]['actions']
        for action in actions:
            card_utils.add_action(player['current_turn'], action)
        if len(actions):
            card_utils.use_action(player['current_turn'], 'action')
        player['current_turn'] = [
            action if action['type'] != 'buying_power' else
            {'type': 'buying_power', 'qty': action['qty'] + int(player['hand'][index].get('buyingPower', 0))}
            for action in player['current_turn']
        ]
        player['hand'][index]['played'] = True
        return player

    @api.doc(params={'index': 'index of card from hand'})
    def post(self, game_id):
        # TODO: Verify playing card is allowed
        game = gamesCollection.find_one({'_id': ObjectId(game_id)})
        if (game is not None):
            game['_id'] = str(game['_id'])
            index = request.args.get('index')
            new_player = self.play_card(game['players'][game['curr_player']], int(index))
            game['players'][game['curr_player']] = new_player
            gamesCollection.update_one({'_id': ObjectId(game_id)},
                                       {"$set": {'players': game['players']}})
            # Return adjusted player hand
            print(game['players'][game['curr_player']])
            return "OK"
        # TODO: Return 404
        return "Not OK"


@api.route('/games/<path:game_id>/player/card/buy')
class Game(Resource):
    def buy_card(self, marketplace, player, index):
        c = marketplace[index]
        marketplace[index] = card_utils.decrementQty(marketplace[index])
        player['discard'].append(c)
        card_utils.use_action(player['current_turn'], 'buy')
        for i in range(int(c['costBuy'])):
            card_utils.use_action(player['current_turn'], 'buying_power')
        return marketplace, player

    @api.doc(params={'index': 'index of card from marketplace'})
    def post(self, game_id):
        # TODO: Verify buying card is allowed
        game = gamesCollection.find_one({'_id': ObjectId(game_id)})
        if (game is not None):
            game['_id'] = str(game['_id'])
            index = request.args.get('index')
            marketplace, player = self.buy_card(game['marketplace'], game['players'][game['curr_player']], int(index))
            game['players'][game['curr_player']] = player
            gamesCollection.update_one({'_id': ObjectId(game_id)},
                                       {"$set": {'players': game['players'], 'marketplace': marketplace}})
            print(marketplace, game['players'][game['curr_player']])
            return "OK"
        # TODO: Return 404
        return "Not OK"


@api.route('/games/<path:game_id>/player/card/draw')
class Game(Resource):
    def draw_cards(self, player, num_draw):
        new_cards = []
        deck = player['deck']
        for i in range(num_draw):
            card_utils.use_action(player['current_turn'], 'draw')
            if (len(deck) == 0):
                deck = deck_utils.shuffle(player['discard'], len(player['discard']))
                player['discard'] = []
            if (len(deck) > 0):
                new_cards.append(deck.pop())
        player['hand'] += new_cards
        return player, new_cards

    @api.doc(params={'num_draw': 'number of cards to draw'})
    def post(self, game_id):
        # TODO: Check and do pre-turn actions
        game = gamesCollection.find_one({'_id': ObjectId(game_id)})
        if (game is not None):
            game['_id'] = str(game['_id'])
            num_draw = request.args.get('num_draw')
            player, new_cards = self.draw_cards(game['players'][game['curr_player']], int(num_draw))
            game['players'][game['curr_player']] = player
            gamesCollection.update_one({'_id': ObjectId(game_id)},
                                       {"$set": {'players': game['players']}})
            print(new_cards)
            # return new cards with images
            return "OK"
        # TODO: Return 404
        return "Not OK"


@api.route('/games/<path:game_id>/player/card/discard')
class Game(Resource):
    @api.doc(params={'index': 'index of card to discard'})
    def post(self, game_id):
        # TODO: Check and do pre-turn actions
        game = gamesCollection.find_one({'_id': ObjectId(game_id)})
        if (game is not None):
            game['_id'] = str(game['_id'])
            index = request.args.get('index')
            player = game['players'][game['curr_player']]
            card_utils.use_action(player['current_turn'], 'discard')
            player['discard'].append(player['hand'].pop(int(index)))
            game['players'][game['curr_player']] = player
            gamesCollection.update_one({'_id': ObjectId(game_id)},
                                       {"$set": {'players': game['players']}})
            print(game['players'])
            # return new hand
            return "OK"
        # TODO: Return 404
        return "Not OK"


@api.route('/games/<path:game_id>/player/card/destroy')
class Game(Resource):
    @api.doc(params={'index': 'index of card to discard'})
    def post(self, game_id):
        # TODO: Check and do pre-turn actions
        game = gamesCollection.find_one({'_id': ObjectId(game_id)})
        if (game is not None):
            game['_id'] = str(game['_id'])
            index = request.args.get('index')
            player = game['players'][game['curr_player']]
            card_utils.use_action(player['current_turn'], 'destroy')
            game['destroy'].append(player['hand'].pop(int(index)))
            game['players'][game['curr_player']] = player
            gamesCollection.update_one({'_id': ObjectId(game_id)},
                                       {"$set": {'players': game['players'], 'destroy': game['destroy']}})
            print(game['players'])
            return "OK"
        # TODO: Return 404
        return "Not OK"


if __name__ == '__main__':
    app.run(debug=True)
