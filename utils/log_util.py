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
