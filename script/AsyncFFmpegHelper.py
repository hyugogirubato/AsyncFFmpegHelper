"""
Project: AsyncFFmpegHelper
Author: hyugogirubato
Script: AsyncFFmpegHelper.py
Version: v2022.02.19
"""

import asyncio
import os.path
import re
import shutil
import sys
import aiofiles
import aiohttp
import utils

SEGMENT = 'seg_{TYPE}{INDEX}.{EXTENSION}'
ENCRYPTION = 'encrypt_{TYPE}.key'
M3U8 = '{TYPE}.m3u8'


def _delete_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)


def _delete_file(path):
    if os.path.exists(path):
        os.remove(path)


def _get_file(path):
    if os.path.exists(path):
        file = open(path, 'r', encoding='utf-8')
        content = file.read()
        file.close()
        if content == '':
            _delete_file(path)
            return None
        else:
            return content
    else:
        return None


def _save_file(path, content):
    file = open(path, 'w', encoding='utf-8')
    file.write(content)
    file.close()


def _get_protocol(url):
    if url.startswith('https://'):
        return 'https'
    elif url.startswith('http://'):
        return 'http'
    else:
        utils.error('Unsupported or invalid protocol.')


def _get_path(config, name):
    path = os.path.join(config['path'], config['id'])
    if not os.path.exists(path):
        os.makedirs(path)
    return os.path.join(path, name)


def _async_download(config, files):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    sema = asyncio.BoundedSemaphore(config['tasks'])
    if sys.version_info[:2] == (3, 7):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    async def download_file(_file):
        _path = _file['path']
        _url = _file['url']
        _id = _file['id']
        _log = _file['log']
        _protocol = _file['protocol']
        _index = _file['index']
        _count = _file['count']

        if not os.path.exists(_path):
            try:
                data = None
                async with sema, aiohttp.ClientSession() as session:
                    if _log:
                        utils.log(f'[{_protocol} @ {_id}]', f'Opening `{_url}` for reading')

                    sys.stdout.write('count={0:<4} index={1:<4} progress={2:<6}\r'.format(
                        _count,
                        _index,
                        f'{round(_index / _count * 100)}%'
                    ))
                    sys.stdout.flush()
                    async with session.get(_url) as r:
                        if r.ok:
                            data = await r.read()

                if not data is None:
                    async with aiofiles.open(_path, 'wb') as outfile:
                        await outfile.write(data)
            except (GeneratorExit, AttributeError, RuntimeError) as e:
                pass
            except Exception as e:
                utils.error(f'Error opening connection `{_url}`', ignore=True)

    _tasks = list()
    count = len(files)
    for i in range(len(files)):
        url = files[i]['url']
        protocol = _get_protocol(url)
        _tasks.append(asyncio.gather(download_file({
            'path': files[i]['path'],
            'url': url,
            'id': config['id'],
            'log': config['log'],
            'protocol': protocol,
            'index': i + 1,
            'count': count
        })))

    try:
        loop.run_until_complete(asyncio.wait(_tasks))
        loop.run_until_complete(asyncio.sleep(2.0))
    except (Exception, KeyboardInterrupt) as e:
        utils.error('The download was interrupted.')
    finally:
        loop.close()


def _check_master(streams, data):
    for i in range(len(streams)):
        if streams[i]['resolution'] == data['resolution'] and streams[i]['bandwidth'] < data['bandwidth']:
            streams[i] = data
            return streams

    streams.append(data)
    return streams


def _get_master_streams(content):
    streams = list()
    items = content.split('\n')
    for i in range(len(items)):
        if items[i].startswith('#EXT-X-STREAM-INF:') and (i + 1) < len(items) and items[i + 1].startswith('http'):
            data = {
                'id': i,
                'bandwidth': int(items[i].split('BANDWIDTH=')[1].split(',')[0]),
                'resolution': int(items[i].split('RESOLUTION=')[1].split(',')[0].split('x')[1]),
                'url': items[i + 1].strip()
            }
            streams = _check_master(streams, data)
    return streams


def _get_master_content(config):
    path = _get_path(config, M3U8.replace('{TYPE}', 'master'))
    if not config['skip']:
        _delete_file(path)

    if not os.path.exists(path):
        files = list()
        files.append({
            'path': path,
            'url': config['url']
        })
        _async_download(config, files)

    content = _get_file(path)
    if content is None:
        utils.error('Error downloading master file.')
    return content


def get_index_content(config, url):
    path = _get_path(config, M3U8.replace('{TYPE}', 'index'))
    if not config['skip']:
        _delete_file(path)

    if not os.path.exists(path):
        files = list()
        files.append({
            'path': path,
            'url': url
        })
        _async_download(config, files)
    content = _get_file(path)
    if content is None:
        utils.error('Error downloading index file.')
    return content


