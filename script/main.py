"""
Project: AsyncFFmpegHelper
Author: hyugogirubato
Script: main.py
"""

import argparse
import os.path
import sys
import AsyncFFmpegHelper
import utils

VERSION = '2022.02.20'


# main_arg.py --download "11" --id "G2XU03VQ5" --url "https://..." --ffmpeg="-c:v copy -c:a copy -c:s copy" --output "video.mp4" --skip true
# main_arg.py --extract --id "G2XU03VQ5" --url "https://..." --skip true
# main_arg.py --clear

def get_config(args):
    config = {}
    config['path'] = args.path
    if args.version:
        print(f'AsyncFFmpegHelper {VERSION}')
        sys.exit(0)
    elif args.clear:
        pass
    elif args.extract or args.download:
        if not args.id:
            utils.error('No process id defined.')
        elif not args.url:
            utils.error('No url defined.')
        else:
            config['skip'] = args.skip
            config['log'] = args.log
            config['id'] = args.id
            config['url'] = args.url
            config['tasks'] = args.tasks
            if config['tasks'] <= 0:
                utils.error('Tasks count cannot be less than 1.')

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
                ffmpeg = ''

            config['ffmpeg'] = ffmpeg
            config['download'] = download
            config['output'] = args.output
    return config


def main():
    parser = argparse.ArgumentParser(
        description='FFmpeg helper to download HLS streams faster in asynchronous mode.',
        epilog='Full documentation at: <https://github.com/hyugogirubato/AsyncFFmpegHelper>',
        conflict_handler='resolve'
    )
    parser.add_argument('-v', '--version', action='store_true', default=False, help='Show script version.')
    parser.add_argument('-p', '--path', type=str, default=os.path.join('tmp'), help='Location of temporary files.')
    parser.add_argument('-i', '--id', type=str, help='Process ID.')
    parser.add_argument('-u', '--url', type=str, help='Link of master m3u8 file.')
    parser.add_argument('-e', '--extract', action='store_true', help='Get available video resolution.')
    parser.add_argument('-d', '--download', type=str, help='Download ID.')
    parser.add_argument('-t', '--tasks', type=int, default=5, help='Number of simultaneous downloads.')
    parser.add_argument('-f', '--ffmpeg', type=str, help='FFmpeg arguments.')
    parser.add_argument('-o', '--output', type=str, help='Output file path.')
    parser.add_argument('-l', '--log', action='store_true', default=False, help='Show process details.')
    parser.add_argument('-s', '--skip', action='store_true', default=False, help='Do not download if the video already exists.')
    parser.add_argument('-c', '--clear', action='store_true', default=False, help='Clean up all temporary files.')
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
