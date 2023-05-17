import unicodedata

"""
The Double Metaphone phonetic encoding algorithm is an improvement to the
phonetic representation algorithm Soundex, commonly used to identify what an
English name "sounds like." However, rather than produce an exact phonetic
description of a name, Double Metaphone produces an intentionally approximate
phonetic representation, in order to account for the way speakers vary their
pronunciations and misspell or otherwise vary words and names. It also
returns both a primary and a secondary encoding for a string (hence the
name "Double" Metaphone), which accounts for some ambiguous cases as well as
for multiple variants of surnames with common ancestry. Double Metaphone is
capable of accounting for irregularities in the spelling and phonetics of
English, Slavic, Germanic, Celtic, Greek, French, Italian, Spanish, Chinese,
and more.
"""

VOWELS = ["A", "E", "I", "O", "U", "Y"]
SILENT_STARTERS = ["GN", "KN", "PN", "WR", "PS"]


class DoubleMetaphone(object):
    """
    A Double Metaphone parsing object capable of performing the double
    coding algorithm on a given input string.
    """

    def __init__(self):
        self.position = 0
        self.primary_phone = ""
        self.secondary_phone = ""
        # next is set to a tuple of the next characters in the primary and
        # secondary codes and to indicate how many characters to move forward
        # in the string.  The secondary code letter is given only when it is
        # different than the primary.
        self.next = (None, 1)

    def __call__(self, string: str):
        return self.parse(string)

    def check_word_start(self):
        # Skip silent letters when they start a word (because they're not
        # phonetic if they're silent)
        if self.word.get_letters(0, 2) in SILENT_STARTERS:
            self.position += 1
        # Starting with 'X' frequently pronounced 'Z' e.g. 'Xavier'
        if self.word.get_letters(0) == "X":
            # 'Z' maps to 'S'
            self.primary_phone = self.secondary_phone = "S"
            self.position += 1

    def process_vowel(self):
        self.next = (None, 1)

        # All starting vowels map to 'A'
        if self.position == self.word.start_index:
            self.next = ("A", 1)

    def process_b(self):
        # "-mb", e.g., "dumb", already accounted for, see 'M'
        if self.word.buffer[self.position + 1] == "B":
            self.next = ("P", 2)
        else:
            self.next = ("P", 1)

    def process_c(self):
        buffer = self.word.buffer
        position = self.position
        start_index = self.word.start_index

        # Handle some germanic linguistics
        if (
            position > start_index + 1
            and buffer[position - 2] not in VOWELS
            and buffer[position - 1 : self.position + 2] == "ACH"
            and buffer[position + 2] not in ["I"]
            and (
                buffer[position + 2] not in ["E"]
                or buffer[position - 2 : position + 4] in ["BACHER", "MACHER"]
            )
        ):
            self.next = ("K", 2)

        # Special case 'CAESAR'
        elif (
            position == start_index
            and buffer[start_index : start_index + 6] == "CAESAR"
        ):
            self.next = ("S", 2)

        # Italian 'chianti'
        elif buffer[position : position + 4] == "CHIA":
            self.next = ("K", 2)
        elif buffer[position : position + 2] == "CH":
            # e.g. 'michael'
            if position > start_index and buffer[position : position + 4] == "CHAE":
                self.next = ("K", "X", 2)
            elif (
                position == start_index
                and (
                    buffer[position + 1 : position + 6] in ["HARAC", "HARIS"]
                    or buffer[position + 1 : position + 4]
                    in ["HOR", "HYM", "HIA", "HEM"]
                )
                and buffer[start_index : start_index + 5] != "CHORE"
            ):
                self.next = ("K", 2)

            # Germanic, greek, or other phonetic 'ch' for 'kh' sound
            elif (
                buffer[start_index : start_index + 4] in ["VAN ", "VON "]
                or buffer[start_index : start_index + 3] == "SCH"
                or buffer[position - 2 : position + 4] in ["ORCHES", "ARCHIT", "ORCHID"]
                or buffer[position + 2] in ["T", "S"]
                or (
                    (
                        buffer[position - 1] in ["A", "O", "U", "E"]
                        or position == start_index
                    )
                    and (
                        buffer[position + 2]
                        in ["L", "R", "N", "M", "B", "H", "F", "V", "W", " "]
                    )
                )
            ):
                self.next = ("K", 2)
            else:
                if position > start_index:
                    if buffer[start_index : start_index + 2] == "MC":
                        self.next = ("K", 2)
                    else:
                        self.next = ("X", "K", 2)
                else:
                    self.next = ("X", 2)

        # e.g, 'czerny'
        elif (
            buffer[position : position + 2] == "CZ"
            and buffer[position - 2 : position + 2] != "WICZ"
        ):
            self.next = ("S", "X", 2)

        # e.g., 'focaccia'
        elif buffer[position + 1 : position + 4] == "CIA":
            self.next = ("X", 3)

        # Double 'C', but not if e.g. 'McClellan'
        elif buffer[position : position + 2] == "CC" and not (
            position == (start_index + 1) and buffer[start_index] == "M"
        ):
            # 'bellocchio' but not 'bacchus'
            if (
                buffer[position + 2] in ["I", "E", "H"]
                and buffer[position + 2 : position + 4] != "HU"
            ):
                # 'accident', 'accede' 'succeed'
                if (
                    position == (start_index + 1) and buffer[start_index] == "A"
                ) or buffer[position - 1 : position + 4] in ["UCCEE", "UCCES"]:
                    self.next = ("KS", 3)

                # 'bacci', 'bertucci', other italian
                else:
                    self.next = ("X", 3)
            else:
                self.next = ("K", 2)

        elif buffer[position : position + 2] in ["CK", "CG", "CQ"]:
            self.next = ("K", 2)
        elif buffer[position : position + 2] in ["CI", "CE", "CY"]:
            # Italian vs. English
            if buffer[position : position + 3] in ["CIO", "CIE", "CIA"]:
                self.next = ("S", "X", 2)
            else:
                self.next = ("S", 2)
        else:
            # Name set in 'mac caffrey', 'mac gregor'
            if buffer[position + 1 : position + 3] in [" C", " Q", " G"]:
                self.next = ("K", 3)
            else:
                if buffer[position + 1] in ["C", "K", "Q"] and buffer[
                    position + 1 : position + 3
                ] not in ["CE", "CI"]:
                    self.next = ("K", 2)

                # Default sound for 'C'
                else:
                    self.next = ("K", 1)

    def process_d(self):
        if self.word.buffer[self.position : self.position + 2] == "DG":
            # e.g. 'edge'
            if self.word.buffer[self.position + 2] in ["I", "E", "Y"]:
                self.next = ("J", 3)
            else:
                self.next = ("TK", 2)
        elif self.word.buffer[self.position : self.position + 2] in ["DT", "DD"]:
            self.next = ("T", 2)
        else:
            self.next = ("T", 1)

    def process_f(self):
        if self.word.buffer[self.position + 1] == "F":
            self.next = ("F", 2)
        else:
            self.next = ("F", 1)

    def process_g(self):
        buffer = self.word.buffer
        position = self.position
        start_index = self.word.start_index
        if buffer[position + 1] == "H":
            if position > start_index and buffer[position - 1] not in VOWELS:
                self.next = ("K", 2)
            elif position < (start_index + 3):
                # 'Ghislane', 'Ghiradelli'
                if position == start_index:
                    if buffer[position + 2] == "I":
                        self.next = ("J", 2)
                    else:
                        self.next = ("K", 2)

            # Parker's rule for e.g., 'Hugh'
            elif (
                (
                    position > (start_index + 1)
                    and buffer[position - 2] in ["B", "H", "D"]
                )
                or (
                    position > (start_index + 2)
                    and buffer[position - 3] in ["B", "H", "D"]
                )
                or (position > (start_index + 3) and buffer[position - 4] in ["B", "H"])
            ):
                self.next = (None, 2)

            else:
                # e.g., 'laugh', 'McLaughlin', 'cough', 'gough', 'rough', 'tough'
                if (
                    position > (start_index + 2)
                    and buffer[position - 1] == "U"
                    and buffer[position - 3] in ["C", "G", "L", "R", "T"]
                ):
                    self.next = ("F", 2)
                else:
                    if position > start_index and buffer[position - 1] != "I":
                        self.next = ("K", 2)

        elif buffer[position + 1] == "N":
            if (
                position == (start_index + 1)
                and buffer[start_index] in VOWELS
                and not self.word.is_slavo_germanic
            ):
                self.next = ("KN", "N", 2)

            else:
                # Not e.g. 'cagney'
                if (
                    buffer[position + 2 : position + 4] != "EY"
                    and buffer[position + 1] != "Y"
                    and not self.word.is_slavo_germanic
                ):
                    self.next = ("N", "KN", 2)
                else:
                    self.next = ("KN", 2)

        # e.g. 'Tagliaro'
        elif (
            buffer[position + 1 : position + 3] == "LI"
            and not self.word.is_slavo_germanic
        ):
            self.next = ("KL", "L", 2)

        # -ges-,-gep-,-gel-, -gie- at beginning
        elif position == start_index and (
            buffer[position + 1] == "Y"
            or buffer[position + 1 : position + 3]
            in ["ES", "EP", "EB", "EL", "EY", "IB", "IL", "IN", "IE", "EI", "ER"]
        ):
            self.next = ("K", "J", 2)

        # -ger-,  -gy-
        elif (
            (buffer[position + 1 : position + 3] == "ER" or buffer[position + 1] == "Y")
            and buffer[start_index : start_index + 6]
            not in ["DANGER", "RANGER", "MANGER"]
            and buffer[position - 1] not in ["E", "I"]
            and buffer[position - 1 : position + 2] not in ["RGY", "OGY"]
        ):
            self.next = ("K", "J", 2)

        # Italian e.g, 'Biaggi'
        elif buffer[position + 1] in ["E", "I", "Y"] or buffer[
            position - 1 : position + 3
        ] in ["AGGI", "OGGI"]:
            # Germanic
            if (
                buffer[start_index : start_index + 4] in ["VON ", "VAN "]
                or buffer[start_index : start_index + 3] == "SCH"
                or buffer[position + 1 : position + 3] == "ET"
            ):
                self.next = ("K", 2)

            else:
                # Always soft if following the French ending
                if buffer[position + 1 : position + 5] == "IER ":
                    self.next = ("J", 2)
                else:
                    self.next = ("J", "K", 2)

        elif buffer[position + 1] == "G":
            self.next = ("K", 2)
        else:
            self.next = ("K", 1)

    def process_h(self):
        # Keep if self.word.start_index & before vowel, or between 2 vowels
        if (
            self.position == self.word.start_index
            or self.word.buffer[self.position - 1] in VOWELS
        ) and self.word.buffer[self.position + 1] in VOWELS:
            self.next = ("H", 2)
        else:
            self.next = (None, 1)

    def process_j(self):
        buffer = self.word.buffer
        position = self.position
        start_index = self.word.start_index

        # Spanish, 'Jose', 'Jacinto', etc.
        if (
            buffer[self.position : self.position + 4] == "JOSE"
            or buffer[start_index : start_index + 4] == "SAN "
        ):
            if (position == start_index and buffer[position + 4] == " ") or buffer[
                start_index : start_index + 4
            ] == "SAN ":
                self.next = ("H",)
            else:
                self.next = ("J", "H")

        # Yankelovich/Jankelowicz
        elif (
            position == start_index
            and buffer[self.position : self.position + 4] != "JOSE"
        ):
            self.next = ("J", "A")

        else:
            # Spanish pronunciation of e.g. 'Bajador'
            if (
                buffer[position - 1] in VOWELS
                and not self.word.is_slavo_germanic
                and buffer[position + 1] in ["A", "O"]
            ):
                self.next = ("J", "H")
            else:
                if position == self.word.end_index:
                    self.next = ("J", " ")
                else:
                    if buffer[position + 1] not in [
                        "L",
                        "T",
                        "K",
                        "S",
                        "N",
                        "M",
                        "B",
                        "Z",
                    ] and buffer[position - 1] not in ["S", "K", "L"]:
                        self.next = ("J",)
                    else:
                        self.next = (None,)

        if buffer[position + 1] == "J":
            self.next = self.next + (2,)
        else:
            self.next = self.next + (1,)

    def process_k(self):
        if self.word.buffer[self.position + 1] == "K":
            self.next = ("K", 2)
        else:
            self.next = ("K", 1)

    def process_l(self):
        buffer = self.word.buffer
        position = self.position
        end_index = self.word.end_index

        if buffer[position + 1] == "L":
            # Spanish e.g. 'cabrillo', 'gallegos'
            if (
                position == (end_index - 2)
                and buffer[position - 1 : position + 3] in ["ILLO", "ILLA", "ALLE"]
            ) or (
                (
                    buffer[end_index - 1 : end_index + 1] in ["AS", "OS"]
                    or buffer[end_index] in ["A", "O"]
                )
                and buffer[position - 1 : position + 3] == "ALLE"
            ):
                self.next = ("L", "", 2)
            else:
                self.next = ("L", 2)
        else:
            self.next = ("L", 1)

    def process_m(self):
        buffer = self.word.buffer
        position = self.position
        if (
            buffer[position + 1 : position + 4] == "UMB"
            and (
                position + 1 == self.word.end_index
                or buffer[position + 2 : position + 4] == "ER"
            )
        ) or buffer[position + 1] == "M":
            self.next = ("M", 2)
        else:
            self.next = ("M", 1)

    def process_n(self):
        if self.word.buffer[self.position + 1] == "N":
            self.next = ("N", 2)
        else:
            self.next = ("N", 1)

    def process_p(self):
        if self.word.buffer[self.position + 1] == "H":
            self.next = ("F", 2)

        # Account for "Campbell", "raspberry"
        elif self.word.buffer[self.position + 1] in ["P", "B"]:
            self.next = ("P", 2)
        else:
            self.next = ("P", 1)

    def process_q(self):
        if self.word.buffer[self.position + 1] == "Q":
            self.next = ("K", 2)
        else:
            self.next = ("K", 1)

    def process_r(self):
        buffer = self.word.buffer
        position = self.position
        end_index = self.word.end_index

        # French e.g. 'Rogier', but exclude e.g. 'Hochmeier'
        if (
            position == end_index
            and not self.word.is_slavo_germanic
            and buffer[position - 2 : position] == "IE"
            and buffer[position - 4 : position - 2] not in ["ME", "MA"]
        ):
            self.next = ("", "R")
        else:
            self.next = ("R",)
        if buffer[position + 1] == "R":
            self.next = self.next + (2,)
        else:
            self.next = self.next + (1,)

    def process_s(self):
        buffer = self.word.buffer
        position = self.position
        start_index = self.word.start_index
        end_index = self.word.end_index

        # Special cases like 'Carlisle', 'Carlysle'
        if buffer[position - 1 : position + 2] in ["ISL", "YSL"]:
            self.next = (None, 1)

        # special case 'sugar-'
        elif (
            position == start_index and buffer[start_index : start_index + 5] == "SUGAR"
        ):
            self.next = ("X", "S", 1)

        elif buffer[position : position + 2] == "SH":
            # Germanic
            if buffer[position + 1 : position + 5] in ["HEIM", "HOEK", "HOLM", "HOLZ"]:
                self.next = ("S", 2)
            else:
                self.next = ("X", 2)

        # Italian & Armenian
        elif (
            buffer[position : position + 3] in ["SIO", "SIA"]
            or buffer[position : position + 4] == "SIAN"
        ):
            if not self.word.is_slavo_germanic:
                self.next = ("S", "X", 3)
            else:
                self.next = ("S", 3)

        # Lots of anglicisations to match here
        # Germanic, e.g. 'Smith' == 'Schmidt', 'Snider' == 'Schneider'
        # Slavic languages, catch -sz- and the tricky Hungarian
        # pronunciation with an 's'
        elif (
            position == start_index and buffer[position + 1] in ["M", "N", "L", "W"]
        ) or buffer[position + 1] == "Z":
            self.next = ("S", "X")
            if buffer[position + 1] == "Z":
                self.next = self.next + (2,)
            else:
                self.next = self.next + (1,)

        elif buffer[position : position + 2] == "SC":
            # Schlesinger's rule
            if buffer[position + 2] == "H":
                # Dutch origin, e.g. 'school', 'schooner'
                if buffer[position + 3 : position + 5] in [
                    "OO",
                    "ER",
                    "EN",
                    "UY",
                    "ED",
                    "EM",
                ]:
                    # 'Schermerhorn', 'Schenker'
                    if buffer[position + 3 : position + 5] in ["ER", "EN"]:
                        self.next = ("X", "SK", 3)
                    else:
                        self.next = ("SK", 3)

                else:
                    if (
                        position == start_index
                        and buffer[start_index + 3] not in VOWELS
                        and buffer[start_index + 3] != "W"
                    ):
                        self.next = ("X", "S", 3)
                    else:
                        self.next = ("X", 3)

            elif buffer[position + 2] in ["I", "E", "Y"]:
                self.next = ("S", 3)
            else:
                self.next = ("SK", 3)

        # French e.g. 'Resnais', 'Artois'
        elif position == end_index and buffer[position - 2 : position] in ["AI", "OI"]:
            self.next = ("", "S", 1)
        else:
            self.next = ("S",)
            if buffer[position + 1] in ["S", "Z"]:
                self.next = self.next + (2,)
            else:
                self.next = self.next + (1,)

    def process_t(self):
        buffer = self.word.buffer
        position = self.position
        start_index = self.word.start_index

        if buffer[position : position + 4] == "TION":
            self.next = ("X", 3)
        elif buffer[position : position + 3] in ["TIA", "TCH"]:
            self.next = ("X", 3)
        elif (
            buffer[position : position + 2] == "TH"
            or buffer[position : position + 3] == "TTH"
        ):
            # 'Thomas', 'Thames' or hard-sound Germanic
            if (
                buffer[position + 2 : position + 4] in ["OM", "AM"]
                or buffer[start_index : start_index + 4] in ["VON ", "VAN "]
                or buffer[start_index : start_index + 3] == "SCH"
            ):
                self.next = ("T", 2)
            else:
                self.next = ("0", "T", 2)

        elif buffer[position + 1] in ["T", "D"]:
            self.next = ("T", 2)
        else:
            self.next = ("T", 1)

    def process_v(self):
        if self.word.buffer[self.position + 1] == "V":
            self.next = ("F", 2)
        else:
            self.next = ("F", 1)

    def process_w(self):
        buffer = self.word.buffer
        position = self.position
        start_index = self.word.start_index

        if buffer[position : position + 2] == "WR":
            self.next = ("R", 2)
        elif position == start_index and (
            buffer[position + 1] in VOWELS or buffer[position : position + 2] == "WH"
        ):
            # Wasserman should match Vasserman
            if buffer[position + 1] in VOWELS:
                self.next = ("A", "F", 1)
            else:
                self.next = ("A", 1)

        # Arnow should match Arnoff
        elif (
            (position == self.word.end_index and buffer[position - 1] in VOWELS)
            or buffer[position - 1 : position + 4]
            in ["EWSKI", "EWSKY", "OWSKI", "OWSKY"]
            or buffer[start_index : start_index + 3] == "SCH"
        ):
            self.next = ("", "F", 1)

        # Polish e.g. 'Filipowicz'
        elif buffer[position : position + 4] in ["WICZ", "WITZ"]:
            self.next = ("TS", "FX", 4)

        # By default, 'W' is skipped phonetically
        else:
            self.next = (None, 1)

    def process_x(self):
        buffer = self.word.buffer
        position = self.position

        # French e.g. 'Breaux'
        self.next = (None,)
        if not (
            position == self.word.end_index
            and (
                buffer[position - 3 : position] in ["IAU", "EAU"]
                or buffer[position - 2 : position] in ["AU", "OU"]
            )
        ):
            self.next = ("KS",)

        if buffer[position + 1] in ["C", "X"]:
            self.next = self.next + (2,)
        else:
            self.next = self.next + (1,)

    def process_z(self):
        # Chinese pinyin e.g. 'zhao'
        if self.word.buffer[self.position + 1] == "H":
            self.next = ("J",)
        elif self.word.buffer[self.position + 1 : self.position + 3] in [
            "ZO",
            "ZI",
            "ZA",
        ] or (
            self.word.is_slavo_germanic
            and self.position > self.word.start_index
            and self.word.buffer[self.position - 1] != "T"
        ):
            self.next = ("S", "TS")
        else:
            self.next = ("S",)
        if (
            self.word.buffer[self.position + 1] == "Z"
            or self.word.buffer[self.position + 1] == "H"
        ):
            self.next = self.next + (2,)
        else:
            self.next = self.next + (1,)

    def parse(self, input):
        self.word = Word(input)
        self.position = self.word.start_index
        self.primary_phone = ""
        self.secondary_phone = ""
        self.next = (None, 1)
        self.check_word_start()

        # Loop through chars in word.buffer
        while self.position <= self.word.end_index:
            character = self.word.buffer[self.position]

            # Vowels and spaces get special handling
            if character in VOWELS:
                self.process_vowel()
            elif character == " ":
                self.position += 1
                continue

            # Other letters each have their own function
            elif character == "B":
                self.process_b()
            elif character == "C":
                self.process_c()
            elif character == "D":
                self.process_d()
            elif character == "F":
                self.process_f()
            elif character == "G":
                self.process_g()
            elif character == "H":
                self.process_h()
            elif character == "J":
                self.process_j()
            elif character == "K":
                self.process_k()
            elif character == "L":
                self.process_l()
            elif character == "M":
                self.process_m()
            elif character == "N":
                self.process_n()
            elif character == "P":
                self.process_p()
            elif character == "Q":
                self.process_q()
            elif character == "R":
                self.process_r()
            elif character == "S":
                self.process_s()
            elif character == "T":
                self.process_t()
            elif character == "V":
                self.process_v()
            elif character == "W":
                self.process_w()
            elif character == "X":
                self.process_x()
            elif character == "Z":
                self.process_z()

            # Handle any residual unprocessed sound clusters
            if len(self.next) == 2:
                if self.next[0]:
                    self.primary_phone += self.next[0]
                    self.secondary_phone += self.next[0]
                self.position += self.next[1]
            elif len(self.next) == 3:
                if self.next[0]:
                    self.primary_phone += self.next[0]
                if self.next[1]:
                    self.secondary_phone += self.next[1]
                self.position += self.next[2]

        # Standardize all representations to the dominant
        # first sound clusters
        if len(self.primary_phone) > 4:
            self.primary_phone = self.primary_phone[:4]
        if len(self.secondary_phone) > 4:
            self.secondary_phone = self.secondary_phone[:4]

        if self.primary_phone == self.secondary_phone:
            self.secondary_phone = ""
        return [self.primary_phone, self.secondary_phone]


