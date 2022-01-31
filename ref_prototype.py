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
        'players':{
            'team1_players': ['YuukiNoTsubasa'],
            'team2_players': ['']
        },
        'mappool': {},
        'picked_maps': [],
        'banned_maps': [],
        'ban_num':1,
        'teammode': '2',
        'scoremode': '3',
        'size': '4'
    }
    return match

#switch to room tab
global next_to_ban
global next_to_pick
global bothook
global roomhook
global match
global messagehook
global yourmessagehook
global bantime
global picktime
global mappoolsize
bantime=True
picktime=False
next_to_pick=1
next_to_ban=1
mappoolsize = (5,3,3,3,2,1)
def channel_switch(tab):
    """returns a context object"""
    return hexchat.find_context(channel = tab)

#create room
def create_room(acronym,team1,team2):
    """returns a tag of room channel"""
    hexchat.command('query -nofocus BanchoBot !mp make {}: ({}) vs ({})'.format(acronym,team1,team2))
    generate_mappool()
    global roomhook
    roomhook = hexchat.hook_print('Open Context', roomhandler)

#setup room
def setup_room(match,matchroom):
    """setup match and invites players"""
    if '#mp' not in matchroom.get_info('channel'):
        return
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



#generate a mappool
def generate_mappool():
    global mappoolsize
    global match
    mapname=['NM','HD','HR','DT','FM','TB']
    index=0
    for num in mappoolsize:
        for i in range(num):
            name=mapname[index]+str(i+1)
            match['mappool'][name]=123456
        index+=1
#ban map
def ban_map(people,map,matchroom):
    global match
    if map in match['banned_maps']:
        matchroom.command('say this map has been banned')
        return
    if map not in match['mappool'].keys():
        matchroom.command('say not in mappool')
        print(match)
        return
    global next_to_ban
    global bantime
    global picktime
    if next_to_ban ==1:
        if people in match['players']['team1_players']:
            match['banned_maps'].append(map)
            matchroom.prnt('{}banned'.format(map))
            next_to_ban=2
            match['ban_num']-=1
            if match['ban_num']<=0:
                bantime=False
                picktime=True
            return
        else:
            matchroom.command('say wrong person to ban')
            return
    else:
        if people in match['players']['team2_players']:
            match['banned_maps'].append(map)
            matchroom.prnt('{}banned'.format(map))
            next_to_ban=1
            match['ban_num']-=1
            if match['ban_num']<=0:
                bantime=False
                picktime=True
            return
        else:
            matchroom.command('say wrong person to ban')
            return
#handle messages
def handler(word, word_eol, userdata):
    """ when hooked, word should be returned with a list contains strings
        word[0] is username
        word[1] is what they said"""
    if not word:
        return hexchat.EAT_ALL
    elif word[0] == 'botstart':
        global match
        match = init_match()
        match['team1'] = word[2]
        match['team2'] = word[3]
        create_room(word[1],word[2],word[3])
        return hexchat.EAT_HEXCHAT

def roomhandler(word, word_eol, userdata):
    """hook to the matchroom"""
    if not word:
        matchroom = hexchat.get_context()
        setup_room(match,matchroom)
        global messagehook
        messagehook = hexchat.hook_print('Channel Message',messagehandler)
        global yourmessagehook
        yourmessagehook = hexchat.hook_print('Your Message',messagehandler)

        return hexchat.EAT_ALL


def messagehandler(word, word_eol, userdata):
    matchroom = hexchat.get_context()
    global bantime
    global picktime
    if '#ban' in word[1] and bantime:
        command = word[1].split(' ')
        ban_map(word[0],command[1],matchroom)

    return hexchat.EAT_NONE


bothook = hexchat.hook_command("BOTSTART", handler)
