import os
import sys
import platform
from flask import Flask, render_template, request, send_file, after_this_request, jsonify
import yt_dlp

app = Flask(__name__)

IS_WINDOWS = platform.system() == 'Windows'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    url = data.get('url')
    format_type = data.get('format', 'mp3')
    
    if not url: return jsonify({'error': 'Falta URL'}), 400

    try:
        # --- AQUÍ ESTÁ EL TRUCO DEL DISFRAZ ---
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': True,
            'ignoreerrors': True,
            # 1. Le decimos que finja ser un Android y un iPhone
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios']
                }
            },
            # 2. Añadimos cabeceras falsas para parecer un navegador real
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        }

        # Configuración extra solo para Windows (Local)
        if IS_WINDOWS:
            ydl_opts['ffmpeg_location'] = '.'
        
        # Post-procesamiento para MP3
        if format_type == 'mp3':
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        filename = ""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            temp_name = ydl.prepare_filename(info)
            # Ajuste de nombre por si acaso
            base_name = temp_name.rsplit('.', 1)[0]
            if format_type == 'mp3':
                filename = base_name + '.mp3'
            else:
                filename = temp_name

        @after_this_request
        def remove_file(response):
            try:
                # Borramos tanto el original como el convertido para limpiar
                if os.path.exists(filename): os.remove(filename)
            except: pass
            return response

        return send_file(filename, as_attachment=True)

    except Exception as e:
        # Imprimimos el error en la consola de Render para verlo
        print(f"❌ ERROR CRÍTICO: {str(e)}")
        return jsonify({'error': f"Bloqueo de YouTube detectado: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