class Word(object):
    """
    Helper class used for representing a single word for token
    parsing.
    """

    def __init__(self, input):
        self.original = input
        if isinstance(input, bytes):
            self.decoded = input.decode("utf-8", "ignore")
        else:
            self.decoded = input

        # Handle accented characters
        self.decoded = self.decoded.replace("\xc7", "s")
        self.decoded = self.decoded.replace("\xe7", "s")
        self.normalized = "".join(
            (
                c
                for c in unicodedata.normalize("NFD", self.decoded)
                if unicodedata.category(c) != "Mn"
            )
        )
        self.upper = self.normalized.upper()
        self.length = len(self.upper)
        self.prepad = "  "
        self.start_index = len(self.prepad)
        self.end_index = self.start_index + self.length - 1
        self.postpad = "      "

        # Buffer used in algorithm to index outside bounds of original string
        self.buffer = self.prepad + self.upper + self.postpad

    @property
    def is_slavo_germanic(self):
        """
        Use letter clusterings to identify likelihood of language origin.
        """
        return (
            self.upper.find("W") > -1
            or self.upper.find("K") > -1
            or self.upper.find("CZ") > -1
            or self.upper.find("WITZ") > -1
        )

    def get_letters(self, start=0, end=None):
        """
        Return all characters in the requested buffer range.
        """
        if not end:
            end = start + 1
        start = self.start_index + start
        end = self.start_index + end
        return self.buffer[start:end]
