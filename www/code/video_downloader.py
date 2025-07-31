
import yt_dlp
import argparse
import os

def download_video(url, output_path='downloaded'):
    os.makedirs(output_path, exist_ok=True)
    ydl_opts = {
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download videos from a given URL.')
    parser.add_argument('url', help='The URL of the video to download.')
    parser.add_argument('-o', '--output', help='The path to save the video to.', default='downloaded')

    args = parser.parse_args()

    download_video(args.url, args.output)
