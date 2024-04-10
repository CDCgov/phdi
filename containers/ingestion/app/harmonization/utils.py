from typing import Literal

import rapidfuzz


def compare_strings(
    string1: str,
    string2: str,
    similarity_measure: Literal[
        "JaroWinkler", "Levenshtein", "DamerauLevenshtein"
    ] = "JaroWinkler",
) -> float:
    """
    Returns the normalized similarity measure between string1 and string2, as
    determined by the similarlity measure. The higher the normalized similarity measure
    (up to 1.0), the more similar string1 and string2 are. A normalized similarity
    measure of 0.0 means string1 and string 2 are not at all similar. This function
    expects basic text cleaning (e.g. removal of numeric characters, trimming of spaces,
    etc.) to already have been performed on the input strings.

    :param string1: First string for comparison.
    :param string2: Second string for comparison.
    :param similarity_measure: The method used to measure the similarity between two
        strings, defaults to "JaroWinkler".
     - JaroWinkler: a ratio of matching characters and transpositions needed to
        transform string1 into string2.
     - Levenshtein: the number of edits (excluding transpositions) needed to transform
        string1 into string2.
     - DamerauLevenshtein: the number of edits (including transpositions) needed to
        transform string1 into string2.
    :return: The normalized similarity between string1 and string2, with 0 representing
        no similarity between string1 and string2, and 1 meaning string1 and string2 are
        dentical words.
    """
    if similarity_measure == "JaroWinkler":
        return rapidfuzz.distance.JaroWinkler.normalized_similarity(string1, string2)
    elif similarity_measure == "Levenshtein":
        return rapidfuzz.distance.Levenshtein.normalized_similarity(string1, string2)
    elif similarity_measure == "DamerauLevenshtein":
        return rapidfuzz.distance.DamerauLevenshtein.normalized_similarity(
            string1, string2
        )
