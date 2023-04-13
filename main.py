from os import path, makedirs
from sys import exit

import subprocess
import json
import re

# text styles
red = '\033[0;31m'
cyan = '\033[0;36m'
green = '\033[0;32m'
bold = '\033[1m'
reset = '\033[0m'

# vars
update_link = 'https://autopatchhk.yuanshen.com/' # update server
genshin_data = '/sdcard/Android/Data/com.miHoYo.GenshinImpact/' # game files

working_dir = path.dirname(__file__)

def log(str):
    print('{color}[i]: {reset}{str}{reset}'.format(color = cyan, reset = reset, str = str))

def error(str):
    print('{color}[!]: {reset}{str}{reset}'.format(color = red, reset = reset, str = str))

def new_input(str):
    return input('{color}[?]: {reset}{str}{reset}'.format(color = green, reset = reset, str = str))

def pull_files():
    log('waiting for android device...')
    subprocess.run(['adb', 'wait-for-device'], stdout=subprocess.DEVNULL)

    log('checking for genshin folder...')
    result = subprocess.run(['adb', 'shell', 'cd ' + genshin_data + 'files'])
    if result.stderr:
        error('You didn\'t run perform a data download, don\'t you?\n   Please perform a data download, then exit the game.')
        exit(1)
    else:
        log('found one!\n')

    log('fetching base_revision...')
    subprocess.run(['adb', 'pull', genshin_data + 'files/base_revision'], stdout=subprocess.DEVNULL)
    log('fetching audio_lang_14...')
    subprocess.run(['adb', 'pull', genshin_data + 'files/audio_lang_14'], stdout=subprocess.DEVNULL)
    log('fetching data_versions_remote...')
    subprocess.run(['adb', 'pull', genshin_data + 'files/data_versions_remote'], stdout=subprocess.DEVNULL)
    log('fetching res_versions_remote...')
    subprocess.run(['adb', 'pull', genshin_data + 'files/res_versions_remote'], stdout=subprocess.DEVNULL)
    log('fetching ScriptVersion...')
    subprocess.run(['adb', 'pull', genshin_data + 'files/ScriptVersion'], stdout=subprocess.DEVNULL)

        
if __name__ == '__main__':

    # brief text
    print('---------\nGenshin Mobile Data Downloader\n---------')
    print('You need to install Genshin Impact on your Android device and RUN it for the first time.')
    print('Run the game, sign in to your HoYoVerse account, perform a data download, then cancel it.')
    print('\nAfter that, close the game, and plug your USB in and make sure you enabled USB debugging in developer options. This is done to check required files to download.')
    print(bold + 'Also, keep in mind that this will only work if you have an Android device!!!' + reset)

    input('\nPress enter to continue.')

    #######

    print('')
    if path.exists(working_dir + '/base_revision') and path.exists(working_dir + '/audio_lang_14') and path.exists('data_versions_remote') and path.exists('res_versions_remote') and path.exists(working_dir + '/ScriptVersion'):
        log('files used to check game version are found.')
        response = new_input('do you want to use them instead? [y/n]: ')
        if response.lower() == 'n': 
            pull_files()
        elif response.lower() == 'y':
            pass
        else:
            error('please input a valid response.')
            exit(1)
    else:
        pull_files()

    # read the file, then assign them in variables
    base_rev = open(working_dir + '/base_revision', 'r').read().split(' ')
    genshin_version = open(working_dir + '/ScriptVersion', 'r').read()
    genshin_audio_language = open(working_dir + '/audio_lang_14', 'r').read()
    genshin_version_code = base_rev[0]
    genshin_version_id = base_rev[1]
    
    # if the hotfix version is 0, use the 'major.minor' format instead of 'major.minor.hotfix'.
    if genshin_version.split('.')[2] == '0':
        __ver = genshin_version.split('.')
        __ver.pop()
        genshin_version = '.'.join(__ver)
    
    print('')
    log('genshin-data-downloader is now downloading data for version {version}_{version_code}_{version_id}'.format(version = genshin_version,version_code = genshin_version_code,version_id = genshin_version_id))

    endpoint = update_link + 'client_game_res/{version}_live/output_{version_code}_{version_id}/client/Android/'.format(
        version = genshin_version,
        version_code = genshin_version_code,
        version_id = genshin_version_id
    )

    # convert res_versions_remote to readable dictionary
    log('parsing res_versions_remote and data_versions_remote...')
    resources = []
    audio_resources = {
        'English(US)': [],
        'Korean': [],
        'Japanese': [],
        'Chinese': []
    }

    required_files_1 = open(working_dir + '/res_versions_remote', 'r').read().split('\n')
    # required_files_2 = open(working_dir + '/data_versions_remote', 'r').read().split('\n')

    for file in required_files_1:
        if file == '': continue
        json_file = json.loads(file)
        if re.search('^English\\(US\\)/.+\\.pck', json_file['remoteName']):
            audio_resources['English(US)'].append(json_file)
        elif re.search('^Korean/.+\\.pck', json_file['remoteName']):
            audio_resources['Korean'].append(json_file)
        elif re.search('^Japanese/.+\\.pck', json_file['remoteName']):
            audio_resources['Japanese'].append(json_file)
        elif re.search('^Chinese/.+\\.pck', json_file['remoteName']):
            audio_resources['Chinese'].append(json_file)
        else:
            resources.append(json_file)

    # for file in required_files_2:
    #     if file == '': continue
    #     json_file = json.loads(file)
    #     resources.append(json_file)

    # start download
    if not path.isdir('files'):
        log('creating data directory...')
        makedirs('files')
        makedirs('files/AssetBundles/blocks')
        makedirs('files/VideoAssets/Android')
        makedirs('files/AudioAssets/')
        
    else:
        log('checking for updates...')

        # TODO: do a checksum check from the information we've gathered
 
    print('')
    log('performing resource download...')
    for file in resources:
        suffix = ''
        if re.search('\\.blk$', file['remoteName']):
            suffix = 'AssetBundles/'
        elif re.search('\\.usm$', file['remoteName']) or re.search('\\.cuepoint$', file['remoteName']):
            suffix = 'VideoAssets/'
        elif re.search('\\.pck$', file['remoteName']):
            suffix = 'AudioAssets/' 

        filepath = working_dir + '/files/' + suffix + file['remoteName']
        if path.isfile(filepath) == False:
            dir = path.dirname(file['remoteName'])
            if dir != '':
                makedirs('files/' + suffix + dir, 0o777, True)
            
            subprocess.run(['aria2c', 
                '--out=' + filepath,
                '--max-concurrent-downloads=8', '--max-connection-per-server=8',
                '--download-result=hide', '--continue=true', endpoint + suffix + file['remoteName']
            ])

    log('downloading ' + genshin_audio_language + ' voice pack...') 
    for pck in audio_resources[genshin_audio_language]:
        filepath = working_dir + '/files/AudioAssets/'+ pck['remoteName']

        if path.isfile(filepath) == False:
            subprocess.run(['aria2c',
                '--out=' + filepath,
                '--max-concurrent-downloads=8', '--max-connection-per-server=8',
                '--downloads-result=hide', '--continue=true', endpoint + 'AudioAssets/' + pck['remoteName']
            ])
    log('done!')

    log('some files are not downloaded due to the game server not storing the files, but this is enough to get the game up and running!')
else:
    print('Please do not import this file, run it with python instead.')
    print('python main.py')
    exit()