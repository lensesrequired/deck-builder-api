import os
from flask import Flask, jsonify, send_file
import time
from PIL import Image
import io
import sys
import traceback
app = Flask(__name__)

# @app.route('/', defaults={'path': ''})
@app.route('/time')
def time_route():
    print('time')
    return jsonify(time=time.time())


@app.route('/photo')
def photo_route():
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


def catch_all():
    print('catch')
    return "catch"
