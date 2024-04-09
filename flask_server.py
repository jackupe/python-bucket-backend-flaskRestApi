#!venv/Scripts/python

from flask import Flask, jsonify, abort, request, make_response, url_for, render_template, redirect, send_from_directory
from flask_cors import CORS, cross_origin

import file_handler
import os
import logging

files = [

]

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1000 * 1000  # 500 MB
app.config['FS_ENGINE'] = file_handler.FileHandler()

CORS_ALLOW_ORIGIN = "*,*"
CORS_EXPOSE_HEADERS = "*,*"
CORS_ALLOW_HEADERS = "content-type,*"
cors = CORS(app, origins=CORS_ALLOW_ORIGIN.split(","), allow_headers=CORS_ALLOW_HEADERS.split(","),
            expose_headers=CORS_EXPOSE_HEADERS.split(","), supports_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'


def make_public_file(file):
    new_file = {}
    for field in file:
        if field == 'path':
            new_file['url'] = url_for('get_file', path=file['path'], _external=True)
        else:
            new_file[field] = file[field]
    return new_file


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(500)
def server_error(error):
    return make_response(jsonify({'error': 'Problem with server. Please try again later'}), 500)


@cross_origin()
@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if request.files:
            file = request.files["file"]
            logging.info("filename=%s, name=%s" % (file.filename, file.name))
            app.config['FS_ENGINE'].save_file(file)
            return jsonify("File uploaded"), 201


@cross_origin()
@app.route('/files', methods=['GET'])
def get_files():
    l_files = ["/".join(file.split(os.sep)) for file in app.config['FS_ENGINE'].list_files()]
    return [make_public_file(file_handler.FileDto({'name': file, 'path': file})) for file in l_files]


@cross_origin()
@app.route('/files/<path:path>', methods=['GET'])
def get_file(path):
    return send_from_directory(app.config['FS_ENGINE'].BASE_UPLOAD_FOLDER, path)


@cross_origin()
@app.route('/files/<path:path>', methods=['DELETE'])
def delete_file(path):
    app.config['FS_ENGINE'].delete_file(path)
    return jsonify({'result': True})


if __name__ == '__main__':
    app.run(debug=True)
