from phdi.harmonization import DoubleMetaphone


def test_single_result():
    dmeta = DoubleMetaphone()
    result = dmeta("aubrey")
    assert result == ["APR", ""]


def test_double_result():
    dmeta = DoubleMetaphone()
    result = dmeta("richard")
    assert result == ["RXRT", "RKRT"]


def test_general_word_list():
    dmeta = DoubleMetaphone()
    result = dmeta("Jose")
    assert result == ["HS", ""]
    result = dmeta("cambrillo")
    assert result == ["KMPR", ""]
    result = dmeta("otto")
    assert result == ["AT", ""]
    result = dmeta("aubrey")
    assert result == ["APR", ""]
    result = dmeta("maurice")
    assert result == ["MRS", ""]
    result = dmeta("auto")
    assert result == ["AT", ""]
    result = dmeta("maisey")
    assert result == ["MS", ""]
    result = dmeta("catherine")
    assert result == ["K0RN", "KTRN"]
    result = dmeta("geoff")
    assert result == ["JF", "KF"]
    result = dmeta("Chile")
    assert result == ["XL", ""]
    result = dmeta("katherine")
    assert result == ["K0RN", "KTRN"]
    result = dmeta("steven")
    assert result == ["STFN", ""]
    result = dmeta("zhang")
    assert result == ["JNK", ""]
    result = dmeta("bob")
    assert result == ["PP", ""]
    result = dmeta("ray")
    assert result == ["R", ""]
    result = dmeta("Tux")
    assert result == ["TKS", ""]
    result = dmeta("bryan")
    assert result == ["PRN", ""]
    result = dmeta("bryce")
    assert result == ["PRS", ""]
    result = dmeta("Rapelje")
    assert result == ["RPL", ""]
    result = dmeta("richard")
    assert result == ["RXRT", "RKRT"]
    result = dmeta("solilijs")
    assert result == ["SLLS", ""]
    result = dmeta("Dallas")
    assert result == ["TLS", ""]
    result = dmeta("Schwein")
    assert result == ["XN", "XFN"]
    result = dmeta("dave")
    assert result == ["TF", ""]
    result = dmeta("eric")
    assert result == ["ARK", ""]
    result = dmeta("Parachute")
    assert result == ["PRKT", ""]
    result = dmeta("brian")
    assert result == ["PRN", ""]
    result = dmeta("randy")
    assert result == ["RNT", ""]
    result = dmeta("Through")
    assert result == ["0R", "TR"]
    result = dmeta("Nowhere")
    assert result == ["NR", ""]
    result = dmeta("heidi")
    assert result == ["HT", ""]
    result = dmeta("Arnow")
    assert result == ["ARN", "ARNF"]
    result = dmeta("Thumbail")
    assert result == ["0MPL", "TMPL"]


def test_homophones():
    dmeta = DoubleMetaphone()
    assert dmeta("tolled") == dmeta("told")
    assert dmeta("katherine") == dmeta("catherine")
    assert dmeta("brian"), dmeta("bryan")


def test_similar_names():
    dmeta = DoubleMetaphone()
    result = dmeta("Bartoš")
    assert result == ["PRTS", ""]
    result = dmeta("Bartosz")
    assert result == ["PRTS", "PRTX"]
    result = dmeta("Bartosch")
    assert result == ["PRTX", ""]
    result = dmeta("Bartos")
    assert result == ["PRTS", ""]


def test_non_english_unicode():
    dmeta = DoubleMetaphone()
    result = dmeta("andestādītu")
    assert result == ["ANTS", ""]


def test_c_cedilla():
    dmeta = DoubleMetaphone()
    result = dmeta("français")
    assert result == ["FRNS", ""]
    result = dmeta("garçon")
    assert result == ["KRSN", ""]
    result = dmeta("leçon")
    assert result == ["LSN", ""]


def test_various_german():
    dmeta = DoubleMetaphone()
    result = dmeta("ach")
    assert result == ["AK", ""]
    result = dmeta("bacher")
    assert result == ["PKR", ""]
    result = dmeta("macher")
    assert result == ["MKR", ""]


def test_various_italian():
    dmeta = DoubleMetaphone()
    result = dmeta("bacci")
    assert result == ["PX", ""]
    result = dmeta("bertucci")
    assert result == ["PRTX", ""]
    result = dmeta("bellocchio")
    assert result == ["PLX", ""]
    result = dmeta("bacchus")
    assert result == ["PKS", ""]
    result = dmeta("focaccia")
    assert result == ["FKX", ""]
    result = dmeta("chianti")
    assert result == ["KNT", ""]
    result = dmeta("tagliaro")
    assert result == ["TKLR", "TLR"]
    result = dmeta("biaggi")
    assert result == ["PJ", "PK"]


