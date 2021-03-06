__module_name__ = 'ref_prototype'

import re
import hexchat
import threading
import time
import json
import os

#match setup
def init_match(players_num=2,team1='',team2='',BOs=11,ban_num=4,teammode='2',scoremode='3',size='6'):
    with open("team.json", 'r') as load_f:
        load_dict = json.load(load_f)
    print(load_dict)
    team1_players=load_dict[team1]
    team2_players=load_dict[team2]
    match = {
        'matchlink': '',
        'players_num': players_num,
        'team1': team1,
        'team2': team2,
        'BOs': BOs,
        'players':{
            'team1_players': team1_players,
            'team2_players': team2_players
        },
        'team1_multipliers':[],
        'team2_multipliers':[],
        'mappool': {},
        'picked_maps': [],
        'banned_maps': [],
        'ban_num': ban_num,
        'teammode': teammode,
        'scoremode': scoremode,
        'size': size,
        'ref':['YuukiNoTsubasa','Truth_you_left']
    }
    print(team1_players)
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
global bantimer
global picktimer
global freemod
global forcemod
global lastgame
global bantimer_exists
global picktimer_exists
bantimer_exists=False
picktimer_exists=False
bantime=False
picktime=False
choosetime=False
starttime=False
rolltime=True
freemod=False
forcemod=False
next_to_pick=1
next_to_ban=1
mappoolsize = (5,3,3,4,2,1)
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
lastgame={
    'winner':'',
    'map':''
}

def debug(argument):
    #change match identities, such as players, mappools, etc..
    #eg: debug(match['mappool']['NM1'] = 1960429)
    #    meaning change NM1 bid to 1960429
    #    to call this function, use #debug [yourcommand]
    global match
    hexchat.prnt('supported match arguments are "players_num","team1","team2","BOs","players","team1_multipliers","team2_multipliers","picked_maps","banned_maps",etc')
    try:
        exec(argument)
        hexchat.prnt('execution went good!')
    except Exception as e:
        hexchat.prnt("you made some mistakes, weren't you?")

def ban_timer():
    matchroom=hexchat.get_context()
    global match
    global next_to_ban
    global bantimer
    global bantime
    global picktime
    if next_to_ban==1:
        match['ban_num']-=1
        if match['ban_num'] <= 0:
            bantime = False
            picktime = True
            matchroom.command('say Banning time finish! Team {}, type #pick [map] to continue'.format(match['team2']))
            matchroom.command('say You have 120 secs to pick a map!')
            matchroom.command('say !mp timer 120')
            picktimer = threading.Timer(120, pick_timer)
            picktimer.start()
        else:
            next_to_ban=2
            matchroom.command('say overtime! Team {}, Please ban a map in 120 secs'.format(match['team2']))
            matchroom.command('say !mp timer 120')
            bantimer = threading.Timer(120, ban_timer)
            bantimer.start()
    elif next_to_ban==2:
        match['ban_num'] -= 1
        if match['ban_num'] <= 0:
            bantime = False
            picktime = True
            matchroom.command('say Banning time finish! Team {}, type #pick [map] to continue'.format(match['team1']))
            matchroom.command('say You have 120 secs to pick a map!')
            matchroom.command('say !mp timer 120')
            picktimer = threading.Timer(120, pick_timer)
            picktimer.start()
        else:
            next_to_ban = 1
            matchroom.command('say overtime! Team {}, Please ban a map in 120 secs'.format(match['team1']))
            matchroom.command('say !mp timer 120')
            bantimer = threading.Timer(120, ban_timer)
            bantimer.start()
