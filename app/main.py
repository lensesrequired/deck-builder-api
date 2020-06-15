import io
import traceback
from flask import Flask, send_file, request
from PIL import Image
from flask_restx import Resource, Api
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from .models import card
from .card_helpers import creation as card_creator

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app,
          version='0.1',
          title='Deck Builder API',
          description='This is API'
          )

CardModel = card.model(api)


@api.route('/photo/<path:photo_type>')
class Photo(Resource):
    @api.doc(params={'name': 'photo name'})
    def get(self, photo_type):
        print('photo')
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
        # TODO: Return all files of type (this is for ui photo selector)
        return "Hello"


@api.route('/card')
class Card(Resource):
    @api.expect(CardModel)
    def post(self):
        payload = api.payload
        img, font_color = card_creator.get_art(payload.get('art', '').split('/'))
        img_io = io.BytesIO()

        card_creator.create_card(payload, img, font_color)

        img.save(img_io, 'PNG', quality=70)
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True)