def test_various_spanish():
    dmeta = DoubleMetaphone()
    result = dmeta("bajador")
    assert result == ["PJTR", "PHTR"]
    result = dmeta("cabrillo")
    assert result == ["KPRL", "KPR"]
    result = dmeta("gallegos")
    assert result == ["KLKS", "KKS"]
    result = dmeta("San Jacinto")
    assert result == ["SNHS", ""]


def test_various_french():
    dmeta = DoubleMetaphone()
    result = dmeta("rogier")
    assert result == ["RJ", "RJR"]
    result = dmeta("breaux")
    assert result == ["PR", ""]


def test_various_slavic():
    dmeta = DoubleMetaphone()
    result = dmeta("Wewski")
    assert result == ["ASK", "FFSK"]


def test_various_chinese():
    dmeta = DoubleMetaphone()
    result = dmeta("zhao")
    assert result == ["J", ""]


def test_dutch_origin():
    dmeta = DoubleMetaphone()
    result = dmeta("school")
    assert result == ["SKL", ""]
    result = dmeta("schooner")
    assert result == ["SKNR", ""]
    result = dmeta("schermerhorn")
    assert result == ["XRMR", "SKRM"]
    result = dmeta("schenker")
    assert result == ["XNKR", "SKNK"]


def test_ch_words():
    dmeta = DoubleMetaphone()
    result = dmeta("Charac")
    assert result == ["KRK", ""]
    result = dmeta("Charis")
    assert result == ["KRS", ""]
    result = dmeta("chord")
    assert result == ["KRT", ""]
    result = dmeta("Chym")
    assert result == ["KM", ""]
    result = dmeta("Chia")
    assert result == ["K", ""]
    result = dmeta("chem")
    assert result == ["KM", ""]
    result = dmeta("chore")
    assert result == ["XR", ""]
    result = dmeta("orchestra")
    assert result == ["ARKS", ""]
    result = dmeta("architect")
    assert result == ["ARKT", ""]
    result = dmeta("orchid")
    assert result == ["ARKT", ""]


def test_cc_words():
    dmeta = DoubleMetaphone()
    result = dmeta("accident")
    assert result == ["AKST", ""]
    result = dmeta("accede")
    assert result == ["AKST", ""]
    result = dmeta("succeed")
    assert result == ["SKST", ""]


def test_mc_words():
    dmeta = DoubleMetaphone()
    result = dmeta("mac caffrey")
    assert result == ["MKFR", ""]
    result = dmeta("mac gregor")
    assert result == ["MKRK", ""]
    result = dmeta("mc crae")
    assert result == ["MKR", ""]
    result = dmeta("mcclain")
    assert result == ["MKLN", ""]


def test_gh_words():
    dmeta = DoubleMetaphone()
    result = dmeta("laugh")
    assert result == ["LF", ""]
    result = dmeta("cough")
    assert result == ["KF", ""]
    result = dmeta("rough")
    assert result == ["RF", ""]


def test_g3_words():
    dmeta = DoubleMetaphone()
    result = dmeta("gya")
    assert result == ["K", "J"]
    result = dmeta("ges")
    assert result == ["KS", "JS"]
    result = dmeta("gep")
    assert result == ["KP", "JP"]
    result = dmeta("geb")
    assert result == ["KP", "JP"]
    result = dmeta("gel")
    assert result == ["KL", "JL"]
    result = dmeta("gey")
    assert result == ["K", "J"]
    result = dmeta("gib")
    assert result == ["KP", "JP"]
    result = dmeta("gil")
    assert result == ["KL", "JL"]
    result = dmeta("gin")
    assert result == ["KN", "JN"]
    result = dmeta("gie")
    assert result == ["K", "J"]
    result = dmeta("gei")
    assert result == ["K", "J"]
    result = dmeta("ger")
    assert result == ["KR", "JR"]
    result = dmeta("danger")
    assert result == ["TNJR", "TNKR"]
    result = dmeta("manager")
    assert result == ["MNKR", "MNJR"]
    result = dmeta("dowager")
    assert result == ["TKR", "TJR"]


def test_pb_words():
    dmeta = DoubleMetaphone()
    result = dmeta("Campbell")
    assert result == ["KMPL", ""]
    result = dmeta("raspberry")
    assert result == ["RSPR", ""]


def test_th_words():
    dmeta = DoubleMetaphone()
    result = dmeta("Thomas")
    assert result == ["TMS", ""]
    result = dmeta("Thames")
    assert result == ["TMS", ""]
