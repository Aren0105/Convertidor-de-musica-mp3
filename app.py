import os
import platform

from flask import Flask, render_template, request, send_file, jsonify, after_this_request
from downloader.youtube import descargar_audio

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():

    data = request.get_json()

    if not data:
        return jsonify({'error': 'No se recibieron datos'}), 400

    url = data.get('url')
    format_type = data.get('format', 'mp3')

    if not url:
        return jsonify({'error': 'Falta la URL'}), 400

    try:

        filename = descargar_audio(
            url,
            format_type,
            DOWNLOAD_FOLDER
        )

        @after_this_request
        def remove_file(response):

            try:
                if os.path.exists(filename):
                    os.remove(filename)
            except Exception as e:
                print(f"Error eliminando archivo: {e}")

            return response

        return send_file(
            filename,
            as_attachment=True
        )

    except Exception as e:

        print(f"ERROR: {e}")

        return jsonify({
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True)