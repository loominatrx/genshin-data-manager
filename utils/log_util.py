# text styles
red = '\x1b[31m'
cyan = '\x1b[36m'
green = '\x1b[32m'
bold = '\x1b[1m'
reset = '\x1b[0m'

def log(str):
    print('{color}[i]: {reset}{str}{reset}'.format(color = cyan, reset = reset, str = str))

def error(str):
    print('{color}[!]: {reset}{str}{reset}'.format(color = red, reset = reset, str = str))

def new_input(str):
    return input('{color}[?]: {reset}{str}{reset}'.format(color = green, reset = reset, str = str))
