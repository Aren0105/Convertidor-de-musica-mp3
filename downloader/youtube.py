import os
import yt_dlp


def descargar_audio(url, format_type, download_folder):

    opciones = {
        'outtmpl': os.path.join(
            download_folder,
            '%(title)s.%(ext)s'
        ),
        'noplaylist': True,
        'cookiefile': 'cookies.txt'
    }

    # MP3
    if format_type == 'mp3':

        opciones['format'] = 'bestaudio/best'

        opciones['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]

    # MP4
    elif format_type == 'mp4':

        opciones['format'] = (
            'bestvideo[ext=mp4]+bestaudio[ext=m4a]/'
            'best[ext=mp4]'
        )

        opciones['merge_output_format'] = 'mp4'

    else:
        raise ValueError('Formato no válido')

    with yt_dlp.YoutubeDL(opciones) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        filename = ydl.prepare_filename(info)

    # Después de convertir a MP3, cambia la extensión
    if format_type == 'mp3':
        filename = os.path.splitext(filename)[0] + '.mp3'

    # En MP4 yt-dlp puede haber generado el archivo .mp4
    elif format_type == 'mp4':
        filename = os.path.splitext(filename)[0] + '.mp4'

    return filename
