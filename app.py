import os
import sys
import platform
import zipfile
import urllib.request
from flask import Flask, render_template, request, send_file, after_this_request, jsonify
import yt_dlp

app = Flask(__name__)

# --- DETECCIÓN DE SISTEMA ---
# Si estamos en Windows, usamos la lógica de descargar .exe
# Si estamos en Linux (Nube), confiamos en que el sistema ya tiene FFmpeg
IS_WINDOWS = platform.system() == 'Windows'

def verificar_ffmpeg_local():
    if not IS_WINDOWS: return # En Linux no hacemos nada
    
    if os.path.exists("ffmpeg.exe") and os.path.exists("ffprobe.exe"):
        return
    
    print("⚠️ WINDOWS DETECTADO: Descargando FFmpeg local...")
    # (Aquí iría tu código de descarga anterior, pero para despliegue
    #  lo simplificamos: asume que en tu PC ya los tienes)

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
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': True,
            'ignoreerrors': True,
        }

        # TRUCO DE INGENIERÍA:
        # Solo le decimos dónde está ffmpeg si estamos en Windows.
        # En el servidor (Linux), yt-dlp lo encuentra solo.
        if IS_WINDOWS:
            ydl_opts['ffmpeg_location'] = '.'
        
        # Post-procesamiento para audio
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
            filename = temp_name.rsplit('.', 1)[0] + '.mp3'

        @after_this_request
        def remove_file(response):
            try:
                if os.path.exists(filename): os.remove(filename)
            except: pass
            return response

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # En local usamos debug=True, en producción gunicorn se encarga
    app.run(debug=True)