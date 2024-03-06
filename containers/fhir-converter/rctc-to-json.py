import json
import re
import sys

import openpyxl

# arg list: 1) input file location/name 2) output file location/name
wb = openpyxl.load_workbook(sys.argv[1])
jsonData = {}
for sheet in wb.worksheets[2:]:
    ws = wb[sheet.title]
    title = sheet.title.replace("_", " ")
    title = re.sub(r" S\d", "", title)
    for val in ws.iter_rows(min_row=17, values_only=True):
        if val[0] is None:
            break
        else:
            jsonData[val[1]] = {
                "Type": title,
                "Name": val[0],
                "OID": val[1],
                "Code System": val[2],
                "Code System OID": val[3],
                "Status": val[4],
                "Condition Name": val[5],
                "Condition Code": val[6],
                "Condition Code System": val[7],
            }

with open(sys.argv[2], "w") as outfile:
    json.dump(jsonData, outfile)
