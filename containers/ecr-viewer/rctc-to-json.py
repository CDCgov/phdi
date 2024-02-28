import json
import re
import sys

import openpyxl

# arg list: 1) input file location/name 2) output file location/name
excelFile = sys.argv[1] if len(sys.argv) > 1 else "RCTC_Release (2023-10-06).xlsx"
wb = openpyxl.load_workbook(excelFile)
jsonData = {}
for sheet in wb.worksheets:
    ws = wb[sheet.title]
    title = sheet.title.replace("_", " ")
    title = re.sub(r" S\d", "", title)
    inTable = False
    for val in ws.iter_rows(values_only=True):
        if val == (
            "Name",
            "OID",
            "Code System",
            "Code System OID",
            "Status",
            "Condition Name",
            "Condition Code",
            "Condition Code System",
            "Condition Code System Version",
            "Additional context code",
            "Display Name",
        ):
            print("Starting", title)
            inTable = True
        elif inTable and val[0] is None:
            print("End of", title)
            break
        elif inTable:
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

with open(
    sys.argv[2] if len(sys.argv) > 2 else "src/app/api/rctc.json", "w"
) as outfile:
    print("Writing to json")
    json.dump(jsonData, outfile)

print("Done")
