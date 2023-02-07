import hashlib
import pandas as pd
from phdi.harmonization.utils import compare_strings
from typing import List, Callable, Dict


def generate_hash_str(linking_identifier: str, salt_str: str) -> str:
    """
    Generates a hash for a given string of concatenated patient information. The hash
    serves as a "unique" identifier for the patient.

    :param linking_identifier: The value to be hashed.  For example, the concatenation
      of a patient's name, address, and date of birth, delimited by dashes.
    :param salt_str: The salt to use with the hash. This is intended to prevent
      reverse engineering of the PII used to create the hash.
    :return: The hash of the linking_identifier string.
    """
    hash_obj = hashlib.sha256()
    to_encode = (linking_identifier + salt_str).encode("utf-8")
    hash_obj.update(to_encode)
    return hash_obj.hexdigest()


def match_within_block(
    block: List[List],
    feature_funcs: dict[int, Callable],
    match_eval: Callable,
    **kwargs
) -> List[tuple]:
    """
    Performs matching on all candidate pairs of records within a given block
    of data. Actual partitioning of the data should be done outside this
    function, as it compares all possible pairs within the provided partition.
    Uses a given construction of feature comparison rules as well as a
    match evaluation rule to determine the final verdict on whether two
    records are indeed a match.

    A feature function is of the form "feature_match_X" for some condition
    X; it must accept two records (lists of data), an index i in which the
    feature to compare is stored, and the parameter **kwargs. It must return
    a boolean indicating whether the features "match" for whatever definition
    of match the function uses (i.e. this allows modular logic to apply to
    different features in the compared records). Note that not all features
    in a record need a comparison function defined.

    A match evaluation rule is a function of the form "eval_X" for some
    condition X. It accepts as input a list of booleans, one for each feature
    that was compared with feature funcs, and determines whether the
    comparisons constitute a match according to X.

    :param block: A list of records to check for matches. Each record in
      the list is itself a list of features. The first feature of the
      record must be an "id" for the record.
    :param feature_funcs: A dictionary mapping feature indices to functions
      used to evaluate those features for a match.
    :param match_eval: A function for determining whether a given set of
      feature comparisons constitutes a match for linkage.
    :return: A list of 2-tuples of the form (i,j), where i,j give the indices
      in the block of data of records deemed to match.
    """
    match_pairs = []

    # Dynamic programming table: order doesn't matter, so only need to
    # check each combo of i,j once
    for i, record_i in enumerate(block):
        for j in range(i + 1, len(block)):
            record_j = block[j]
            feature_comps = [
                feature_funcs[x](record_i, record_j, x, **kwargs)
                for x in range(len(record_i))
                if x in feature_funcs
            ]

            # If it's a match, store the result
            is_match = match_eval(feature_comps)
            if is_match:
                match_pairs.append((i, j))

    return match_pairs


def _match_within_block_cluster_ratio(
    block: List[List],
    cluster_ratio: float,
    feature_funcs: dict[int, Callable],
    match_eval: Callable,
    **kwargs
) -> List[set]:
    """
    A matching function for statistically testing the impact of membership
    ratio to the quality of clusters formed. This function behaves similarly
    to `match_within_block`, except that rather than identifying all pairwise
    candidates which are deemed matches, the function creates a list of
    clusters of patients, where each cluster constitutes what would be a
    single "representative" patient in the database. The formation of
    clusters is determined by the parameter `cluster_ratio`, which defines
    the proportion of other records in an existing cluster that a new
    incoming record must match in order to join the cluster.

    :param block: A list of records to check for matches. Each record in
      the list is itself a list of features. The first feature of the
      record must be an "id" for the record.
    :param cluster_ratio: A float giving the proportion of records in an
      existing cluster that a new incoming record must match in order
      to qualify for membership in the cluster.
    :param feature_funcs: A dictionary mapping feature indices to functions
      used to evaluate those features for a match.
    :param match_eval: A function for determining whether a given set of
      feature comparisons constitutes a match for linkage.
    :return: A list of 2-tuples of the form (i,j), where i,j give the indices
      in the block of data of records deemed to match.
    """
    clusters = []
    for i in range(len(block)):
        # Base case
        if len(clusters) == 0:
            clusters.append({i})
            continue
        found_master_cluster = False

        # Iterate through clusters to find one that we match with
        for cluster in clusters:
            belongs = _eval_record_in_cluster(
                block, i, cluster, cluster_ratio, feature_funcs, match_eval, **kwargs
            )
            if belongs:
                found_master_cluster = True
                cluster.add(i)
                break

        # Create a new singleton if no other cluster qualified
        if not found_master_cluster:
            clusters.append({i})
    return clusters


