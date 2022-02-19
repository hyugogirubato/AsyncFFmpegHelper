"""
Project: AsyncFFmpegHelper
Author: hyugogirubato
Script: main.py
Version: v2022.02.19
"""

import argparse
import os.path
import sys

import AsyncFFmpegHelper
import utils


# main_arg.py --download "11" --id "G2XU03VQ5" --url "https://..." --ffmpeg="-c:v copy -c:a copy -c:s copy" --output "video.mp4" --skip true
# main_arg.py --extract --id "G2XU03VQ5" --url "https://..." --skip true
# main_arg.py --clear

def get_config(args):
    config = {}
    config['path'] = args.path
    if args.clear:
        pass
    elif args.extract or args.download:
        if not args.id:
            utils.error('No process id defined.')
        elif not args.url:
            utils.error('No url defined.')
        else:
            config['skip'] = args.skip
            config['log'] = args.log
            config['tasks'] = args.tasks
            config['id'] = args.id
            config['url'] = args.url

        if args.extract:
            pass
        elif args.download:
            if not args.output:
                utils.error('No output file defined.')

            try:
                download = int(args.download)
            except Exception as e:
                utils.error('Invalid ID. The id must be an int.')
            if args.ffmpeg:
                ffmpeg = args.ffmpeg
            else:
                utils.warning('No FFmpeg argument. Using the default configuration.')
                ffmpeg = '-c:v copy -c:a copy -c:s copy'

            config['ffmpeg'] = ffmpeg
            config['download'] = download
            config['output'] = args.output
    return config


def main():
    parser = argparse.ArgumentParser(description='', epilog='', conflict_handler='resolve')
    parser.add_argument('--path', '-p', type=str, default=os.path.join('tmp'), help='Location of temporary files.')
    parser.add_argument('--id', '-i', type=str, help='Process ID.')
    parser.add_argument('--url', '-u', type=str, help='Link of master m3u8 file.')
    parser.add_argument('--extract', '-e', action='store_true', help='Get available video resolution.')
    parser.add_argument('--download', '-d', type=str, help='Download ID.')
    parser.add_argument('--tasks', '-t', type=int, default=5, help='Number of simultaneous downloads.')
    parser.add_argument('--ffmpeg', '-f', type=str, help='FFmpeg arguments.')
    parser.add_argument('--output', '-o', type=str, help='Output file path.')
    parser.add_argument('--log', '-l', action='store_true', default=False, help='Show process details.')
    parser.add_argument('--skip', '-s', action='store_true', default=False, help='Do not download if the video already exists.')
    parser.add_argument('--clear', '-c', action='store_true', default=False, help='Clean up all temporary files.')
    args = parser.parse_args()
    config = get_config(args)

    FFmpegHelper = AsyncFFmpegHelper.FFmpegHelper(config)
    if args.clear:
        FFmpegHelper.clear()
    elif args.extract:
        FFmpegHelper.extract()
    elif args.download:
        FFmpegHelper.download()
    else:
        parser.print_usage()
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
