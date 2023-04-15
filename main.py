from os import path, makedirs, walk
from sys import exit

import util

import subprocess
import json
import re

# text styles
bold = '\033[1m'
reset = '\033[0m'

# vars
update_link = 'https://autopatchhk.yuanshen.com/' # update server
genshin_data = '/sdcard/Android/Data/com.miHoYo.GenshinImpact' # game files

working_dir = path.dirname(__file__)

# files
base_rev_file = path.join(working_dir, 'base_revision')
audio_file = path.join(working_dir, 'audio_lang_14')
main_data_file = path.join(working_dir, 'res_versions_persist')
additional_data_file = path.join(working_dir, 'data_versions_persist')
game_version_file = path.join(working_dir, 'ScriptVersion')

def header():
    print('---------\nGenshin Mobile Data Downloader\n---------\n')

def pull_files():
    util.wait_for_android_device()

    util.log('Checking for genshin folder...')
    result = subprocess.run(['adb', 'shell', 'cd ' + genshin_data + '/files'])
    if result.stderr:
        util.error('You didn\'t run perform a data download, don\'t you?\n   Please perform a data download, then exit the game.')
        exit(1)
    else:
        util.log('Found one!\n')

    util.log('fetching base_revision...')
    subprocess.run(['adb', 'pull', genshin_data + '/files/base_revision', base_rev_file], stdout=subprocess.DEVNULL)
    util.log('fetching audio_lang_14...')
    subprocess.run(['adb', 'pull', genshin_data + '/files/audio_lang_14', audio_file], stdout=subprocess.DEVNULL)
    util.log('fetching data_versions_persist...')
    subprocess.run(['adb', 'pull', genshin_data + '/files/data_versions_persist', additional_data_file], stdout=subprocess.DEVNULL)
    util.log('fetching res_versions_persist...')
    subprocess.run(['adb', 'pull', genshin_data + '/files/res_versions_persist', main_data_file], stdout=subprocess.DEVNULL)
    util.log('fetching ScriptVersion...')
    subprocess.run(['adb', 'pull', genshin_data + '/files/ScriptVersion', game_version_file], stdout=subprocess.DEVNULL)

def parse_resource(which_resource):
    main_resources = []
    voice_resources = {
        'English(US)': [],
        'Korean': [],
        'Japanese': [],
        'Chinese': []
    }
    video_resources = []

    required_files_1 = open(main_data_file, 'r').read().split('\n')
    # required_files_2 = open(additional_data_file, 'r').read().split('\n') # additional ~200MB file that don't work unfortunately

    # separate them into lists
    for file in required_files_1:
        if file == '': continue
        json_file = json.loads(file)
        if util.is_voice_file(json_file['remoteName']) == 'English(US)' and which_resource == 'voice':
            voice_resources['English(US)'].append(json_file)
        elif util.is_voice_file(json_file['remoteName']) == 'Korean' and which_resource == 'voice':
            voice_resources['Korean'].append(json_file)
        elif util.is_voice_file(json_file['remoteName']) == 'Japanese' and which_resource == 'voice':
            voice_resources['Japanese'].append(json_file)
        elif util.is_voice_file(json_file['remoteName']) == 'Chinese' and which_resource == 'voice':
            voice_resources['Chinese'].append(json_file)
        elif util.is_cutscene_file(json_file['remoteName']) and which_resource == 'video':
            video_resources.append(json_file)
        elif (util.is_asset_block_file(json_file['remoteName']) or (util.is_voice_file(json_file['remoteName']) == None and util.is_audio_file(json_file['remoteName']))) and which_resource == 'main':
            main_resources.append(json_file)

    
    # for file in required_files_2:
    #     if file == '': continue
    #     json_file = json.loads(file)
    #     resources.append(json_file)

    
    if which_resource == 'main':
        return main_resources
    elif which_resource == 'voice':
        return voice_resources
    elif which_resource == 'video':
        return video_resources

def download_main_assets(endpoint, resources, force_update):
    util.log('Downloading main resources...')
    for file in resources:
        prefix = ''
        if re.search('\.blk$', file['remoteName']):
            prefix = 'AssetBundles/'
        elif re.search('\.pck$', file['remoteName']):
            prefix = 'AudioAssets/' 

        filepath = 'files/' + prefix + file['remoteName']
        if path.exists(filepath) == False or force_update == True or path.exists(filepath + '.aria2') == True:
            dir = path.dirname(file['remoteName'])
            if dir != '':
                makedirs('files/' + prefix + dir, 0o777, True)
            
            subprocess.run(['aria2c', 
                '--out=' + filepath, '--file-allocation=prealloc', '--dir=' + working_dir,
                '--max-concurrent-downloads=8', '--max-connection-per-server=8',
                '--download-result=hide', '--continue=true', '--check-integrity=true', '--checksum=md5=' + file['md5'],
                endpoint + prefix + file['remoteName']
            ])

