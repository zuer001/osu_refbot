__module_name__ = 'ref_prototype'

import re

import hexchat
import threading
import time

#match setup
def init_match():
    match = {
        'matchlink': '',
        'ref': '', #enter your username here
        'players_num':1,
        'team1': '',
        'team2': '',
        'BOs': 7,
        'players':{
            'team1_players': ['YuukiNoTsubasa'],
            'team2_players': ['Truth_you_left']
        },
        'mappool': {},
        'picked_maps': [],
        'banned_maps': [],
        'ban_num':2,
        'teammode': '2',
        'scoremode': '3',
        'size': '4',
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
global highlighthook
global bantime
global picktime
global choosetime
global starttime
global mappoolsize
global team1_roll
global team2_roll
global rollwinner
global team1_num
global team2_num
global team1_score
global team2_score
global team1_point
global team2_point
global real_player_num
global rolltime
bantime=False
picktime=False
choosetime=False
starttime=False
rolltime=True
next_to_pick=1
next_to_ban=1
mappoolsize = (5,3,3,3,2,1)
team1_roll=-1
team2_roll=-1
rollwinner=0
team1_num=0
team2_num=0
team1_score=0
team2_score=0
team1_point=0
team2_point=0
real_player_num=0
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
            match['mappool'][name]=index*10+i+1
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
    if 'TB' in map:
        matchroom.command('say TB cannot be banned')
    global next_to_ban
    global bantime
    global picktime
    if next_to_ban ==1:
        if people in match['players']['team1_players']:
            match['banned_maps'].append(map)
            matchroom.command('say {} banned'.format(map))
            next_to_ban=2
            match['ban_num']-=1
            if match['ban_num']<=0:
                bantime=False
                picktime=True
                matchroom.command('say Banning time finish! Teams, type #pick [map] to continue')
                matchroom.command('say You have 120 secs to pick a map!')
            return
        else:
            matchroom.command('say wrong person to ban')
            return
    else:
        if people in match['players']['team2_players']:
            match['banned_maps'].append(map)
            matchroom.command('say {} banned'.format(map))
            next_to_ban=1
            match['ban_num']-=1
            if match['ban_num']<=0:
                bantime=False
                picktime=True
                matchroom.command('say Banning time finish! Teams, type #pick [map] to continue')
                matchroom.command('say You have 120 secs to pick a map!')
            return
        else:
            matchroom.command('say wrong person to ban')
            return
def pick_map(people,map,matchroom):
    global match
    if map in match['banned_maps']:
        matchroom.command('say this map has been banned')
        return
    if map in match['picked_maps']:
        matchroom.command('say this map has been picked')
        return
    if map not in match['mappool'].keys():
        matchroom.command('say not in mappool')
        print(match)
        return
    if 'TB' in map:
        matchroom.command('say TB cannot be picked')
    global picktime
    global next_to_pick
    global starttime
    if next_to_pick==1:
        if people in match['players']['team1_players']:
            match['picked_maps'].append(map)
            matchroom.command('say {} picked'.format(map))
            next_to_pick=2
            picktime=False
            matchroom.command('say Picking time finish! Please Get your teams Ready in 180 secs!')
            starttime=True
            setmap(map,matchroom)
        else:
            matchroom.command('say wrong person to pick')
    elif next_to_pick==2:
        if people in match['players']['team2_players']:
            match['picked_maps'].append(map)
            matchroom.command('say {} picked'.format(map))
            next_to_pick=1
            picktime=False
            matchroom.command('say Picking time finish! Please Get your teams Ready in 180 secs!')
            starttime=True
            setmap(map,matchroom)
        else:
            matchroom.command('say wrong person to pick')
def setmap(map,matchroom):
    global match
    matchroom.command('say !mp map {}'.format(match['mappool'][map]))
    if 'FM' in map or 'TB' in map:
        matchroom.command('say !mp mods Freemod')
    elif 'NM' in map:
        matchroom.command('say !mp mods NF')
    elif 'HD' in map:
        matchroom.command('say !mp mods NF HD')
    elif 'HR' in map:
        matchroom.command('say !mp mods NF HR')
    elif 'DT' in map:
        matchroom.command('say !mp mods NF DT')
def pick_order(people,command,matchroom):
    global match
    global rollwinner
    global next_to_ban
    global next_to_pick
    global bantime
    global choosetime
    if choosetime == False:
        return

    if rollwinner == 1:
        if people not in match['players']['team1_players']:
            matchroom.command('say wrong person to choose')
            return
        else:
            if command == '#firstpick':
                next_to_ban=2
                next_to_pick=1
                bantime=True
                choosetime=False
                matchroom.command('say {} choose first to pick'.format(match['team1']))
                matchroom.command('say Rolling time finish! Teams, type #ban [map] to continue')
                return
            elif command == '#secondpick':
                next_to_pick=2
                next_to_ban=1
                bantime=True
                choosetime=False
                matchroom.command('say {} choose second to pick'.format(match['team1']))
                matchroom.command('say Rolling time finish! Teams, type #ban [map] to continue')
                return
    elif rollwinner == 2:
        if people not in match['players']['team2_players']:
            matchroom.command('say wrong person to choose')
            return
        else:
            if command == '#firstpick':
                next_to_ban=1
                next_to_pick=2
                bantime=True
                choosetime=False
                matchroom.command('say {} choose first to pick'.format(match['team2']))
                matchroom.command('say Rolling time finish! Teams, type #ban [map] to continue')
                return
            elif command == '#secondpick':
                next_to_pick=1
                next_to_ban=2
                bantime=True
                choosetime=False
                matchroom.command('say {} choose second to pick'.format(match['team2']))
                matchroom.command('say Rolling time finish! Teams, type #ban [map] to continue')

def greeting_event(word,matchroom):
    words=word.split(' ')
    space_num=len(words)-4
    people=words[0]
    for i in range(space_num):
        people=people+'_'+words[i+1]
    matchroom.command('say Greetings! {} We are in Roll time right now, if you are captain, you can type !roll to roll for your team')

def roll_event(word,matchroom):
    global match
    global next_to_ban
    global next_to_pick
    global team1_roll
    global team2_roll
    global choosetime
    global rollwinner
    words=word.split(' ')
    space_num=len(words)-4
    people=words[0]
    for i in range(space_num):
        people=people+'_'+words[i+1]
    print(people)
    if people in match['players']['team1_players'] and team1_roll == -1:
        team1_roll=int(words[-2])
        print(team1_roll)
    if people in match['players']['team2_players'] and team2_roll == -1:
        team2_roll=int(words[-2])
        print(team2_roll)
    if team1_roll !=  -1 and team2_roll != -1:
        if team1_roll>team2_roll:
            rollwinner=1
            choosetime=True
            matchroom.command('say {} wins the roll'.format(match['team1']))
        elif team2_roll>team1_roll:
            rollwinner=2
            choosetime=True
            matchroom.command('say {} wins the roll'.format(match['team2']))
        else:
            team1_roll=-1
            team2_roll=-1
            matchroom.command('say TIE! please roll again')

def finish_event(word,matchroom):
    global picktime
    global starttime
    global team1_point
    global team2_point
    global match
    global team1_score
    global team2_score
    picktime=True
    starttime=False
    if team1_score>team2_score:
        team1_point+=1
        matchroom.command('say {}-{}'.format(team1_point,team2_point))
    elif team2_score>team1_score:
        team2_point+=1
        matchroom.command('say {}-{}'.format(team1_point, team2_point))
    if team1_point==team2_point and team1_point==(match['BOs']-1)/2:
        matchroom.command('say TB now')
        picktime=False
        setmap('TB1',matchroom)
def count_event(word,matchroom):
    global match
    global real_player_num
    global team1_num
    global team2_num
    words = word.split(' ')
    print(len(words))
    if 'Host' in word:
        space_num=len(words)-15
        if 'Team Red' in word:
            space_num-=1
        people=words[9]
        for i in range(space_num):
            people=people+'_'+words[i+10]
        print(people)
        if people in match['players']['team1_players']:
            team1_num+=1
        elif people in match['players']['team2_players']:
            team2_num+=1
    else:
        print(words)
        space_num = len(words) - 13
        if 'Team Red' in word:
            space_num-=1
        people = words[9]
        for i in range(space_num):
            people = people + '_' + words[i + 10]
        print(people)
        if people in match['players']['team1_players']:
            team1_num+=1
        elif people in match['players']['team2_players']:
            team2_num+=1
    real_player_num-=1
    if real_player_num==0:
        print('team1:{}'.format(team1_num))
        print('team2:{}'.format(team2_num))
        if team2_num==match['players_num'] and team1_num==match['players_num']:
            matchroom.command('say !mp start 10')
        else:
            matchroom.command('say inappropriate players')
def score_event(word):
    global match
    global team1_score
    global team2_score
    words = word.split(' ')
    space_num = len(words) - 6
    people = words[0]
    for i in range(space_num):
        people = people + '_' + words[i + 1]
    print(people)
    score=int(re.findall(r'\d+',words[-2])[0])
    print(score)
    if people in match['players']['team1_players']:
        team1_score+=score
    elif people in match['players']['team2_players']:
        team2_score+=score
#handle messages
def handler(word, word_eol, userdata):
    """ when hooked, word should be returned with a list contains strings
        word[0] is username
        word[1] is what they said"""
    if not word:
        return hexchat.EAT_HEXCHAT
    elif word[0] == 'botstart':
        global match
        match = init_match()
        match['team1'] = word[2]
        match['team2'] = word[3]
        create_room(word[1],word[2],word[3])
        global messagehook
        messagehook = hexchat.hook_print('Channel Message',messagehandler)
        global yourmessagehook
        yourmessagehook = hexchat.hook_print('Your Message',messagehandler)
        global highlighthook
        highlighthook=hexchat.hook_print('Channel Msg Hilight', messagehandler)
    return hexchat.EAT_HEXCHAT

def roomhandler(word, word_eol, userdata):
    """hook to the matchroom"""
    if not word:
        matchroom = hexchat.get_context()
        setup_room(match,matchroom)
    return hexchat.EAT_HEXCHAT


def messagehandler(word, word_eol, userdata):
    matchroom = hexchat.get_context()
    global bantime
    global picktime
    global match
    global starttime
    global rolltime
    command = word[1].split(' ')
    print(word[0])
    print(word[1])
    if 'BanchoBot' in word[0]:
        if 'rolls' in word[1] and rolltime:
            roll_event(word[1],matchroom)
        elif 'are ready' in word[1] and starttime:
            matchroom.command('say !mp settings')
        elif 'has finished' in word[1] and starttime:
            finish_event(word[1],matchroom)
        elif 'joined' in word[1]:
            greeting_event(word[1],matchroom)
        elif 'finished playing' in word[1] and starttime:
            score_event(word[1])
        elif 'Players:' in word[1] and starttime:
            global real_player_num
            global team1_num
            global team2_num
            real_player_num=int(command[1])
            team1_num=0
            team2_num=0
        elif 'Slot' in word[1] :
            count_event(word[1],matchroom)
    elif command[0] == '#ban' and bantime:
        ban_map(word[0],command[1],matchroom)
    elif command[0] == '#pick' and picktime:
        pick_map(word[0],command[1],matchroom)
    elif command[0] == '#firstpick'or command[0] == '#secondpick':
        pick_order(word[0],command[0],matchroom)
    return hexchat.EAT_NONE


bothook = hexchat.hook_command("BOTSTART", handler)
