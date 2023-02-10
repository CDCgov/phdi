import hashlib
import pandas as pd
from phdi.harmonization.utils import compare_strings
from phdi.harmonization import double_metaphone_string
from typing import List, Callable, Union


def block_data(data: pd.DataFrame, blocks: List) -> dict:
    """
    Generates dictionary of blocked data where each key is a block
    and each value is a distinct list of lists containing the data
    for a given block.

    :param path: Path to parquet file containing data that needs to
      be linked.
    :param blocks: List of columns to be used in blocks.
    :return: A dictionary of with the keys as the blocks and the
      values as the data within each block, stored as a list of
      lists.
    """
    blocked_data_tuples = tuple(data.groupby(blocks))

    # Convert data to list of lists within dict
    blocked_data = dict()
    for block, df in blocked_data_tuples:
        blocked_data[block] = df.values.tolist()

    return blocked_data


def compile_match_lists(match_lists: List[dict], cluster_mode: bool = False):
    """
    Turns a list of matches of either clusters or candidate pairs found
    during linkage into a single unified structure holding all found matches
    across all rules passes. E.g. if a single pass of a linkage algorithm
    uses three rules, hence generates three dictionaries of matches, this
    function will aggregate the results of those three separate dicts into
    a single unified and deduplicated dictionary. For consistency during
    statistical evaluation, the returned dictionary is always indexed by
    the lower ID of the records in a given pair.

    :param match_lists: A list of the dictionaries obtained during a run
      of the linkage algorithm, one dictionary per rule used in the run.
    :param cluster_mode: An optional boolean indicating whether the linkage
      algorithm was run in cluster mode. Default is False.
    :return: The aggregated dictionary of unified matches.
    """
    matches = {}
    for matches_from_rule in match_lists:
        for matches_within_blocks in matches_from_rule.values():
            for candidate_set in matches_within_blocks:
                # Always index the aggregate by the lowest valued ID
                # for statistical consistency and deduplication
                root_record = min(candidate_set)
                if root_record not in matches:
                    matches[root_record] = set()

                # For clustering, need to add all other records in the cluster
                if cluster_mode:
                    for clustered_record in candidate_set:
                        if clustered_record != root_record:
                            matches[root_record].add(clustered_record)
                else:
                    matched_record = max(candidate_set)
                    matches[root_record].add(matched_record)
    return matches


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


def feature_match_four_char(
    record_i: List, record_j: List, feature_x: int, **kwargs: dict
) -> bool:
    """
    Determines whether a string feature in a pair of records exactly matches
    on the first four characters.

    :param record_i: One of the records in the candidate pair to evaluate.
    :param record_j: The second record in the candidate pair.
    :param feature_x: A number representing the index of the feature to
      compare.
    :return: A boolean indicating whether the features are a match.
    """
    first_four_i = record_i[feature_x][: min(4, len(record_i[feature_x]))]
    first_four_j = record_j[feature_x][: min(4, len(record_j[feature_x]))]
    return first_four_i == first_four_j


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
    **kwargs,
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


def perform_linkage_pass(
    data: pd.DataFrame,
    blocks: List,
    feature_funcs: dict[int, Callable],
    matching_rule: Callable,
    cluster_ratio: Union[float, None] = None,
    **kwargs,
) -> dict:
    """
    Performs a partial run of a linkage algorithm using a single rule.
    Each rule in an algorithm is associated with its own pass through the
    data.

    :param data: A pandas dataframe of records to link.
    :param blocks: A list of column headers to use as blocking assignments
      by which to partition the data.
    :param feature_funcs: A dictionary mapping feature indices to functions
      used to evaluate those features for a match.
    :param matching_rule: A function for determining whether a given set of
      feature comparisons constitutes a match for linkage.
    :param cluster_ratio: An optional parameter indicating, if using the
      algorithm in cluster mode, the required membership percentage a record
      must score with an existing cluster in order to join.
    :return: A dictionary mapping each block found in the pass to the matches
      discovered within that block.
    """
    blocked_data = block_data(data, blocks)
    matches = {}
    for block in blocked_data:
        if cluster_ratio:
            matches_in_block = _match_within_block_cluster_ratio(
                blocked_data[block],
                cluster_ratio,
                feature_funcs,
                matching_rule,
                **kwargs,
            )
        else:
            matches_in_block = match_within_block(
                blocked_data[block], feature_funcs, matching_rule, **kwargs
            )
        matches_in_block = _map_matches_to_record_ids(
            matches_in_block, blocked_data[block], cluster_ratio is not None
        )
        matches[block] = matches_in_block
    return matches


