__module_name__ = 'ref_prototype'
import hexchat
import threading
import time

#match setup
def init_match():
    match = {
        'matchlink': '',
        'ref': '', #enter your username here
        'team1': '',
        'team2': '',
        'BOs': '',
        'players': {
            'team1_players': ['YuukiNoTsubasa'],
            'team2_players': ['']
        },
        'mappool': {},
        'picked_maps': [],
        'banned_maps': [],
        'teammode': '2',
        'scoremode': '3',
        'size': '4'
    }
    return match

#switch to room tab
def channel_switch(tab):
    """returns a context object"""
    return hexchat.find_context(channel = tab)

#create room
def create_room(acronym,team1,team2):
    """returns a tag of room channel"""
    hexchat.command('query -nofocus BanchoBot !mp make {}: ({}) vs ({})'.format(acronym,team1,team2))
    global roomhook
    roomhook = hexchat.hook_print('Focus tab', roomhandler)

#setup room
def setup_room(match,matchroom):
    """setup match and invites players"""
    matchroom.command('say !mp set {teammode} {scoremode} {size}'.format_map(match))
    matchroom.command('say !mp mods Freemod')
    players = []
    for key in match['players'].keys():
        for player in match['players'].get(key):
            players.append(player)
    for player in players:
        if player:
            matchroom.command('query -nofocus {} Your match is Ready! click the link below to join the match'.format(player))
            matchroom.command('say !mp invite {}'.format(player))

#retrieve match infos
def getmatchinfos(name,team1,team2):
    pass

#mappool configuration
mappoolsize = (5,3,3,3,2,1)
mapids = (123456,) #set mapids here

#generate a mappool
def generate_mappool(mapids,mappoolsize):
    """return a dictionary of mappool
        mapids is a tuple of beatmapIds
        mappoolsize is a tuple which consists of mappool mods and how many of them individually
        it should be formatted like this:
        mapppoolsize = ([NM],[HD],[HR],[DT],[FM],[TB])
        if you don't have mods which mentioned above, you should replace it by 0
        mappoolmods are used when creating keys of the maps"""

    mappoolmods = {
        '0':'NM',
        '1':'HD',
        '2':'HR',
        '3':'DT',
        '4':'FM',
        '5':'TB'
    }

    beatmaptags = ()
    for item in mappoolsize:
        flag = 0
        while flag < item:
            flag += 1
            beatmapTagElement = mappoolmods[item] + str(flag)
            beatmaptags.append(beatmapTagElement)
    return dict [beatmaptags,mapids]

#change map
def change_map(match,map_num,matchroom):
    """ mapmods are used when applying mods of the maps
        map_num is tag of a single beatmap, such as FM2"""
    mappool = match.get('mappool')
    picked_maps = match.get('picked_maps')
    banned_maps = match.get('banned_maps')
    mapmods = {
        'NM':'NF',
        'HD':'NF HD',
        'HR':'NF HR',
        'DT':'NF DT',
        'FM':'Freemod'
    }

    if map_num in mappool.keys() and map_num not in banned_maps:
        picked_maps.append(map_num)
        map_mod = map_num[:3]
        matchroom.command('say !mp mods {}'.format(mapmods[map_mod]))
        matchroom.command('say !mp map {}'.format(map_num))
        matchroom.command('say Nowplaying {}'.format(map_num))
    elif map_num in mappool.keys() and map_num in picked_maps:
        matchroom.command('say this map has been picked')
        matchroom.command('say please try again')
    else:
        matchroom.command('say this map does not exists or have been banned or picked')
        matchroom.command('say please try again')
        matchroom.command('say format is "pick [mapnumber]"')
        matchroom.command('say e.g. pick NM5')

#ban map
def ban_map(map_num,matchroom):
    if map_num in mappool.keys():
        banned_maps.append(map_num)
        matchroom.command('say {} is banned from mappool'.format(map_num))
    else:
        matchroom.command('say this map does not exists in this mappool!')
        matchroom.command('say please try again')
        matchroom.command('say format is "ban [mapnumber]"')
        matchroom.command('say e.g. ban NM5')

#handle messages
def handler(word, word_eol, userdata):
    """ when hooked, word should be returned with a list contains strings
        word[0] is username
        word[1] is what they said"""
    if not word:
        return hexchat.EAT_ALL
    elif word[0] == 'botstart':
        hexchat.unhook(bothook)
        global match
        match = init_match()
        match['team1'] = word[2]
        match['team2'] = word[3]
        create_room(word[1],word[2],word[3])
        return hexchat.EAT_HEXCHAT

def roomhandler(word, word_eol, userdata):
    """hook to the matchroom"""
    if not word:
        hexchat.unhook(roomhook)
        matchroom = hexchat.get_context()
        setup_room(match,matchroom)
        global messagehook
        messagehook = hexchat.hook_print('Channel Message',messagehandler)
        global yourmessagehook
        yourmessagehook = hexchat.hook_print('Your Message',messagehandler)

        return hexchat.EAT_NONE

def messagehandler(word, word_eol, userdata):
    matchroom = hexchat.get_context()
    if word[0] == 'BanchoBot':
        matchroom.prnt('Successfully caught BanchoBot said {}'.format(word[1]))
    elif word:
        matchroom.prnt('You said something')
    return hexchat.EAT_NONE

global bothook
bothook = hexchat.hook_command("BOTSTART", handler)
