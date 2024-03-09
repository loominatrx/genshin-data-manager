from re import search
valid_language = ['English(US)', 'Chinese', 'Japanese', 'Korean']

def is_aria2_file(filename):
    return search('\\.aria2$', filename) == None

def is_audio_file(filename):
    return search('\\.pck$', filename) != None

def is_asset_block_file(filename):
    return search('\\.blk$', filename) != None or search('\\.json$', filename) != None or search('\\.dat$', filename) != None

def is_voice_file(filename):
    if search('^English\\(US\\)/.+\\.pck', filename) != None:
        return 'English(US)'
    elif search('^Chinese/.+\\.pck', filename) != None:
        return 'Chinese'
    elif search('^Korean/.+\\.pck', filename) != None:
        return 'Korean'
    elif search('^Japanese/.+\\.pck', filename) != None:
        return 'Japanese'

def is_cutscene_file(filename):
    return search('\\.usm$', filename) != None or search('\\.cuepoint$', filename) != None