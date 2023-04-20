from os import system, name
from re import search

import subprocess

# text styles
red = '\033[0;31m'
cyan = '\u001b[0;36m'
green = '\u001b[0;32m'
bold = '\033[1m'
reset = '\033[0m'

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
    if name == 'posix': system('clear')
    else: system('cls')

def wait_for_android_device():
    log('Waiting for android device...')
    subprocess.run(['adb', 'wait-for-device'], stdout=subprocess.DEVNULL)

def is_aria2_file(filename):
    return search('\.aria2$', filename) == None

def is_audio_file(filename):
    return search('\.pck$', filename) != None

def is_asset_block_file(filename):
    return search('\.blk$', filename) != None or search('\.json$', filename) != None or search('\.dat$', filename) != None

def is_voice_file(filename):
    if search('^English\\(US\\)/.+\.pck', filename) != None:
        return 'English(US)'
    elif search('^Chinese/.+\.pck', filename) != None:
        return 'Chinese'
    elif search('^Korean/.+\.pck', filename) != None:
        return 'Korean'
    elif search('^Japanese/.+\.pck', filename) != None:
        return 'Japanese'

def is_cutscene_file(filename):
    return search('\.usm$', filename) != None or search('\.cuepoint$', filename) != None

