from os import system, name
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