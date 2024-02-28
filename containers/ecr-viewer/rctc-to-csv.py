import csv
import re
import sys

import openpyxl

# arg list: 1) input file location/name 2) output file location/name
excelFile = sys.argv[1] if len(sys.argv) > 1 else "RCTC_Release (2023-10-06).xlsx"
wb = openpyxl.load_workbook(excelFile)
data = [
    [
        "Type",
        "Name",
        "OID",
        "Code System",
        "Code System OID",
        "Status",
        "Condition Name",
        "Condition Code",
        "Condition Code System",
    ]
]

for sheet in wb.worksheets:
    ws = wb[sheet.title]
    title = sheet.title.replace("_", " ")
    title = re.sub(r"S\d", "", title)
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
            row = [
                title,
                val[0],
                val[1],
                val[2],
                val[3],
                val[4],
                val[5],
                val[6],
                val[7],
            ]
            data.append(row)

with open(
    sys.argv[2] if len(sys.argv) > 2 else "src/app/api/rctc.csv", "w", newline=""
) as file:
    print("Writing to csv")
    writer = csv.writer(file)
    writer.writerows(data)

print("Done")