def pick_timer():
    matchroom = hexchat.get_context()
    global match
    global next_to_pick
    global picktimer
    if next_to_pick==1:
        next_to_pick=2
        matchroom.command('say overtime! Team {}, Please pick a map in 120 secs'.format(match['team2']))
        matchroom.command('say !mp timer 120')
        oldpicktimer=picktimer
        picktimer = threading.Timer(120, pick_timer)
        oldpicktimer.cancel()
        picktimer.start()
    elif next_to_pick == 2:
        next_to_pick = 1
        matchroom.command('say overtime! Team {}, Please pick a map in 120 secs'.format(match['team1']))
        matchroom.command('say !mp timer 120')
        oldpicktimer=picktimer
        picktimer = threading.Timer(120, pick_timer)
        oldpicktimer.cancel()
        picktimer.start()
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
def invite_players(player,matchroom):
    argument=[player,matchroom]
    def invite_player(player,matchroom):
        matchroom.command('say !mp invite {}'.format(player))
    invite_timer = threading.Timer(10,invite_player,args=argument)
    invite_timer.start()

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
    match['team1_multipliers']=[]
    match['team2_multipliers'] = []
    for i in range(len(match['players']['team1_players'])):
        match['team1_multipliers'].append(1)
    for i in range(len(match['players']['team2_players'])):
        match['team2_multipliers'].append(1)
    print(match['team1_multipliers'])
    print(match['team2_multipliers'])
#retrieve match infos
def getmatchinfos(name,team1,team2):
    pass



#generate a mappool
def generate_mappool():
    global mappoolsize
    global match
    with open("mappool.json", 'r') as load_f:
        load_dict = json.load(load_f)
    print(load_dict)
    match['mappool']=load_dict
#ban map
def ban_map(people,map,matchroom):
    global match
    if map in match['banned_maps']:
        matchroom.command('say this map has been banned')
        return
    if map not in match['mappool'].keys():
        matchroom.command('say not in mappool')
        return
    if 'TB' in map:
        matchroom.command('say TB cannot be banned')
        return
    global next_to_ban
    global bantime
    global picktime
    global bantimer
    global picktimer
    global picktimer_exists
    if next_to_ban ==1:
        if people in match['players']['team1_players']:
            match['banned_maps'].append(map)
            matchroom.command('say {} bans {}'.format(match['team1'],map))
            matchroom.command('say !mp aborttimer')
            bantimer.cancel()
            next_to_ban=2
            match['ban_num']-=1
            if match['ban_num']<=0:
                bantime=False
                picktime=True
                matchroom.command('say Banning time finish! Team {}, type #pick [map] to continue'.format(match['team1']))
                matchroom.command('say You have 120 secs to pick a map!')
                matchroom.command('say !mp timer 120')
                picktimer =threading.Timer(120,pick_timer)
                picktimer.start()
                picktimer_exists=True
            else:
                matchroom.command('say Team {}, Please ban a map in 120 secs'.format(match['team2']))
                matchroom.command('say !mp timer 120')
                bantimer = threading.Timer(120,ban_timer)
                bantimer.start()
            return
        else:
            matchroom.command('say wrong person to ban')
            return
    else:
        if people in match['players']['team2_players']:
            match['banned_maps'].append(map)
            matchroom.command('say {} bans {}'.format(match['team2'],map))
            matchroom.command('say !mp aborttimer')
            bantimer.cancel()
            next_to_ban=1
            match['ban_num']-=1
            if match['ban_num']<=0:
                bantime=False
                picktime=True
                matchroom.command('say Banning time finish! Team {}, type #pick [map] to continue'.format(match['team2']))
                matchroom.command('say You have 120 secs to pick a map!')
                matchroom.command('say !mp timer 120')
                picktimer =threading.Timer(120,pick_timer)
                picktimer.start()
                picktimer_exists = True
            else:
                matchroom.command('say Team {}, Please ban a map in 120 secs'.format(match['team1']))
                matchroom.command('say !mp timer 120')
                bantimer = threading.Timer(120,ban_timer)
                bantimer.start()
            return
        else:
            matchroom.command('say wrong person to ban')
            return

