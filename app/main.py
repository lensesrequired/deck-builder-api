import io
import traceback
from datetime import datetime
from flask import Flask, send_file, request, jsonify, after_this_request
from flask_restx import Resource, Api, abort
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.exceptions import BadRequest
from flask_cors import CORS
from .models import card, game
from .card_helpers import creation as card_creator, utils as card_utils
from .card_helpers import art_files
from .deck_helpers import creation as deck_creator
from .game_helpers import utils as game_utils
import pymongo
from bson.objectid import ObjectId
from bson.errors import InvalidId
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
GameModel = game.model(api)
GameSettingsModel = game.settings(api)

# set up database access
try:
    client = pymongo.MongoClient(
        "mongodb+srv://dbUser:some-password@deckbuilder-crpyz.mongodb.net/deckbuilder?retryWrites=true&w=majority")
    db = client.deckbuilder
    decksCollection = db.decks
    gamesCollection = db.games
except Exception as error:
    print('error', error)
    traceback.print_tb(error.__traceback__)


def lookupDeck(id):
    try:
        return decksCollection.find_one({'_id': ObjectId(id)})
    except InvalidId as e:
        raise BadRequest(str(e))


def lookupGame(id):
    try:
        return gamesCollection.find_one({'_id': ObjectId(id)})
    except InvalidId as e:
        raise BadRequest(str(e))


# write routes

@api.route('/deck')
class Deck(Resource):
    def post(self):
        """
        Creates a new empty deck an returns the DB ID of the new deck
        :return: string
        """
        new_deck = {
            'cards': []
        }
        # insert new deck
        deck_id = decksCollection.insert_one(new_deck).inserted_id
        return str(deck_id)


@api.route('/deck/<path:deck_id>')
class Deck(Resource):
    def get(self, deck_id):
        """
        Look up and return a user created deck of cards by id
        :param deck_id: string
        :return: Deck object (contains array Cards)
        """
        # look up deck and return 404 if it doesn't exist
        deck = lookupDeck(deck_id)
        if (deck is not None):
            # id needs to be casted to string since object id isn't json-ready
            deck['_id'] = str(deck['_id'])
            return jsonify(deck)
        raise abort(404, "Deck could not be found")


@api.route('/photo/<path:photo_type>')
class Photo(Resource):
    def get(self, photo_type):
        """
        Returns all of the file names for photos of a specified type (ie characters, items, or places)
        :param photo_type:string
        :return:list of file names
        """
        # look up the list of file names or return empty list if the type doesn't exist
        return jsonify(art_files.card_types.get(photo_type, []))


@api.route('/cards/<path:deck_id>')
class Card(Resource):
    @api.expect([CardModel])
    def put(self, deck_id):
        """
        Replaces the cards of a deck and if the deck doesn't exist, creates it
        :param deck_id: string
        :return: OK or error
        """
        # look up deck or create it if it doesn't exist
        deck = lookupDeck(deck_id)
        if (deck is not None):
            decksCollection.update_one({'_id': deck['_id']}, {"$set": {"cards": api.payload}})
            return "OK"

        decksCollection.insert_one({'_id': ObjectId(deck_id), 'cards': api.payload})
        return "OK"


@api.route('/deck/images/<path:deck_id>')
class DeckImages(Resource):
    @api.doc(params={'card_id': 'specific card id (optional)'})
    def get(self, deck_id):
        """
        Looks up a user created deck by id and
        returns array of all the card images if no card id is specified,
        otherwise returns only image of card id requested (still in an array)
        :param deck_id: string
        :return: list of image objects (objects contain image itself, card id, and the last time it was modified)
        """
        # look up deck and return 404 if it doesn't exist
        deck = lookupDeck(deck_id)
        if (deck is not None):
            images = []

            # check if a card id was supplied
            card_id = request.args.get('card_id', False)

            for card_data in deck.get('cards', []):
                # if there wasn't a card id, always create and add card image
                # or if there is a card id only create an image for the card with that id
                if (not card_id or card_id == card_data.get('id', '')):
                    # get the background art and font color based on that
                    img, font_color = card_creator.get_art(card_data.get('art', '').split('/'))

                    # put the card data on the art
                    card_creator.create_card(card_data, img, font_color)

                    # create an image object with the PIL image
                    img_io = io.BytesIO()
                    img.save(img_io, format='PNG')
                    images.append({'id': card_data.get('id', ''),
                                   'data': base64.encodebytes(img_io.getvalue()).decode('ascii'),
                                   'modified_at': datetime.strptime(card_data['modified_at'][:-5],
                                                                    "%Y-%m-%dT%H:%M:%S")})
            return jsonify(images)
        raise abort(404, "Deck could not be found")


