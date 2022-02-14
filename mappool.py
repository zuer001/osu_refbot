# coding=utf-8
import openpyxl
import json
import re
table=openpyxl.load_workbook('mappool.xlsx')
ws=table['Team Roster']
team={}
for i in range(ws.max_row):
    name=ws.cell(row=i+1,column=1).value
    team[name]=[]
    for j in range(4):
        player=ws.cell(row=i+1,column=3+j).value
        if player is not None :
            if type(player) is int:
                player=str(player)
            player=player.replace(' ','_')
            team[name].append(player)
print(team)
with open("team.json","w") as f:
     json.dump(team,f)