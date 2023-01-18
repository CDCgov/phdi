# This script aggregates the information from 6 open source nickname
# files into a single compiled database. The repos from which these
# source files were downloaded can be found in the Acknowledgments
# section of the project's root README.

import pathlib

names_to_nicknames = {}

with open(pathlib.Path(__file__).parent / "nicknames.csv") as fp:
    i = 0
    for line in fp:
        if line.strip() != "":
            if i == 0:
                i += 1
                continue
            toks = line.strip().split(",")
            root_name = toks[1].strip().upper()
            if root_name not in names_to_nicknames:
                names_to_nicknames[root_name] = []
            names_to_nicknames[root_name].append(toks[2].strip().upper())

for f in ["names.csv", "male_diminutives.csv", "female_diminutives.csv"]:
    with open(pathlib.Path(__file__).parent / f) as fp:
        for line in fp:
            if line.strip() != "":
                root_name, nicknames = line.strip().split(",", 1)
                root_name = root_name.strip().upper()
                if root_name not in names_to_nicknames:
                    names_to_nicknames[root_name] = []
                for name in nicknames.strip().upper().split(","):
                    names_to_nicknames[root_name].append(name.strip())

with open(pathlib.Path(__file__).parent / "nick_to_name.csv") as fp:
    i = 0
    for line in fp:
        if line.strip() != "":
            if i == 0:
                i += 1
                continue
            nick, names = line.strip().split(",", 1)
            nick = nick.strip().upper()
            for name in names.strip().upper().split(","):
                if name.strip() not in names_to_nicknames:
                    names_to_nicknames[name.strip()] = []
                names_to_nicknames[name.strip()].append(nick)

with open(pathlib.Path(__file__).parent / "nicknames.txt") as fp:
    for line in fp:
        if line.strip() != "":
            toks = line.strip().upper().split()
            root_name = toks[0]
            if root_name not in names_to_nicknames:
                names_to_nicknames[root_name] = []
            for name in toks[1:]:
                if name.strip() != "":
                    names_to_nicknames[root_name].append(name.strip())

for name in names_to_nicknames:
    names_to_nicknames[name] = list(set(names_to_nicknames[name]))

with open(pathlib.Path(__file__).parent / "phdi_nicknames.csv", "w") as fp:
    names = names_to_nicknames.keys()
    names = sorted(names)
    for name in names:
        nickname_str = ",".join(names_to_nicknames[name])
        write_str = name + ":" + nickname_str
        fp.write(write_str + "\n")