@api.route('/deck/<path:deck_id>/pdf/<path:download_id>')
class DeckPDF(Resource):
    def get(self, deck_id, download_id):
        """
        Creates a pdf file of all the cards from a user created deck in the correct quantities
        :param deck_id: string
        :param download_id: string
        :return: pdf file
        """
        # look up deck and return 404 if it doesn't exist
        deck = lookupDeck(deck_id)
        if (deck is not None):
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
                        os.path.abspath(__file__)) + "/../pdfs/deck_" + deck_id + "_" + download_id + ".pdf")
                return response

            # create images out of cards from the deck
            pdf_pages = deck_creator.create_pdf(deck.get('cards', []))

            # convert the images which are paper size and contain up to 8 cards each to something pdf-like
            for page in pdf_pages:
                page.convert('RGB')

            # if there's actual pages save them off into a file on the server 
            # (using save_all will create a duplicate of the first page in this case so we splice it off)
            if (len(pdf_pages)):
                pdf_pages[0].save("pdfs/deck_" + deck_id + "_" + download_id + ".pdf", save_all=True,
                                  append_images=pdf_pages[1:])

            return send_file("../pdfs/deck_" + deck_id + "_" + download_id + ".pdf", mimetype='application/pdf')
        raise abort(404, "Deck could not be found")


@api.route('/games/<path:game_id>')
class Game(Resource):
    def clean_turn_actions(self, actions):
        """
        Convert empty strings to 0's for all action qtys
        :param actions: dictionary where the keys are action_types and the values are dictionaries
        :return: dictionary
        """
        for action, qtys in actions.items():
            if (qtys.get('required', '') == ''):
                actions[action]['required'] = 0
            if (qtys.get('optional', '') == ''):
                actions[action]['optional'] = 0
        return actions

    def get(self, game_id):
        """
        Look up and return game by id
        :param game_id: string
        :return: Game object
        """
        # look up game and return 404 if it doesn't exist
        game = lookupGame(game_id)
        if (game is not None):
            # id needs to be casted to string since object id isn't json-ready
            game['_id'] = str(game['_id'])
            return jsonify(game)
        raise abort(404, "Game could not be found")


@api.route('/games/create/<path:deck_id>')
class Game(Resource):
    def post(self, deck_id):
        """
        Creates a new game with the specified deck and returns the created game's id
        :param deck_id: string
        :return: string
        """
        new_game = {
            'deck_id': deck_id,
            'settings': {
                'num_players': 0,
                'starting_deck': [],
                'starting_hand_size': 0,
                'turn': {
                    'pre': [],
                    'during': dict(),
                    'post': []
                },
                'end_trigger': dict()
            },
            'num_turns': 0,
            'curr_player': -1,
            'players': [],
            'marketplace': [],
            'destroy': [],
            'game_ended': False
        }
        game_id = gamesCollection.insert_one(new_game).inserted_id
        return str(game_id)


@api.route('/games/<path:game_id>/settings')
class Game(Resource):
    @api.expect(GameSettingsModel)
    def patch(self, game_id):
        """
        Update settings and marketplace for a give game id
        :param game_id: string
        :return: OK or error
        """
        # look up game and return 404 if it doesn't exist
        game = lookupGame(game_id)
        if (game is not None):
            settings = {
                'num_players': int(api.payload['numPlayers']),
                'starting_deck': api.payload['startingDeck'],
                'starting_hand_size': int(api.payload['handSize']),
                'turn': {
                    'pre': self.clean_turn_actions(api.payload.get('turn', dict()).get('pre', dict())),
                    'during': self.clean_turn_actions(api.payload.get('turn', dict()).get('during', dict())),
                    'post': self.clean_turn_actions(api.payload.get('turn', dict()).get('post', dict()))
                },
                'end_trigger': api.payload.get('end_trigger', {'turns': 10})
            }
            marketplace = api.payload['marketplace']

            # update db
            gamesCollection.update_one({'_id': ObjectId(game_id)},
                                       {"$set": {"settings": settings,
                                                 "marketplace": marketplace}})
            return "OK"
        raise abort(404, "Game could not be found")