def pick_map(people,map,matchroom):
    global match
    global freemod
    global forcemod
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
        return
    global picktime
    global next_to_pick
    global starttime
    global picktimer
    global lastgame
    if next_to_pick==1:
        if people in match['players']['team1_players']:
            match['picked_maps'].append(map)
            matchroom.command('say {} picked {}'.format(match['team1'],map))
            matchroom.command('say !mp aborttimer')
            picktimer.cancel()
            next_to_pick=2
            picktime=False
            matchroom.command('say Picking time finish! Please Get your teams Ready in 180 secs!')
            starttime=True
            setmap(map,matchroom)
            lastgame['map']=map
        else:
            matchroom.command('say wrong person to pick')
    elif next_to_pick==2:
        if people in match['players']['team2_players']:
            match['picked_maps'].append(map)
            matchroom.command('say {} picked {}'.format(match['team2'],map))
            matchroom.command('say !mp aborttimer')
            picktimer.cancel()
            next_to_pick=1
            picktime=False
            matchroom.command('say Picking time finish! Please Get your teams Ready in 180 secs!')
            starttime=True
            setmap(map,matchroom)
            lastgame['map'] = map
        else:
            matchroom.command('say wrong person to pick')

def setmap(map,matchroom):
    global match
    global freemod
    global forcemod
    matchroom.command('say !mp map {}'.format(match['mappool'][map]))
    if 'FM' in map:
        matchroom.command('say !mp mods Freemod')
        freemod=True
        forcemod=False
    elif 'TB' in map:
        matchroom.command('say !mp mods Freemod')
        forcemod = True
        freemod = False
    elif 'NM' in map:
        matchroom.command('say !mp mods NF')
        forcemod=True
        freemod=False
    elif 'HD' in map:
        matchroom.command('say !mp mods NF HD')
        forcemod=True
        freemod=False
    elif 'HR' in map:
        matchroom.command('say !mp mods NF HR')
        forcemod=True
        freemod=False
    elif 'DT' in map:
        matchroom.command('say !mp mods NF DT')
        forcemod=True
        freemod=False
    matchroom.command('say !mp timer 180')

def pick_order(people,command,matchroom):
    global match
    global rollwinner
    global next_to_ban
    global next_to_pick
    global bantime
    global choosetime
    global bantimer
    global bantimer_exists
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
                matchroom.command('say Rolling time finish! Team {}, type #ban [map] to continue.'.format(match['team2']))
                matchroom.command('say You have 120 secs to ban a map')
                matchroom.command('say !mp timer 120')
                bantimer = threading.Timer(120,ban_timer)
                bantimer.start()
                bantimer_exists=True
                return
            elif command == '#secondpick':
                next_to_pick=2
                next_to_ban=1
                bantime=True
                choosetime=False
                matchroom.command('say {} choose second to pick'.format(match['team1']))
                matchroom.command('say Rolling time finish! Team {}, type #ban [map] to continue'.format(match['team1']))
                matchroom.command('say You have 120 secs to ban a map')
                matchroom.command('say !mp timer 120')
                bantimer = threading.Timer(120,ban_timer)
                bantimer.start()
                bantimer_exists=True
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
                matchroom.command('say Rolling time finish! Team {}, type #ban [map] to continue'.format(match['team1']))
                matchroom.command('say You have 120 secs to ban a map')
                matchroom.command('say !mp timer 120')
                bantimer = threading.Timer(120,ban_timer)
                bantimer.start()
                bantimer_exists=True
                return
            elif command == '#secondpick':
                next_to_pick=1
                next_to_ban=2
                bantime=True
                choosetime=False
                matchroom.command('say {} choose second to pick'.format(match['team2']))
                matchroom.command('say Rolling time finish! Team {}, type #ban [map] to continue'.format(match['team2']))
                matchroom.command('say You have 120 secs to ban a map')
                matchroom.command('say !mp timer 120')
                bantimer = threading.Timer(120,ban_timer)
                bantimer.start()
                bantimer_exists=True
                return

