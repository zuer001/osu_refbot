__module_name__ = 'ref_prototype'
import hexchat
import threading
import time

#match setup
match = {
    'matchlink': '',
    'ref': '', #enter your username here
    'team1': '',
    'team2': '',
    'BOs': '',
    'players': {
        'team1_players': [''],
        'team2_players': ['']
    },
    'mappool': {}
}

#create room
def create_room(acronym,team1,team2):
    """returns a tag of room channel"""
    hexchat.command('query BanchoBot !mp make {}: ({}) vs ({})'.format(acronym,team1,team2))
    return hexchat.get_info('topic')

#switch to room tab
def channel_switch(tab):
    """returns a context object"""
    return hexchat.find_context(channel = tab)

#setup room
def setup_room(players,
    matchroom,
    teammode = '2',
    scoremode = '3',
    size = '4',
    ):
    """setup match and invites players"""
    matchroom.command('say !mp set {} {} {}'.format(teammode,scoremode,size))
    matchroom.command('say !mp mods Freemod')
    for player in players:
        matchroom.command('query -nofocus {} Your match is Ready! click the link below to join the match'.format(player))
        matchroom.command('say !mp invite {}'.format(player))

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
def change_map(mappool,map_num,matchroom):
    """ mapmods are used when applying mods of the maps
        map_num is tag of a single beatmap, such as FM2"""
    mapmods = {
        'NM':'NF',
        'HD':'NF HD',
        'HR':'NF HR',
        'DT':'NF DT',
        'FM':'Freemod'
    }

    if map_num in mappool.keys() and map_num not in banned_maps:
        map_mod = map_num[:3]
        matchroom.command('say !mp mods {}'.format(mapmods[map_mod]))
        matchroom.command('say !mp map {}'.format(map_num))
        matchroom.command('say Nowplaying {}'.format(map_num))
    else:
        matchroom.command('say this map does not exists or have been banned')
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

#set match state
def matchstate(state,matchroom):
    """ 0 for warmup state
        1 for Ban state
        2 for Pick state
        3 for lineup state
        4 for tiebreaker state
        5 for end state"""
    pass

#handle messages
def handler(word, word_eol, userdata):
    """ when hooked, word should be returned with a list contains strings
        word[0] is username
        word[1] is what they said"""

    create_room(word[1],word[2],word[3])

    return hexchat.EAT_ALL

hexchat.hook_command("BOTSTART", handler)