def _eval_record_in_cluster(
    block: List[List],
    i: int,
    cluster: set,
    cluster_ratio: float,
    feature_funcs: dict[int, Callable],
    match_eval: Callable,
    **kwargs,
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


def _map_matches_to_record_ids(
    match_list: List[tuple], data_block, cluster_mode: bool = False
) -> List[tuple]:
    """
    Helper function to turn a list of tuples of row indices in a block
    of data into a list of tuples of the IDs of the records within
    that block.
    """
    matched_records = []

    # Assumes ID is last column in data set
    if cluster_mode:
        for cluster in match_list:
            new_cluster = set()
            for record_idx in cluster:
                new_cluster.add(data_block[record_idx][-1])
            matched_records.append(new_cluster)
    else:
        for matching_pair in match_list:
            id_i = data_block[matching_pair[0]][-1]
            id_j = data_block[matching_pair[1]][-1]
            matched_records.append((id_i, id_j))
    return matched_records


def _match_within_block_cluster_ratio(
    block: List[List],
    cluster_ratio: float,
    feature_funcs: dict[int, Callable],
    match_eval: Callable,
    **kwargs,
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


def score_linkage_vs_truth(
    found_matches: dict[Union[int, str], set],
    true_matches: dict[Union[int, str], set],
    records_in_dataset: int,
) -> tuple:
    """
    Compute the statistical qualities of a run of record linkage against
    known true results. This function assumes that matches have already
    been determined by the algorithm, and further assumes that true
    matches have already been identified in the data.

    :param found_matches: A dictionary mapping IDs of records to sets of
      other records which were determined to be a match.
    :param true_matches: A dictionary mapping IDs of records to sets of
      other records which are _known_ to be a true match.
    :param records_in_dataset: The number of records in the original data
      set to-link.
    :return: A tuple reporting the sensitivity/precision, specificity/recall,
      positive prediction value, and F1 score of the linkage algorithm.
    """
    # Need division by 2 because ordering is irrelevant, matches are symmetric
    total_possible_matches = (records_in_dataset * (records_in_dataset - 1)) / 2.0
    true_positives = 0.0
    false_positives = 0.0
    false_negatives = 0.0

    for root_record in true_matches:
        if root_record in found_matches:
            true_positives += len(
                true_matches[root_record].intersection(found_matches[root_record])
            )
            false_positives += len(
                found_matches[root_record].difference(true_matches[root_record])
            )
            false_negatives += len(
                true_matches[root_record].difference(found_matches[root_record])
            )
        else:
            false_negatives += len(true_matches[root_record])
    for record in set(set(found_matches.keys()).difference(true_matches.keys())):
        false_positives += len(found_matches[record])

    true_negatives = (
        total_possible_matches - true_positives - false_positives - false_negatives
    )

    print("True Positives Found:", true_positives)
    print("False Positives Misidentified:", false_positives)
    print("False Negatives Missed:", false_negatives)

    sensitivity = round(true_positives / (true_positives + false_negatives), 3)
    specificity = round(true_negatives / (true_negatives + false_positives), 3)
    ppv = round(true_positives / (true_positives + false_positives), 3)
    f1 = round(
        (2 * true_positives) / (2 * true_positives + false_negatives + false_positives),
        3,
    )
    return (sensitivity, specificity, ppv, f1)