def greeting_event(word,matchroom):
    words=word.split(' ')
    space_num=len(words)-8
    people=words[0]
    for i in range(space_num):
        people=people+'_'+words[i+1]
    matchroom.command('say Greetings, {}! We are in Roll time right now, if you are captain, you can type !roll to roll for your team'.format(people))

def roll_event(word,matchroom):
    global match
    global next_to_ban
    global next_to_pick
    global team1_roll
    global team2_roll
    global choosetime
    global rollwinner
    global rolltime
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
            rolltime=False
            matchroom.command('say {} wins the roll'.format(match['team1']))
            matchroom.command('say {} please pick the ban/pick order'.format(match['team1']))
            matchroom.command('say type #firstpick to pick first or #secondpick to ban first')
        elif team2_roll>team1_roll:
            rollwinner=2
            choosetime=True
            rolltime=False
            matchroom.command('say {} wins the roll'.format(match['team2']))
            matchroom.command('say {} please pick the ban/pick order'.format(match['team2']))
            matchroom.command('say type #firstpick to pick first or #secondpick to ban first')
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
    global next_to_pick
    global picktimer
    global freemod
    global forcemod
    global lastgame
    picktime=True
    starttime=False
    freemod=False
    forcemod=False
    matchroom.command('say {}: {} points'.format(match['team1'],team1_score))
    matchroom.command('say {}: {} points'.format(match['team2'],team2_score))

    if team1_score>team2_score:
        team1_point+=1
        lastgame['winner'] ='team1'
        if team1_point == team2_point and team1_point == (match['BOs'] - 1) / 2:
            matchroom.command(
                'say {} {}-{} {} | The result is a tie, We have to play Tiebreaker'.format(match['team1'], team1_point,
                                                                                           team2_point, match['team2']))
            picktime = False
            starttime = True
            picktimer.cancel()
            team1_score=0
            team2_score=0
            setmap('TB', matchroom)
            return
        if team1_point == (match['BOs'] + 1) / 2:
            matchroom.command(
                'say {} {}-{} {} | {} wins the match! GGWP to both team!'.format(match['team1'], team1_point,
                                                                                 team2_point, match['team2'],
                                                                                 match['team1']))
            team1_score=0
            team2_score=0
            return
        matchroom.command('say {} {}-{} {} | next to pick: {}, you have 120 secs to pick a map'.format(match['team1'],team1_point,team2_point,match['team2'],match['team'+str(next_to_pick)]))
        matchroom.command('say !mp timer 120')
        picktimer = threading.Timer(120, pick_timer)
        picktimer.start()
    elif team2_score>team1_score:
        team2_point+=1
        lastgame['winner'] ='team2'
        if team1_point == team2_point and team1_point == (match['BOs'] - 1) / 2:
            matchroom.command(
                'say {} {}-{} {} | The result is a tie, We have to play Tiebreaker'.format(match['team1'], team1_point,
                                                                                           team2_point, match['team2']))
            picktime = False
            starttime = True
            picktimer.cancel()
            team1_score=0
            team2_score=0
            setmap('TB', matchroom)
            return
        if team2_point == (match['BOs'] + 1) / 2:
            matchroom.command(
                'say {} {}-{} {} | {} wins the match! GGWP to both team!'.format(match['team1'], team1_point,
                                                                                 team2_point, match['team2'],
                                                                                 match['team2']))
            team1_score=0
            team2_score=0
            return
        matchroom.command('say {} {}-{} {} | next to pick: {}, you have 120 secs to pick a map'.format(match['team1'],team1_point,team2_point,match['team2'],match['team'+str(next_to_pick)]))
        matchroom.command('say !mp timer 120')
        picktimer = threading.Timer(120, pick_timer)
        picktimer.start()

    team1_score=0
    team2_score=0

