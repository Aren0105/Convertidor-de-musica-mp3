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
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': True,
            'ignoreerrors': True,
            # --- AQUÍ ESTÁ LA MAGIA: LAS COOKIES 🍪 ---
            # Le decimos que use el archivo que subiste
            'cookiefile': 'cookies.txt', 
            # ------------------------------------------
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
        }

        if IS_WINDOWS:
            ydl_opts['ffmpeg_location'] = '.'
        
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
            base_name = temp_name.rsplit('.', 1)[0]
            if format_type == 'mp3':
                filename = base_name + '.mp3'
            else:
                filename = temp_name

        @after_this_request
        def remove_file(response):
            try:
                if os.path.exists(filename): os.remove(filename)
            except: pass
            return response

        return send_file(filename, as_attachment=True)

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        # Si falla, le damos una pista clara al usuario
        if "Sign in" in str(e):
            return jsonify({'error': "Error de Bloqueo: YouTube rechazó las cookies o la IP. Intenta más tarde."}), 500
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
