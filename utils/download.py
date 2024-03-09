from os import path
from . import check, helper, log_util as util

import json
import re
import subprocess

update_link = 'https://autopatchhk.yuanshen.com/' # update server

# text styles
bold = '\033[1m'
reset = '\033[0m'

# filenames
main_assets_filename = 'main_assets.txt'
cutscenes_filename = 'cutscenes.txt'

def get_endpoint():
    # read the file, then assign them in variables
    base_rev = open(helper.base_rev_file, 'r').read().split(' ')
    genshin_version = open(helper.game_version_file, 'r').read()
    genshin_version_code = base_rev[0]
    genshin_version_id = base_rev[1]
    
    # if the hotfix version is 0, use the 'major.minor' format instead of 'major.minor.hotfix'.
    if genshin_version.split('.')[2] == '0':
        __ver = genshin_version.split('.')
        __ver.pop()
        genshin_version = '.'.join(__ver)
    
    print('')
    util.log('genshin-data-downloader is now downloading data for version {version}_{version_code}_{version_id}'.format(version = genshin_version,version_code = genshin_version_code,version_id = genshin_version_id))

    return update_link + 'client_game_res/{version}_live/output_{version_code}_{version_id}/client/Android/'.format(
        version = genshin_version,
        version_code = genshin_version_code,
        version_id = genshin_version_id
    )

endpoint = get_endpoint()

def generate_main_assets_list(force_update=False):
    util.log('Generating main assets list...')

    a2filename = path.join(helper.working_dir, main_assets_filename)
    a2file = None

    if path.exists(a2filename) and force_update:
        a2file = open(a2filename, 'w+')
        a2file.write('')
    elif path.exists(a2filename):
        util.error('Main asset list has already generated.')
        return
    else:
        a2file = open(a2filename, 'x+')

    content = ''
    file = open(helper.main_data_file, 'r').read().split('\n')
    for f in file:
        if f == '': continue
        json_file = json.loads(f)
        prefix = ''
        if (check.is_asset_block_file(json_file['remoteName']) or (check.is_voice_file(json_file['remoteName']) == None and check.is_audio_file(json_file['remoteName']))):
            if re.search('\\.blk$', json_file['remoteName']):
                prefix = 'AssetBundles/'
            elif re.search('\\.pck$', json_file['remoteName']):
                prefix = 'AudioAssets/' 

            filepath = 'files/' + prefix + json_file['remoteName']
            content = f'{content}{endpoint + prefix + json_file['remoteName']}\n    out={filepath}\n    dir={helper.working_dir}\n    checksum=md5={json_file['md5']}\n\n'
    
    a2file.write(content)

    return main_assets_filename

def generate_voice_list(language='English(US)', force_update=False):
    if not (language in check.valid_language):
        util.error('Invalid voice language')
        return

    util.log(f'Generating {language} voice list...')

    name = f'voice.{language}.txt'
    a2filename = path.join(helper.working_dir, name)
    a2file = None

    if path.exists(a2filename) and force_update:
        a2file = open(a2filename, 'w+')
        a2file.write('')
    elif path.exists(a2filename):
        util.error('Main asset list has already generated.')
        return
    else:
        a2file = open(a2filename, 'x+')

    content = ''
    file = open(helper.main_data_file, 'r').read().split('\n')
    for f in file:
        if f == '': continue
        json_file = json.loads(f)
        if check.is_audio_file(json_file['remoteName']) and check.is_voice_file(json_file['remoteName']) == language:
            filepath = 'files/AudioAssets/'+ json_file['remoteName']
            content = f'{content}{endpoint + 'AudioAssets/' + json_file['remoteName']}\n    out={filepath}\n    dir={helper.working_dir}\n    checksum=md5={json_file['md5']}\n\n'
    
    a2file.write(content)

    return name

def generate_cutscene_list(force_update=False):
    util.log('Generating cutscene list...')

    a2filename = path.join(helper.working_dir, cutscenes_filename)
    a2file = None

    if path.exists(a2filename) and force_update:
        a2file = open(a2filename, 'w+')
        a2file.write('')
    elif path.exists(a2filename):
        util.error('Main asset list has already generated.')
        return
    else:
        a2file = open(a2filename, 'x+')

    content = ''
    file = open(helper.main_data_file, 'r').read().split('\n')
    for f in file:
        if f == '': continue
        json_file = json.loads(f)
        if check.is_cutscene_file(json_file['remoteName']):
            filepath = 'files/VideoAssets/' + json_file['remoteName']
            content = f'{content}{endpoint + 'VideoAssets/' + json_file['remoteName']}\n    out={filepath}\n    dir={helper.working_dir}\n    checksum=md5={json_file['md5']}\n\n'
    
    a2file.write(content)

    return cutscenes_filename

def generate_all_voice_list(force_update=False):
    files = []
    for lang in check.valid_language:
        gen_file = generate_voice_list(lang, force_update)
        files.append(gen_file)
    
    return files

def gen_all(voice_language='English(US)', force_update=False):
    generate_main_assets_list(force_update)
    generate_voice_list(voice_language, force_update)
    generate_cutscene_list(force_update)
    

def download_file_from_aria2script(file='main_assets.txt'):
    subprocess.Popen(['aria2c', '--no-conf', '--async-dns=false', '--console-log-level=warn',
        '--log-level=info', '--log=aria2_download.log', '--file-allocation=prealloc', 
        '--max-concurrent-downloads=8', '--max-connection-per-server=8', '--download-result=hide', 
        '--continue=true', '--check-integrity=true', '-R',
        f'-i{path.join(helper.working_dir, file)}'
    ])
