import openpyxl
import json
table=openpyxl.load_workbook('mappool.xlsx')
sheetnames=table.get_sheet_names()
ws=table.get_sheet_by_name(sheetnames[0])
for i in range(ws.max_row):
    mod=ws.cell(i,1)