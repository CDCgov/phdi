import json
import re
import sys

import openpyxl

# arg list: 1) input file location/name 2) output file location/name
wb = openpyxl.load_workbook(sys.argv[1])
jsonData = {}
jsonData_expansion = {}
top_rows_buffer = 17
tables_buffer = 7

for sheet in wb.worksheets[2:]:
    ws = wb[sheet.title]
    title = sheet.title.replace("_", " ")
    title = re.sub(r" S\d", "", title)
    end_grouping = None

    # Grouping List
    for i, val in enumerate(ws.iter_rows(min_row=top_rows_buffer, values_only=True)):
        if val[0] is None:
            end_grouping = i + 17
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

    # Expansion List
    for val in ws.iter_rows(min_row=(end_grouping + tables_buffer), values_only=True):
        if val[0] is None:
            break
        else:
            jsonData_expansion[val[1]] = {
                "Type": title,
                "Member OID": val[0],
                "Code": val[1],
                "Descriptor": val[2],
                "Code System": val[3],
                "Version": val[4],
                "Status": val[5],
                "Remap Info": val[6],
            }

with open(sys.argv[2], "w") as outfile1, open(sys.argv[3], "w") as outfile2:
    json.dump(jsonData, outfile1)

    json.dump(jsonData_expansion, outfile2)