def count_event(word,matchroom):
    global match
    global real_player_num
    global team1_num
    global team2_num
    global freemod
    global forcemod
    mods=word.split('[')
    if 'Not Ready' in word:
        matchroom.command('say plz ready!')
        return
    if not forcemod and 'NoFail' not in mods[-1]:
        matchroom.command('say plz mod NF')
        return
    word_without_mod = mods[0]
    for i in range(len(mods) - 2):
        word_without_mod = word_without_mod + '[' + mods[i + 1]
    words = word_without_mod.split(' ')
    print(words)
    while words[-1]=='':
        del words[-1]
    print(words)
    space_num = len(words) - 10
    people = words[9]
    for i in range(space_num):
        people = people + '_' + words[i + 10]
    print(people)
    if freemod:
        if 'Hard' in mods[-1] or 'Flash' in mods[-1]or 'Hidden' in mods[-1]or 'Easy' in mods[-1]:
            if people in match['players']['team1_players']:
                team1_num+=1
                index = match['players']['team1_players'].index(people)
                match['team1_multipliers'][index] = 1
                if'Easy' in mods[-1]:
                    index=match['players']['team1_players'].index(people)
                    match['team1_multipliers'][index]=match['team1_multipliers'][index]*1.75
                if 'Flash' in mods[-1]:
                    index = match['players']['team1_players'].index(people)
                    match['team1_multipliers'][index] =match['team1_multipliers'][index]*2

            elif people in match['players']['team2_players']:
                team2_num+=1
                index = match['players']['team2_players'].index(people)
                match['team2_multipliers'][index] = 1
                if 'Easy' in mods[-1]:
                    index = match['players']['team2_players'].index(people)
                    match['team2_multipliers'][index] = match['team2_multipliers'][index]*1.75
                if 'Flash' in mods[-1]:
                    index = match['players']['team2_players'].index(people)
                    match['team2_multipliers'][index] = match['team2_multipliers'][index]*2
            real_player_num-=1
            if real_player_num==0:
                print('team1:{}'.format(team1_num))
                print('team2:{}'.format(team2_num))
                if team2_num==match['players_num'] and team1_num==match['players_num']:
                    matchroom.command('say !mp aborttimer')
                    matchroom.command('say !mp start 10')
                else:
                    matchroom.command('say inappropriate players')
        else:
            matchroom.command('say not right mod')
    else:
        if people in match['players']['team1_players']:
            team1_num += 1
            index = match['players']['team1_players'].index(people)
            match['team1_multipliers'][index] = 1
            if 'Easy' in mods[-1]:
                index = match['players']['team1_players'].index(people)
                match['team1_multipliers'][index] =  match['team1_multipliers'][index]*1.75
            if 'Flash' in mods[-1]:
                index = match['players']['team1_players'].index(people)
                match['team1_multipliers'][index] = match['team1_multipliers'][index]*2
        elif people in match['players']['team2_players']:
            team2_num += 1
            index = match['players']['team2_players'].index(people)
            match['team2_multipliers'][index] = 1
            if 'Easy' in mods[-1]:
                index = match['players']['team2_players'].index(people)
                match['team2_multipliers'][index] =  match['team2_multipliers'][index]*1.75
            if 'Flash' in mods[-1]:
                index = match['players']['team2_players'].index(people)
                match['team2_multipliers'][index] = match['team2_multipliers'][index]*2
        real_player_num -= 1
        if real_player_num == 0:
            print('team1:{}'.format(team1_num))
            print('team2:{}'.format(team2_num))
            if team2_num == match['players_num'] and team1_num == match['players_num']:
                matchroom.command('say !mp aborttimer')
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
    if people in match['players']['team1_players']:
        index = match['players']['team1_players'].index(people)
        score=score*match['team1_multipliers'][index]
        print(score)
        team1_score+=score
    elif people in match['players']['team2_players']:
        index = match['players']['team2_players'].index(people)
        score=score*match['team2_multipliers'][index]
        print(score)
        team2_score+=score