def download_cutscene(endpoint, resources, force_update):
    util.log('Downloading cutscenes...')
    for video in resources:
        filepath = 'files/VideoAssets/' + video['remoteName']
        if path.exists(filepath) == False or force_update == True or path.exists(filepath + '.aria2') == True:
            
            subprocess.run(['aria2c', 
                '--out=' + filepath, '--file-allocation=prealloc', '--dir=' + working_dir,
                '--max-concurrent-downloads=8', '--max-connection-per-server=8',
                '--download-result=hide', '--continue=true', '--check-integrity=true', '--checksum=md5=' + video['md5'],
                endpoint + 'VideoAssets/' + video['remoteName']
            ])

def download_voice(endpoint, resources, force_update, voice_language):
    if voice_language == None:
        voice_language = open(audio_file, 'r').read()
        util.log('Using pulled audio_lang_14 file: ' + voice_language)
    else:
        util.log('Voice language overriden: ' + voice_language)
    
    util.log('Downloading ' + voice_language + ' voice pack...') 
    for pck in resources[voice_language]:
        filepath = 'files/AudioAssets/'+ pck['remoteName']

        if path.exists(filepath) == False or force_update == True or path.exists(filepath + '.aria2') == True:
            subprocess.run(['aria2c',
                '--out=' + filepath, '--file-allocation=prealloc', '--dir=' + working_dir,
                '--max-concurrent-downloads=8', '--max-connection-per-server=8',
                '--download-result=hide', '--continue=true', '--check-integrity=true', '--checksum=md5=' + pck['md5'],
                endpoint + 'AudioAssets/' + pck['remoteName']
            ])

def get_endpoint():
    # read the file, then assign them in variables
    base_rev = open(base_rev_file, 'r').read().split(' ')
    genshin_version = open(game_version_file, 'r').read()
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

def download_resources(download_bundles=True, download_voices=True, download_cutscenes=True, force_update=False):
    util.clear()
    header()

    print('You need to install Genshin Impact on your Android device and RUN it for the first time.')
    print('Run the game, sign in to your HoYoVerse account, perform a data download, then cancel it.')
    print('\nAfter that, close the game, and plug your USB in and make sure you enabled USB debugging in developer options.\nThis is done to check required files to download.')
    print(bold + 'Also, keep in mind that this will only work if you have an Android device!!!' + reset)

    input('\nPress enter to continue or Ctrl+C to quit.')

    #######

    print('')

    if force_update:
        util.clear()
        header()

        util.error(bold + 'WARNING!')
        print('You are attempting to force update the game data.')
        print('Force-update checks every file\'s integrity and download a new one if the file is considered old.')
        print('Integrity check isn\'t enforced on normal download to prevent any slowdowns.\n')
        print(bold + 'Only use this if you really want to update your game files!' + reset)

        input('\nPress enter to proceed or Ctrl+C to quit.')

    print('')

    if force_update == False:
        if (path.exists(base_rev_file) and path.exists(audio_file) and path.exists(additional_data_file) and path.exists(main_data_file) and path.exists(game_version_file)):
            util.log('Files used to check game version are found.')
            response = util.question('Do you want to use them instead?')
            if response == False:
                pull_files()
            else:
                pass

    pull_files()
    
    endpoint = get_endpoint()

    # convert res_versions_remote to readable dictionary
    util.log('Parsing res_versions_persist and data_versions_persist...')
    # start download
    if not path.isdir('files'):
        util.log('Creating data directory...')
        makedirs('files', 0o777, True)
        makedirs('files/AssetBundles/blocks', 0o777, True)
        makedirs('files/VideoAssets/Android', 0o777, True)
        makedirs('files/AudioAssets/', 0o777, True)

    # TODO: do a checksum check from the information we've gathered
 
    print('')
    util.log('Performing resource download...')
    if force_update: util.log('Force re-download: ENABLED')
    if download_voices:
        voice_resources = parse_resource('voice')
        download_voice(endpoint, voice_resources, force_update)
    else:
        util.log('Skipping voice pack...')

    if download_bundles == True:
        main_resources = parse_resource('main')
        download_main_assets(endpoint, main_resources, force_update)
    else:
        util.log('Skipping main resources...')

    if download_cutscenes:
        video_resources = parse_resource('video')
        download_cutscene(endpoint, video_resources, force_update)
    else:
        util.log('Skipping cutscenes...')
    
    main_menu('Download done! Some files aren\'t downloaded due to the game server not storing the file, but this is enough to run the game!')

