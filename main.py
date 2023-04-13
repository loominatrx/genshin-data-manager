from os import path, makedirs, system, walk
from os import name as os_name
from sys import exit

import subprocess
import json
import re

# text styles
red = '\033[0;31m'
cyan = '\u001b[0;36m'
green = '\u001b[0;32m'
bold = '\033[1m'
reset = '\033[0m'

# vars
update_link = 'https://autopatchhk.yuanshen.com/' # update server
genshin_data = '/sdcard/Android/Data/com.miHoYo.GenshinImpact' # game files

working_dir = path.dirname(__file__)

def log(str):
    print('{color}[i]: {reset}{str}{reset}'.format(color = cyan, reset = reset, str = str))

def error(str):
    print('{color}[!]: {reset}{str}{reset}'.format(color = red, reset = reset, str = str))

def new_input(str):
    return input('{color}[?]: {reset}{str}{reset}'.format(color = green, reset = reset, str = str))

def question(str):
    out = new_input(str + ' [y/n]: ')
    if out.lower() == 'y':
        return True
    elif out.lower() == 'n':
        return False
    else:
        error('Please input a valid response.')
        exit(1)

def choice(n, str):
    print('{color}[{num}]: {reset}{str}{reset}'.format(num = n, color = green, reset = reset, str = str))

def clear():
    if os_name == 'posix': system('clear')
    else: system('cls')

def wait_for_android_device():
    log('Waiting for android device...')
    subprocess.run(['adb', 'wait-for-device'], stdout=subprocess.DEVNULL)

def pull_files():
    wait_for_android_device()

    log('Checking for genshin folder...')
    result = subprocess.run(['adb', 'shell', 'cd ' + genshin_data + 'files'])
    if result.stderr:
        error('You didn\'t run perform a data download, don\'t you?\n   Please perform a data download, then exit the game.')
        exit(1)
    else:
        log('Found one!\n')

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

def download_resources():
    print('You need to install Genshin Impact on your Android device and RUN it for the first time.')
    print('Run the game, sign in to your HoYoVerse account, perform a data download, then cancel it.')
    print('\nAfter that, close the game, and plug your USB in and make sure you enabled USB debugging in developer options. This is done to check required files to download.')
    print(bold + 'Also, keep in mind that this will only work if you have an Android device!!!' + reset)

    input('\nPress enter to continue.')

    #######

    print('')
    if path.exists(working_dir + '/base_revision') and path.exists(working_dir + '/audio_lang_14') and path.exists('data_versions_remote') and path.exists('res_versions_remote') and path.exists(working_dir + '/ScriptVersion'):
        log('Files used to check game version are found.')
        response = question('Do you want to use them instead?')
        if response == False:
            pull_files()
        else:
            pass
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
    log('Parsing res_versions_remote and data_versions_remote...')
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
        log('Creating data directory...')
        makedirs('files')
        makedirs('files/AssetBundles/blocks')
        makedirs('files/VideoAssets/Android')
        makedirs('files/AudioAssets/')
        
    else:
        log('Checking for updates...')

        # TODO: do a checksum check from the information we've gathered
 
    print('')
    log('Performing resource download...')
    for file in resources:
        suffix = ''
        if re.search('\\.blk$', file['remoteName']):
            suffix = 'AssetBundles/'
        elif re.search('\\.usm$', file['remoteName']) or re.search('\\.cuepoint$', file['remoteName']):
            suffix = 'VideoAssets/'
        elif re.search('\\.pck$', file['remoteName']):
            suffix = 'AudioAssets/' 

        filepath = 'files/' + suffix + file['remoteName']
        if path.isfile(filepath) == False:
            dir = path.dirname(file['remoteName'])
            if dir != '':
                makedirs('files/' + suffix + dir, 0o777, True)
            
            subprocess.run(['aria2c', 
                '--out=' + filepath, '--file-allocation=prealloc', '--dir=' + working_dir,
                '--max-concurrent-downloads=8', '--max-connection-per-server=8',
                '--download-result=hide', '--continue=true', endpoint + suffix + file['remoteName']
            ])

    log('Downloading ' + genshin_audio_language + ' voice pack...') 
    for pck in audio_resources[genshin_audio_language]:
        filepath = 'files/AudioAssets/'+ pck['remoteName']

        if path.isfile(filepath) == False:
            subprocess.run(['aria2c',
                '--out=' + filepath, '--file-allocation=prealloc', '--dir=' + working_dir,
                '--max-concurrent-downloads=8', '--max-connection-per-server=8',
                '--download-result=hide', '--continue=true', endpoint + 'AudioAssets/' + pck['remoteName']
            ])
    
    main_menu('Download done! Some files aren\'t downloaded due to the game server not storing the file, but this is enough to run the game!')

def copy_resources():
    copy_voice_pack = question('Do you want to copy voice packs?')
    copy_cutscenes = question('Do you want to copy pre-rendered (video) cutscenes?')
    
    log('Do NOT UNPLUG or TURN OFF your device during this session!!!')
    wait_for_android_device()

    print('')
    log('Fetching audio language...\n')
    genshin_audio_language = open(working_dir + '/audio_lang_14', 'r').read()

    log('Begin pushing!\n')
    skipped_voice = False
    skipped_cutscene = False
    
    for root, _, files in walk(working_dir + '/files/'):
        if re.search('AudioAssets/' + genshin_audio_language + '^', root):
            if not copy_voice_pack:
                if not skipped_voice:
                    log('Skipping voice pack...')
                    skipped_voice = True

                continue
        if re.search('VideoAssets.+^', root):
            if not copy_cutscenes:
                if not skipped_cutscene:
                    log('Skipping cutscenes...')
                    skipped_cutscene = True
                    
                continue

        # mkdir if the folder don't exist
        subprocess.run(['adb', 'shell', 'mkdir', '-p', genshin_data + root.replace(working_dir, '')])
        if len(files) > 0:
            for file in files:
                f = path.join(root, file)
                dest = genshin_data + root.replace(working_dir, '') + '/' + file

                log('Copying' + f + ' to ' + dest)
                subprocess.run(['adb', 'push', f, dest])

    main_menu('Game files copied to your phone! Enjoy genshin without staring at the login screen any longer!')

def main_menu(custom_text='', greet_type='info' or 'error'):
    clear()
    print('---------\nGenshin Mobile Data Downloader\n---------')

    print('')

    if greet_type == 'info':
        log(custom_text)
    elif greet_type == 'error':
        error(custom_text)

    log('What do you want to do today?')

    print('')

    choice(1, 'Download game resources')
    choice(2, 'Copy game resources to your phone')

    print('')

    choice(0, 'Exit the console app')

    print('')

    c = new_input('Your choice: ')

    print('')

    if c == '1':
        download_resources()
    elif c == '2':
        copy_resources()
    elif c == '0':
        exit(0)
    else:
        main_menu('Invalid input.', 'error')

if __name__ == '__main__':
    main_menu('Welcome to genshin-data-manager!')
else:
    print('Please do not import this file, run it with python instead.')
    print('python main.py')
    exit()