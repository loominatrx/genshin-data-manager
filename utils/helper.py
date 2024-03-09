from . import log_util as util
from os import path, getcwd, exit

import subprocess

genshin_data = '/sdcard/Android/Data/com.miHoYo.GenshinImpact' # game files
working_dir = getcwd()

# files
base_rev_file = path.join(working_dir, 'base_revision')
audio_file = path.join(working_dir, 'audio_lang_14')
main_data_file = path.join(working_dir, 'res_versions_remote')
additional_data_file = path.join(working_dir, 'data_versions_remote')
game_version_file = path.join(working_dir, 'ScriptVersion')

def wait_for_device():
    util.log('Waiting for an Android device to be plugged in...')
    subprocess.run(['adb', 'wait-for-device'], stdout=subprocess.DEVNULL)

def is_config_file_present_on_android():
    return subprocess.run(['adb', 'shell', 'cd ' + genshin_data + '/files']) == None

def is_config_file_present_on_pc():
    return path.exists(base_rev_file) and path.exists(audio_file) and path.exists(base_rev_file) and path.exists(main_data_file) and path.exists(additional_data_file) and path.exists(game_version_file)

def retrieve_config_files_from_android():
    wait_for_device()

    util.log('Looking for Genshin Impact\'s download information...')
    genshin_folder_check = subprocess.run(['adb', 'shell', f'cd {genshin_data}/files'])
    if genshin_folder_check.stderr:
        util.error('You didn\'t run a data download on Genshin. Please do perform a data download, then exit the game.')
        exit(1)
    else:
        util.log('Data found!')

    util.log('Fetching base_revision...')
    subprocess.run(['adb', 'pull', genshin_data + '/files/base_revision', base_rev_file], stdout=subprocess.DEVNULL)
    util.log('Fetching audio_lang_14...')
    subprocess.run(['adb', 'pull', genshin_data + '/files/audio_lang_14', audio_file], stdout=subprocess.DEVNULL)
    util.log('Fetching data_versions_remote...')
    subprocess.run(['adb', 'pull', genshin_data + '/files/data_versions_remote', additional_data_file], stdout=subprocess.DEVNULL)
    util.log('Fetching res_versions_remote...')
    subprocess.run(['adb', 'pull', genshin_data + '/files/res_versions_remote', main_data_file], stdout=subprocess.DEVNULL)
    util.log('Fetching ScriptVersion...')
    subprocess.run(['adb', 'pull', genshin_data + '/files/ScriptVersion', game_version_file], stdout=subprocess.DEVNULL)