@api.route('/games/<path:game_id>/start')
class Gameplay(Resource):
    def post(self, game_id):
        """
        Start a game by setting the players based on the settings and the current player to the first player
        :param game_id: string
        :return: game object
        """
        # look up game and return 404 if it doesn't exist
        game = lookupGame(game_id)
        if (game is not None):
            # initialize a list of players of the user specified size
            players = [game_utils.setup_player(i, game['settings']) for i in range(game['settings']['num_players'])]

            # set the index of the current player to be the first one and set the players to the initialized list
            game["curr_player"] = 0
            game["players"] = players
            gamesCollection.update_one({'_id': ObjectId(game_id)},
                                       {"$set": game})

            # id needs to be casted to string since object id isn't json-ready
            game['_id'] = str(game['_id'])
            return jsonify(game)
        raise abort(404, "Game could not be found")


@api.route('/games/<path:game_id>/player/start')
class GamePlayer(Resource):
    def post(self, game_id):
        """
        Update current player's turn into started state
        :param game_id: string
        :return: OK or error
        """
        # TODO: Check and do pre-turn actions
        # look up game and return 404 if it doesn't exist
        game = lookupGame(game_id)
        if (game is not None):
            # update the player at the current player index with a turn that is started
            game['players'][game['curr_player']] = game_utils.start_turn(game['players'][game['curr_player']],
                                                                         game['settings'])
            gamesCollection.update_one({'_id': ObjectId(game_id)},
                                       {"$set": {'players': game['players']}})
            return "OK"
        raise abort(404, "Game could not be found")


@api.route('/games/<path:game_id>/player/end')
class GamePlayer(Resource):
    def post(self, game_id):
        """
        Update current player's turn into ended state and set the next player as current
        :param game_id: string
        :return: OK or error
        """
        # TODO: Check and do post-turn actions
        # look up game and return 404 if it doesn't exist
        game = lookupGame(game_id)
        if (game is not None):
            # get player at curr_player index
            player = game['players'][game['curr_player']]

            # check if the player is allowed to end their turn or if they have actions they must still take
            if (game_utils.check_turn_actions(player) > 0):
                raise BadRequest("There are still required actions")

            # update the player with a turn that is ended
            game['players'][game['curr_player']] = game_utils.end_turn(player, game['settings'])
            # increase the current player index by one and if it's greater than the number of players,
            # use mod to start it back over at 0
            curr_player = (game['curr_player'] + 1) % int(game['settings']['num_players'])

            # set number of turns played
            num_turns = game.get('num_turns', 0)
            if (curr_player == 0):
                num_turns += 1

            # check if it's the end of the game and if it is, calculate the stats
            end = game_utils.check_end_triggers(game['settings']['end_trigger'], num_turns, game['marketplace'])
            if (end):
                end = game_utils.calculate_stats(game)

            gamesCollection.update_one({'_id': ObjectId(game_id)},
                                       {"$set": {'players': game['players'],
                                                 'curr_player': curr_player,
                                                 'num_turns': num_turns,
                                                 'game_ended': end}})
            return "OK"
        raise abort(404, "Game could not be found")


@api.route('/games/<path:game_id>/player/card/<path:action_type>')
class GamePlayerCard(Resource):
    @api.doc(params={'index': 'index of card for action', 'num': 'number of cards to act on'})
    def post(self, game_id, action_type):
        """
        Update game/current player with effects of a card action
        :param game_id: string
        :param action_type: string (buy, destroy, discard, draw, or play)
        :return: OK or error
        """
        # look up game and return 404 if it doesn't exist
        game = lookupGame(game_id)
        if (game is not None):
            # look up action in action functions from utils and do that function on the game
            # if the action requested doesn't exist, just return the game as is
            action = card_utils.action_functions.get(action_type, lambda g, a: g)
            try:
                updated_game = action(game, request.args)
            except Exception as e:
                raise BadRequest(str(e))

            # don't send id in the updated game
            del updated_game['_id']
            gamesCollection.update_one({'_id': ObjectId(game_id)},
                                       {"$set": updated_game})
            return "OK"
        raise abort(404, "Game could not be found")


if __name__ == '__main__':
    app.run(debug=True)