def _build_tmp(config, content):
    tmp_master_encryption = ENCRYPTION.replace('{TYPE}', 'tmp_master')
    tmp_audio_encryption = ENCRYPTION.replace('{TYPE}', 'tmp_audio')
    tmp_index_encryption = ENCRYPTION.replace('{TYPE}', 'tmp_index')
    tmp_master = M3U8.replace('{TYPE}', 'tmp_master')
    tmp_audio = M3U8.replace('{TYPE}', 'tmp_audio')
    tmp_index = M3U8.replace('{TYPE}', 'tmp_index')

    _delete_file(_get_path(config, tmp_master_encryption))
    _delete_file(_get_path(config, tmp_audio_encryption))
    _delete_file(_get_path(config, tmp_index_encryption))
    _delete_file(_get_path(config, tmp_audio))
    _delete_file(_get_path(config, tmp_index))

    encryption = None
    audio = None
    stream = None
    items = content.split('\n')
    for i in range(len(items)):
        if items[i].startswith('#EXT-X-SESSION-KEY:'):
            url = items[i].split('URI="')[1].split('"')[0]
            encryption = {
                'data': items[i].replace(url, tmp_master_encryption),
                'path': _get_path(config, tmp_master_encryption),
                'url': url
            }
        elif items[i].startswith('#EXT-X-MEDIA:TYPE=AUDIO,'):
            group_id = items[i].split('GROUP-ID="')[1].split('"')[0].lower()
            name = items[i].split('NAME="')[1].split('"')[0]
            if group_id == 'audio':
                rate = name
            else:
                rate = group_id
            try:
                rate = int(re.sub('[^0-9]', '', rate))
            except Exception as e:
                rate = 128

            if audio is None or rate > audio['rate']:
                audio = {
                    'data': f'#EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="audio",NAME="AAC_und_ch2_{rate}kbps",CHANNELS="2",URI="{tmp_audio}"',
                    'path': _get_path(config, tmp_audio),
                    'url': items[i].split('URI="')[1].split('"')[0],
                    'rate': rate,
                    'type': 'audio'
                }
        elif i == config['download']:
            bandwidth = items[i].split('BANDWIDTH=')[1].split(',')[0]
            resolution = items[i].split('RESOLUTION=')[1].split(',')[0]
            codecs = items[i].split('CODECS="')[1].split('"')[0]
            stream = {
                'data': f'#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH={bandwidth},RESOLUTION={resolution},CODECS="{codecs}"',
                'path': _get_path(config, tmp_index),
                'file': tmp_index,
                'url': items[i + 1].strip(),
                'type': 'video'
            }

    if stream is None:
        utils.error('Unable to build index.')

    files = list()
    master = list()
    master.append('#EXTM3U')
    master.append('#EXT-X-VERSION:4')
    if not encryption is None:
        files.append(encryption)
        master.append(encryption['data'])

    if not audio is None:
        files.append(audio)
        master.append(audio['data'])
        stream['data'] += ',AUDIO="audio"'

    files.append(stream)
    master.append(stream['data'])
    master.append(stream['file'])
    _save_file(_get_path(config, tmp_master), '\n'.join(master))
    _async_download(config, files)

    files = list()
    if audio:
        if not os.path.exists(audio['path']):
            utils.error('The audio file is invalid.')
        files += _check_tmp(config, audio)
    if not os.path.exists(stream['path']):
        utils.error('The stream file is invalid.')
    files += _check_tmp(config, stream)
    return files


def _check_tmp(config, data):
    base_uri = str(data['url'].split('?')[0]).rsplit('/', 1)[0]
    content = _get_file(data['path'])
    items = content.split('\n')
    files = list()
    index = 0
    for i in range(len(items)):
        if items[i].startswith('#EXTINF:'):
            if not items[i + 1].startswith('http'):
                items[i + 1] = f'{base_uri}/{items[i + 1]}'

            if data['type'] == 'video':
                _type = 'v'
                extension = 'ts'
            else:
                _type = 'a'
                extension = 'aac'

            file = SEGMENT.replace('{INDEX}', str(index)).replace('{TYPE}', _type).replace('{EXTENSION}', extension)
            files.append({
                'path': _get_path(config, file),
                'url': items[i + 1]
            })
            items[i + 1] = file
            index += 1
        elif items[i].startswith('#EXT-X-KEY:'):
            if data['type'] == 'video':
                file = ENCRYPTION.replace('{TYPE}', 'tmp_index')
            else:
                file = ENCRYPTION.replace('{TYPE}', 'tmp_audio')

            url = items[i].split('URI="')[1].split('"')[0]
            files.append({
                'path': _get_path(config, file),
                'url': url
            })
            items[i] = items[i].replace(url, file)

    _save_file(data['path'], '\n'.join(items))
    return files


def _get_download_files(config):
    content = _get_master_content(config)
    streams = _get_master_streams(content)
    exist = False
    for stream in streams:
        if stream['id'] == config['download']:
            exist = True
            break

    if not exist:
        utils.error('Download ID does not exist.')

    return _build_tmp(config, content)


class FFmpegHelper:

    def __init__(self, config):
        self._config = config

    def extract(self):
        content = _get_master_content(self._config)
        streams = _get_master_streams(content)
        print('{0:<6} {1:<14} {2:<10}'.format('ID', 'Resolution', 'Bandwidth'))
        for stream in streams:
            print('{0:<6} {1:<14} {2:<10}'.format(stream['id'], stream['resolution'], stream['bandwidth']))

    def download(self):
        path = self._config['output']
        if os.path.exists(path):
            if self._config['skip']:
                utils.warning('File not downloaded because it already exists.')
                sys.exit(0)
            else:
                os.remove(path)
                utils.warning('Existing file deleted.')

        files = _get_download_files(self._config)
        _async_download(self._config, files)

        print('INFO: Merging video with ffmpeg in progress...')
        tmp_master = M3U8.replace('{TYPE}', 'tmp_master')
        command = ['ffmpeg', '-hide_banner', '-v', 'warning',
                   '-allowed_extensions', 'ALL', '-protocol_whitelist',
                   'file,http,https,tcp,tls,crypto',
                   '-i', f'"{_get_path(self._config, tmp_master)}"',
                   self._config['ffmpeg'], f'"{path}"']
        try:
            os.system(' '.join(command))
            print('INFO: The video has been downloaded.')
            _delete_dir(_get_path(self._config, ''))
        except Exception as e:
            utils.error('An error occurred while creating the video.')

    def clear(self):
        _delete_dir(self._config['path'])
