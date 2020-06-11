import os
import io
import traceback
from flask import Flask, jsonify, send_file
import time
from PIL import Image
from flask_restx import Resource, Api
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app,
          version='0.1',
          title='Our sample API',
          description='This is our sample API'
          )


@api.route('/hello_world')
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


@api.route('/time')
class Time(Resource):
    def get(self):
        print('time')
        return jsonify(time=time.time())


@api.route('/photo')
class Photo(Resource):
    def get(self):
        print('photo')
        img_io = io.BytesIO()
        try:
            script_dir = os.path.dirname(__file__)
            rel_path = "../public/01.png"
            abs_file_path = os.path.join(script_dir, rel_path)
            print("path", abs_file_path)
            image = Image.open(abs_file_path)
            image.save(img_io, 'PNG', quality=70)
            img_io.seek(0)
        except Exception as error:
            print('error', error)
            traceback.print_tb(error.__traceback__)
        return send_file(img_io, mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True)