def _eval_record_in_cluster(
    block: List[List],
    i: int,
    cluster: set,
    cluster_ratio: float,
    feature_funcs: dict[int, Callable],
    match_eval: Callable,
    **kwargs
):
    """
    A helper function used to evaluate whether a given incoming record
    satisfies the matching proportion threshold of an existing cluster,
    and therefore would belong to the cluster.
    """
    record_i = block[i]
    num_matched = 0.0
    for j in cluster:
        record_j = block[j]
        feature_comps = [
            feature_funcs[x](record_i, record_j, x, **kwargs)
            for x in range(len(record_i))
            if x in feature_funcs
        ]

        is_match = match_eval(feature_comps)
        if is_match:
            num_matched += 1.0
    if (num_matched / len(cluster)) >= cluster_ratio:
        return True
    return False


def feature_match_exact(
    record_i: List, record_j: List, feature_x: int, **kwargs: dict
) -> bool:
    """
    Determines whether a single feature in a given pair of records
    constitutes an exact match (perfect equality).

    :param record_i: One of the records in the candidate pair to evaluate.
    :param record_j: The second record in the candidate pair.
    :param feature_x: A number representing the index of the feature to
      compare for equality.
    :return: A boolean indicating whether the features are an exact match.
    """
    return record_i[feature_x] == record_j[feature_x]


def feature_match_fuzzy_string(
    record_i: List, record_j: List, feature_x: int, **kwargs: dict
) -> bool:
    """
    Determines whether two strings in a given pair of records are close
    enough to constitute a partial match. The exact nature of the match
    is determined by the specified string comparison function (see
    harmonization/utils/compare_strings for more details) as well as a
    scoring threshold the comparison must meet or exceed.

    :param record_i: One of the records in the candidate pair to evaluate.
    :param record_j: The second record in the candidate pair.
    :param feature_x: A number representing the index of the feature to
      compare for a partial match.
    :param **kwargs: Optionally, a dictionary including specifications for
      the string comparison metric to use, as well as the cutoff score
      beyond which to classify the strings as a partial match.
    :return: A boolean indicating whether the features are a fuzzy match.
    """
    # Special case for two empty strings, since we don't want vacuous
    # equality (or in-) to penalize the score
    if record_i[feature_x] == "" and record_j[feature_x] == "":
        return True
    if record_i[feature_x] is None and record_j[feature_x] is None:
        return True

    similarity_measure = "JaroWinkler"
    if "similarity_measure" in kwargs:
        similarity_measure = kwargs["similarity_measure"]
    threshold = 0.7
    if "threshold" in kwargs:
        threshold = kwargs["threshold"]
    score = compare_strings(
        record_i[feature_x], record_j[feature_x], similarity_measure
    )
    return score >= threshold


def eval_perfect_match(feature_comparisons: List) -> bool:
    """
    Determines whether a given set of feature comparisons represent a
    'perfect' match (i.e. whether all features that were compared match
    in whatever criteria was specified for them).

    :param feature_comparisons: A list of 1s and 0s, one for each feature
      that was compared during the match algorithm.
    :return: The evaluation of whether the given features all match.
    """
    return sum(feature_comparisons) == len(feature_comparisons)


def block_parquet_data(path: str, blocks: List) -> Dict:
    """
    Generates dictionary of blocked data where each key is a block and each value is a
    distinct list of lists containing the data for a given block.

    :param path: Path to parquet file containing data that needs to be linked.
    :param blocks: List of columns to be used in blocks.
    :return: A dictionary of with the keys as the blocks and the values as the data
    within each block, stored as a list of lists.
    """
    data = pd.read_parquet(path, engine="pyarrow")
    blocked_data_tuples = tuple(data.groupby(blocks))

    # Convert data to list of lists within dict
    blocked_data = dict()
    for block, df in blocked_data_tuples:
        blocked_data[block] = df.values.tolist()

    return blocked_data