def copy_resources():
    util.clear()
    header()

    print('Before copying the game data to your phone, make sure you have enough storage')
    print('on your phone. genshin-data-manager will fail to copy the game data and spamming you errors')
    print('on the console if you don\'t do so.\n')

    input('Press enter to proceed or Ctrl+C to quit.')
    print('')

    util.wait_for_android_device()
    util.log('Android device detected!')
    copy_voice_pack = util.question('Do you want to copy voice packs?')
    copy_cutscenes = util.question('Do you want to copy pre-rendered (video) cutscenes?')
    
    util.log('Do NOT UNPLUG or TURN OFF your device during this session!!!\n')
    util.log('Fetching audio language...')
    genshin_audio_language = open(audio_file, 'r').read()

    util.log('Begin pushing!\n')
    skipped_voice = False
    skipped_cutscene = False
    
    for root, _, files in walk(path.join(working_dir, 'files')):
        # mkdir if the folder don't exist
        subprocess.run(['adb', 'shell', 'mkdir', '-p', genshin_data + root.replace(working_dir, '').replace('\\', '/') + '/'])
        if len(files) > 0:
            for file in files:
                if (re.search('\.usm$', file) or re.search('\.cuepoint$', file)) and copy_cutscenes == False:
                    if skipped_cutscene == False:
                        util.log('Skipping cutscenes...')
                        skipped_cutscene = True
                    continue
                elif re.search(re.escape(genshin_audio_language), root) and re.search('\.pck$', file) and copy_voice_pack == False:
                    if skipped_voice == False:
                        util.log('Skipping voice pack...')
                        skipped_voice = True
                    continue

                f = path.join(root, file)
                dest = genshin_data + root.replace(working_dir, '').replace('\\', '/') + '/' + file
                
                util.log('Copying ' + f + ' to ' + dest)
                subprocess.run(['adb', 'push', f, dest])

    main_menu('Game files copied to your phone! Enjoy genshin without staring at the login screen any longer!')

def about_page():
    util.clear()
    header()

    print('Quoting from the repo:')
    print('This python script allows you to download and manage Genshin Impact\'s game data in your PC!\n')
    print('You can use this to quickly restore the game data in case you accidentally delete the game data\nand don\'t want to spend hours on redownloading 20GB+ worth of data.\n')
    print('Currently, it only supports full data download (not selective download) and\ncopying ALL required game data to your Android phone.')
    print('You can choose not to copy the voice audio and/or the video cutscene, but it will ruin your experience\nif you don\'t know what you\'re doing.\n')

    # free software notice
    print('----------\n')
    print('genshin-data-manager  Copyright (C) 2023  loominatrx/loominagit')
    print('This program comes with ABSOLUTELY NO WARRANTY.')
    print('This is free software, and you are welcome to redistribute it')
    print('under certain conditions.')

    input('\nPress enter to go back to main menu.')
    main_menu('Welcome to genshin-data-manager!')

def download_voice_pack_prompt():
    util.clear()
    header()
    util.log('Which voice language you want to download?\n')

    util.choice(1, 'English (US)')
    util.choice(2, 'Chinese')
    util.choice(3, 'Korean')
    util.choice(4, 'Japanese\n')

    language = util.new_input('Your choice: ')
    force_update = util.question('Do you want to perform a force-update? Answer n if this is new download.')

    if language == '1':
        language = 'English(US)'
    elif language == '2':
        language = 'Chinese'
    elif language == '3':
        language = 'Korean'
    elif language == '4':
        language = 'Japanese'
    else:
        util.log('Invalid choice.')
        exit(0)
    
    download_voice(get_endpoint(), parse_resource('voice'), force_update, language)

    main_menu(language + ' voice pack has been downloaded! Enjoy your favorite character in ' + language + '! :D')

def main_menu(custom_text='', greet_type='info'):
    util.clear()
    header()

    if greet_type == 'info':
        util.log(custom_text)
    elif greet_type == 'error':
        util.error(custom_text)

    util.log('What do you want to do today?\n')

    util.choice(1, 'Download ALL game resources')
    util.choice(2, 'Force-update ALL game resources\n')
    util.choice(3, 'Copy game resources to your phone\n')
    util.choice(4, 'Download voice packs')
    util.choice(5, 'Download specific game data\n')

    util.choice(9, 'About this app')
    util.choice(0, 'Exit the console app\n')

    print('---\n')

    c = util.new_input('Your choice: ')

    print('')

    if c == '1':
        download_resources()
    elif c == '2':
        download_resources(force_update=True)
    elif c == '3':
        copy_resources()
    elif c == '4':
        download_voice_pack_prompt()
    elif c == '5':
        util.clear()
        header()
        download_bundles = util.question('Do you want to download the main resources?')
        download_voices = util.question('Do you want to download voice resources? (default language: ' + open(audio_file, 'r').read() + ')')
        download_cutscenes = util.question('Do you want to download cutscenes?')
        print('')
        force_update = util.question('Do you want to force-update all those assets?')

        download_resources(download_bundles, download_voices, download_cutscenes, force_update)
    elif c == '9':
        about_page()
    elif c == '0':
        util.log('See you next time!')
        exit(0)
    else:
        main_menu('Invalid input.', 'error')

if __name__ == '__main__':
    main_menu('Welcome to genshin-data-manager!')
else:
    print('Please do not import this file, run it with python instead.')
    print('python main.py')
    exit()