import os
import yt_dlp


def descargar_audio(url, format_type, download_folder):

    opciones = {

        'format': 'bestaudio/best',

        'outtmpl': os.path.join(
            download_folder,
            '%(title)s.%(ext)s'
        ),

        'noplaylist': True,

        'cookiefile': 'cookies.txt'
    }

    if format_type == 'mp3':

        opciones['postprocessors'] = [

            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }

        ]

    with yt_dlp.YoutubeDL(opciones) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        filename = ydl.prepare_filename(info)

    if format_type == 'mp3':

        filename = os.path.splitext(filename)[0] + '.mp3'

    return filename