def rematch_event(matchroom):
    global match
    global team1_point
    global team2_point
    global lastgame
    global picktimer
    global picktime
    global starttime
    picktimer.cancel()
    picktime=False
    starttime=True
    setmap(lastgame['map'],matchroom)
    if lastgame['winner']=='team1':
        team1_point-=1
        matchroom.command('say rematch! {} {}-{} {}'.format(match['team1'],team1_point,team2_point,match['team2']))
    elif lastgame['winner']=='team2':
        team2_point-=1
        matchroom.command('say rematch! {} {}-{} {}'.format(match['team1'], team1_point, team2_point, match['team2']))

def replace_event(old,new,matchroom):
    global match
    if old in match['players']['team1_players']:
        for i,item in enumerate(match['players']['team1_players']):
            if item==old:
                match['players']['team1_players'][i]=new
                matchroom.command('say replaced {} to {}'.format(old,new))
                with open("team.json", 'r') as load_f:
                    load_dict = json.load(load_f)
                load_dict[match['team1']]=match['players']['team1_players']
                with open("team.json", "w") as f:
                    json.dump(load_dict, f)
    elif old in match['players']['team2_players']:
        for i,item in enumerate(match['players']['team2_players']):
            if item==old:
                match['players']['team2_players'][i]=new
                matchroom.command('say replaced {} to {}'.format(old, new))
                with open("team.json", 'r') as load_f:
                    load_dict = json.load(load_f)
                load_dict[match['team2']]=match['players']['team2_players']
                with open("team.json", "w") as f:
                    json.dump(load_dict, f)
    else:
        matchroom.command('say did not find {}'.format(old))
#handle messages
def handler(word, word_eol, userdata):
    """ when hooked, word should be returned with a list contains strings
        word[0] is username
        word[1] is what they said"""
    if not word:
        return hexchat.EAT_HEXCHAT
    elif word[0] == 'botstart':
        global match
        match = init_match(team1=word[2],team2=word[3])
        create_room(word[1],word[2],word[3])
        if len(word)>=5:
            match['BOs']=int(word[4])
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
        global match
        matchroom = hexchat.get_context()
        setup_room(match,matchroom)
    return hexchat.EAT_HEXCHAT

def messagehandler(word, word_eol, userdata):
    matchroom = hexchat.get_context()
    global bantime
    global picktime
    global picktimer
    global bantimer
    global match
    global starttime
    global rolltime
    global messagehook
    global yourmessagehook
    global highlighthook
    global bantimer_exists
    global picktimer_exists
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
        elif 'joined' in word[1] and rolltime:
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
            for i in range(len(match['team1_multipliers'])):
                match['team1_multipliers'][i] = 1
            for i in range(len(match['team2_multipliers'])):
                match['team2_multipliers'][i] = 1
        elif 'Slot' in word[1] :
            count_event(word[1],matchroom)
    elif word[0] in match['ref'] and command[0]=='#rematch':
        rematch_event(matchroom)
    elif word[0] in match['ref'] and command[0] == '#replace':
        replace_event(command[1],command[2],matchroom)
    elif word[0] in match['ref'] and command[0] == '#debug':
        debug(' '.join(command[1:]))
    elif command[0] == '#ban' and bantime:
        ban_map(word[0],command[1],matchroom)
    elif command[0] == '#pick' and picktime:
        pick_map(word[0],command[1],matchroom)
    elif command[0] == '#firstpick'or command[0] == '#secondpick':
        pick_order(word[0],command[0],matchroom)
    elif command[0] == '#stop' :
        if word[0] in match['ref']:
            hexchat.unhook(messagehook)
            hexchat.unhook(yourmessagehook)
            hexchat.unhook(highlighthook)
            if bantimer_exists:
                bantimer.cancel()
            if picktimer_exists:
                picktimer.cancel()
    return hexchat.EAT_NONE


bothook = hexchat.hook_command("BOTSTART", handler)
