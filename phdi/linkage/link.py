import copy
import datetime
import hashlib
import json
import logging
import pathlib
from itertools import combinations
from math import log
from random import sample
from typing import Callable
from typing import List
from typing import Union

import matplotlib.pyplot as plt
import pandas as pd
from pydantic import Field

from phdi.fhir.utils import extract_value_with_resource_path
from phdi.harmonization.utils import compare_strings
from phdi.linkage.mpi import BaseMPIConnectorClient
from phdi.linkage.mpi import DIBBsMPIConnectorClient
from phdi.linkage.utils import datetime_to_str

LINKING_FIELDS_TO_FHIRPATHS = {
    "first_name": "Patient.name.given",
    "last_name": "Patient.name.family",
    "birthdate": "Patient.birthDate",
    "address": "Patient.address.line",
    "zip": "Patient.address.postalCode",
    "city": "Patient.address.city",
    "state": "Patient.address.state",
    "sex": "Patient.gender",
    "mrn": "Patient.identifier.where(type.coding.code='MR').value",
}


def block_data(data: pd.DataFrame, blocks: List) -> dict:
    """
    Generates dictionary of blocked data where each key is a block
    and each value is a distinct list of lists containing the data
    for a given block.

    :param data: A pandas dataframe of records to be linked.
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


def calculate_log_odds(
    m_probs: dict,
    u_probs: dict,
    file_to_write: Union[pathlib.Path, None] = None,
):
    """
    Calculate the per-field log odds ratio score that two records will
    match in a given field. Measures the likelihood that two records
    match on a column due to being a true match as opposed to random
    chance.

    :param m_probs: A dictionary of m-probabilities computed per field.
    :param u_probs: A dictionary of u_probabilities computed per field.
    :param file_to_write: Optionally, a destination filepath at which
      to write the probabilities in JSON format. Default is None.
    :raises ValueError: If the supplied m- and u- probability dictionaries
      do not share an equal key set.
    """
    if m_probs.keys() != u_probs.keys():
        raise ValueError(
            "m- and u- probability dictionaries must contain the same set of keys"
        )
    log_odds = {}
    for k in m_probs:
        log_odds[k] = log(m_probs[k]) - log(u_probs[k])
    _write_prob_file(log_odds, file_to_write)
    return log_odds


# TODO: We will eventually want to move away from pandas in favor of something
# more light-weight. While pandas is good for pre-computing and model
# examination, it does come with substantial overhead. Maybe make this work
# on a list of lists at some point.
def calculate_m_probs(
    data: pd.DataFrame,
    true_matches: dict,
    cols: Union[List[str], None] = None,
    file_to_write: Union[pathlib.Path, None] = None,
):
    """
    For a given set of patient records, calculate the per-field
    m-probability. The m-probability for field X is defined as the
    probability that a pair of records A and B have the same value in
    X, given that A and B are a true matching pair. This function
    incorporates LaPlacian Smoothing to account for unseen data and
    to resolve future logarithms against 0.

    :param data: A pandas dataframe of patient records to compute
      probabilities for.
    :param true_matches: A dictionary holding the IDs of record pairs
      that are true matches in the data set. The format of the dictionary
      should be such that the IDs of the "lower numbered" records in each
      match pair are the keys, and the values are sets of the "higher
      numbered" records in each pair.
    :param cols: Optionally, a list of columns to compute probabilities
      for. If not supplied, computes probabilities across all fields.
      Default is None.
    :param file_to_write: Optionally, a destination filepath at which to
      write the probabilities in JSON format. Default is None.
    """
    if cols is None:
        cols = data.columns
    m_probs = {c: 1.0 for c in cols}
    total_pairs = 1.0
    for root_record, paired_records in true_matches.items():
        total_pairs += len(paired_records)
        for pr in paired_records:
            for c in cols:
                if data[c].iloc[root_record] == data[c].iloc[pr]:
                    m_probs[c] += 1
    for c in cols:
        m_probs[c] /= total_pairs

    _write_prob_file(m_probs, file_to_write)
    return m_probs


# TODO: We will eventually want to move away from pandas in favor of something
# more light-weight. While pandas is good for pre-computing and model
# examination, it does come with substantial overhead. Maybe make this work
# on a list of lists at some point.
def calculate_u_probs(
    data: pd.DataFrame,
    true_matches: dict,
    n_samples: Union[int, None] = None,
    cols: Union[List, None] = None,
    file_to_write: Union[pathlib.Path, None] = None,
):
    """
    For a given set of patient records, calculate the per-field
    u-probability. The u-probability for field X is defined as the
    probability that a pair of records A and B have the same value in
    X, given that A and B are not a true matching pair. This function
    incorporates LaPlacian Smoothing to account for unseen data and
    to handle future logarithms against 0.

    Note: This function can be slow to compute for large data sets.
    It is recommended to pass only a representative subsample of the
    data to the function (we recommend sampling ~25k candidate pairs
    from a sub-sample of ~25k records), even if the sample operation
    is used.

    :param data: A pandas dataframe of patient records to compute
      probabilities for.
    :param true_matches: A dictionary holding the IDs of record pairs
      that are true matches in the data set. The format of the dictionary
      should be such that the IDs of the "lower numbered" records in each
      match pair are the keys, and the values are sets of the "higher
      numbered" records in each pair.
    :param n_samples: Optionally, a number of samples to take from the
      list of possible pairs to compute probabilities over.
    :param cols: Optionally, a list of columns to compute probabilities
      for. If not supplied, computes probabilities across all fields.
      Default is None.
    :param file_to_write: Optionally, a destination filepath at which to
      write the probabilities in JSON format. Default is None.
    """
    if cols is None:
        cols = data.columns

    u_probs = {c: 1.0 for c in cols}

    # Want only the pairs of candidates that aren't true matches
    base_pairs = list(combinations(data.index, 2))
    neg_pairs = [
        x
        for x in base_pairs
        if x[0] not in true_matches or x[1] not in true_matches[x[0]]
    ]

    if n_samples is not None and n_samples < len(neg_pairs):
        neg_pairs = sample(neg_pairs, n_samples)
    for index in neg_pairs:
        for c in cols:
            if data[c].iloc[index[0]] == data[c].iloc[index[1]]:
                u_probs[c] += 1.0

    for c in cols:
        if n_samples is not None and n_samples < len(neg_pairs):
            u_probs[c] = u_probs[c] / (n_samples + 1.0)
        else:
            u_probs[c] = u_probs[c] / (len(neg_pairs) + 1.0)

    _write_prob_file(u_probs, file_to_write)
    return u_probs


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


def eval_perfect_match(feature_comparisons: List, **kwargs) -> bool:
    """
    Determines whether a given set of feature comparisons represent a
    'perfect' match (i.e. whether all features that were compared match
    in whatever criteria was specified for them).

    :param feature_comparisons: A list of 1s and 0s, one for each feature
      that was compared during the match algorithm.
    :return: The evaluation of whether the given features all match.
    """
    return sum(feature_comparisons) == len(feature_comparisons)


def eval_log_odds_cutoff(feature_comparisons: List, **kwargs) -> bool:
    """
    Determines whether a given set of feature comparisons matches enough
    to be the result of a true patient link instead of just random chance.
    This is represented using previously computed log-odds ratios.

    :param feature_comparisons: A list of floats representing the log-odds
      score of each field computed on.
    :return: Whether the feature comparisons score well enough to be
      considered a match.
    """
    if "true_match_threshold" not in kwargs:
        raise KeyError("Cutoff threshold for true matches must be passed.")
    return sum(feature_comparisons) >= kwargs["true_match_threshold"]


def extract_blocking_values_from_record(
    record: dict, blocking_fields: List[dict]
) -> dict:
    """
    Extracts values from a given patient record for eventual use in database
    record linkage blocking. A list of fields to block on, as well as a mapping
    of those fields to any desired transformations of their extracted values,
    is used to fhir-path parse the value out of the incoming patient record.

    Currently supported blocking fields:
    - first_name
    - last_name
    - birthdate
    - address
    - city
    - state
    - zip
    - sex
    - mrn

    Currently supported transformations on extracted fields:
    - first4: the first four characters of the value
    - last4: the last four characters of the value

    :param record: A FHIR-formatted Patient record.
    :param blocking_fields: A List of dictionaries giving the blocking
      fields and any transformations that should be applied to them. Each
      dictionary in the list should include a "value" key with one of the
      supported blocking fields above, and may also optionally contain a
      "transformation" key whose value is one of our supported transforms.
    """

    transform_funcs = {
        "first4": lambda x: x[:4] if len(x) >= 4 else x,
        "last4": lambda x: x[-4:] if len(x) >= 4 else x,
    }

    for block_dict in blocking_fields:
        if "value" not in block_dict:
            raise KeyError(
                f"Input dictionary for block {block_dict} must contain a 'value' key."
            )

    block_vals = dict.fromkeys([b.get("value") for b in blocking_fields], "")
    transform_blocks = [b for b in blocking_fields if "transformation" in b]
    transformations = dict(
        zip(
            [b.get("value") for b in transform_blocks],
            [b.get("transformation") for b in transform_blocks],
        )
    )
    for block_dict in blocking_fields:
        block = block_dict.get("value")
        try:
            # Apply utility extractor for safe parsing
            value = extract_value_with_resource_path(
                record,
                LINKING_FIELDS_TO_FHIRPATHS[block],
                selection_criteria="first",
            )
            if value:
                if block in transformations:
                    try:
                        value = transform_funcs[transformations[block]](value)
                    except KeyError:
                        raise ValueError(
                            f"Transformation {transformations[block]} is not valid."
                        )
                    block_vals[block] = {
                        "value": value,
                        "transformation": transformations[block],
                    }
                else:
                    block_vals[block] = {"value": value}

        except KeyError:
            raise ValueError(f"Field {block} is not a supported extraction field.")

    # Account for any incoming FHIR resources that return no data
    # for a field--don't count this against records to-block
    keys_to_pop = []
    for field in block_vals:
        if _is_empty_extraction_field(block_vals, field):
            keys_to_pop.append(field)
    for k in keys_to_pop:
        block_vals.pop(k)

    return block_vals


def feature_match_exact(
    record_i: List,
    record_j: List,
    feature_col: str,
    col_to_idx: dict[str, int],
    **kwargs: dict,
) -> bool:
    """
    Determines whether a single feature in a given pair of records
    constitutes an exact match (perfect equality).

    :param record_i: One of the records in the candidate pair to evaluate.
    :param record_j: The second record in the candidate pair.
    :param feature_col: The name of the column being evaluated (e.g. "city").
    :param col_to_idx: A dictionary mapping column names to the numeric index
      in which they occur in order in the data.
    :return: A boolean indicating whether the features are an exact match.
    """
    idx = col_to_idx[feature_col]
    return record_i[idx] == record_j[idx]


def feature_match_four_char(
    record_i: List,
    record_j: List,
    feature_col: str,
    col_to_idx: dict[str, int],
    **kwargs: dict,
) -> bool:
    """
    Determines whether a string feature in a pair of records exactly matches
    on the first four characters.

    :param record_i: One of the records in the candidate pair to evaluate.
    :param record_j: The second record in the candidate pair.
    :param feature_col: The name of the column being evaluated (e.g. "city").
    :param col_to_idx: A dictionary mapping column names to the numeric index
      in which they occur in order in the data.
    :return: A boolean indicating whether the features are a match.
    """
    idx = col_to_idx[feature_col]
    first_four_i = record_i[idx][: min(4, len(record_i[idx]))]
    first_four_j = record_j[idx][: min(4, len(record_j[idx]))]
    return first_four_i == first_four_j


def feature_match_fuzzy_string(
    record_i: List,
    record_j: List,
    feature_col: str,
    col_to_idx: dict[str, int],
    **kwargs: dict,
) -> bool:
    """
    Determines whether two strings in a given pair of records are close
    enough to constitute a partial match. The exact nature of the match
    is determined by the specified string comparison function (see
    harmonization/utils/compare_strings for more details) as well as a
    scoring threshold the comparison must meet or exceed.

    :param record_i: One of the records in the candidate pair to evaluate.
    :param record_j: The second record in the candidate pair.
    :param feature_col: The name of the column being evaluated (e.g. "city").
    :param col_to_idx: A dictionary mapping column names to the numeric index
      in which they occur in order in the data.
    :param **kwargs: Optionally, a dictionary including specifications for
      the string comparison metric to use, as well as the cutoff score
      beyond which to classify the strings as a partial match.
    :return: A boolean indicating whether the features are a fuzzy match.
    """
    idx = col_to_idx[feature_col]

    # Convert datetime obj to str using helper function
    if feature_col == "birthdate":
        record_i[idx] = datetime_to_str(record_i[idx])
        record_j[idx] = datetime_to_str(record_j[idx])

    # Special case for two empty strings, since we don't want vacuous
    # equality (or in-) to penalize the score
    if record_i[idx] == "" and record_j[idx] == "":
        return True
    if record_i[idx] is None and record_j[idx] is None:
        return True

    similarity_measure = "JaroWinkler"
    if "similarity_measure" in kwargs:
        similarity_measure = kwargs["similarity_measure"]
    threshold = 0.7
    if "threshold" in kwargs:
        threshold = kwargs["threshold"]
    score = compare_strings(record_i[idx], record_j[idx], similarity_measure)
    return score >= threshold


def feature_match_log_odds_exact(
    record_i: List,
    record_j: List,
    feature_col: str,
    col_to_idx: dict[str, int],
    **kwargs: dict,
) -> float:
    """
    Determines whether two feature values in two records should earn the full
    log-odds similarity score (i.e. they match exactly) or whether they
    should earn no weight (they differ). Used for fields for which fuzzy
    comparisons are inappropriate, such as sex.

    :param record_i: One of the records in the candidate pair to evaluate.
    :param record_j: The second record in the candidate pair.
    :param feature_col: The name of the column being evaluated (e.g. "city").
    :param col_to_idx: A dictionary mapping column names to the numeric index
      in which they occur in order in the data.
    :return: A float of the score the feature comparison earned.
    """
    if "log_odds" not in kwargs:
        raise KeyError("Mapping of columns to m/u log-odds must be provided.")
    col_odds = kwargs["log_odds"][feature_col]
    idx = col_to_idx[feature_col]
    if record_i[idx] == record_j[idx]:
        return col_odds
    else:
        return 0.0


def feature_match_log_odds_fuzzy_compare(
    record_i: List,
    record_j: List,
    feature_col: str,
    col_to_idx: dict[str, int],
    **kwargs: dict,
) -> float:
    """
    Determines the weighted string-odds similarly score earned by two
    feature values in two records, as a function of the pre-computed
    log-odds weights and the string similarity between the two features.
    This scales the full score that would be earned from a perfect
    match to a degree of partial weight appropriate to how similar the
    two strings are.

    :param record_i: One of the records in the candidate pair to evaluate.
    :param record_j: The second record in the candidate pair.
    :param feature_col: The name of the column being evaluated (e.g. "city").
    :param col_to_idx: A dictionary mapping column names to the numeric index
      in which they occur in order in the data.
    :return: A float of the score the feature comparison earned.
    """
    if "log_odds" not in kwargs:
        raise KeyError("Mapping of columns to m/u log-odds must be provided.")
    threshold = 0.7
    if "threshold" in kwargs:
        threshold = kwargs["threshold"]
    col_odds = kwargs["log_odds"][feature_col]
    idx = col_to_idx[feature_col]

    # Convert datetime obj to str using helper function
    if feature_col == "birthdate":
        record_i[idx] = datetime_to_str(record_i[idx])
        record_j[idx] = datetime_to_str(record_j[idx])

    score = compare_strings(record_i[idx], record_j[idx], "JaroWinkler")
    if score < threshold:
        score = 0.0
    return score * col_odds


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


def link_record_against_mpi(
    record: dict,
    algo_config: List[dict],
    external_person_id: str = None,
    mpi_client: BaseMPIConnectorClient = None,
) -> tuple[bool, str]:
    """
    Runs record linkage on a single incoming record (extracted from a FHIR
    bundle) using an existing database as an MPI. Uses a flexible algorithm
    configuration to allow customization of the exact kind of linkage to
    run. Linkage is assumed to run using cluster membership (i.e. the new
    record must match a certain proportion of existing records all assigned
    to a person in order to match), and if multiple persons are matched,
    the new record is linked to the person with the strongest membership
    percentage.

    :param record: The FHIR-formatted patient resource to try to match to
      other records in the MPI.
    :param algo_config: An algorithm configuration consisting of a list
      of dictionaries describing the algorithm to run. See
      `read_linkage_config` and `write_linkage_config` for more details.
    :returns: A tuple consisting of a boolean indicating whether a match
      was found for the new record in the MPI, followed by the ID of the
      Person entity now associated with the incoming patient (either a
      new Person ID or the ID of an existing matched Person).
    """
    # Initialize MPI client
    if mpi_client is None:
        logging.info("MPI client was None, instatiating new client.")
        mpi_client = DIBBsMPIConnectorClient()

    # Need to bind function names back to their symbolic invocations
    # in context of the module--i.e. turn the string of a function
    # name back into the callable defined in link.py

    algo_config = copy.deepcopy(algo_config)
    logging.info(
        f"Starting _bind_func_names_to_invocations at: {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
    )
    algo_config = _bind_func_names_to_invocations(algo_config)
    logging.info(
        f"Done with _bind_func_names_to_invocations at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
    )

    # Membership ratios need to persist across linkage passes so that we can
    # find the highest scoring match across all trials
    linkage_scores = {}
    for linkage_pass in algo_config:
        blocking_fields = linkage_pass["blocks"]

        # MPI will be able to find patients if *any* of their names or addresses
        # contains extracted values, so minimally block on the first line
        # if applicable
        logging.info(
            f"Starting extract_blocking_values_from_record at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
        )
        blocking_criteria = extract_blocking_values_from_record(record, blocking_fields)
        logging.info(
            f"Done with extract_blocking_values_from_record at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
        )

        # We don't enforce blocking if an extracted value is empty, so if all
        # values come back blank, skip the pass because the only alt is comparing
        # to all found records
        if len(blocking_criteria) == 0:
            logging.info("No blocking criteria extracted from incoming record.")
            continue
        logging.info(
            f"Starting get_block_data at: {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
        )
        raw_data_block = mpi_client.get_block_data(blocking_criteria)
        logging.info(
            f"Done with get_block_data at: {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
        )

        data_block = _convert_given_name_to_first_name(raw_data_block)

        # First row of returned block is column headers
        # Map column name to idx, not including patient/person IDs
        col_to_idx = {v: k for k, v in enumerate(data_block[0][2:])}
        if len(data_block[1:]) > 0:  # Check if data_block is empty
            data_block = data_block[1:]
            logging.info(
                f"Starting _flatten_patient_resource at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
            )
            flattened_record = _flatten_patient_resource(record, col_to_idx)
            logging.info(
                f"Done with _flatten_patient_resource at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
            )

            logging.info(
                f"Starting _group_patient_block_by_person at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
            )
            clusters = _group_patient_block_by_person(data_block)
            logging.info(
                f"Done with _group_patient_block_by_person at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
            )

            # Check if incoming record should belong to one of the person clusters
            kwargs = linkage_pass.get("kwargs", {})
            for person in clusters:
                num_matched_in_cluster = 0.0
                for linked_patient in clusters[person]:
                    logging.info(
                        f"Starting _compare_records at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
                    )
                    is_match = _compare_records(
                        flattened_record,
                        linked_patient,
                        linkage_pass["funcs"],
                        col_to_idx,
                        linkage_pass["matching_rule"],
                        **kwargs,
                    )
                    logging.info(
                        f"Done with _compare_records at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
                    )

                    if is_match:
                        num_matched_in_cluster += 1.0

                # Update membership score for this person cluster so that we can
                # track best possible link across multiple passes
                logging.info(
                    f"Starting to update membership score at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
                )
                belongingness_ratio = num_matched_in_cluster / len(clusters[person])
                if belongingness_ratio >= linkage_pass.get("cluster_ratio", 0):
                    logging.info(
                        f"belongingness_ratio >= linkage_pass.get('cluster_ratio', 0): {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
                    )
                    if person in linkage_scores:
                        linkage_scores[person] = max(
                            [linkage_scores[person], belongingness_ratio]
                        )
                    else:
                        linkage_scores[person] = belongingness_ratio
                logging.info(
                    f"Done with updating membership score at: {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
                )
    person_id = None
    matched = False

    # If we found any matches, find the strongest one
    if len(linkage_scores) != 0:
        logging.info(
            f"Starting _find_strongest_link at: {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
        )
        person_id = _find_strongest_link(linkage_scores)
        matched = True
        logging.info(
            f"Done with _find_strongest_link at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
        )
    logging.info(
        f"Starting mpi_client.insert_matched_patient at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
    )
    person_id = mpi_client.insert_matched_patient(
        record, person_id=person_id, external_person_id=external_person_id
    )
    logging.info(
        f"Done with mpi_client.insert_matched_patient at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
    )

    return (matched, person_id)


def load_json_probs(path: pathlib.Path):
    """
    Load a dictionary of probabilities from a JSON-formatted file.
    The probabilities correspond to previously computed m-, u-, or
    log-odds probabilities derived from patient records, with one
    score for each field (column) appearing in the data.

    :param path: The file path to load the data from.
    :return: A dictionary of probability scores, one for each field
      in the data set on which they were computed.
    :raises FileNotFoundError: If a file does not exist at the given
      path.
    :raises JSONDecodeError: If the file cannot be read as valid JSON.
    """
    try:
        with open(path, "r") as file:
            prob_dict = json.load(file)
        return prob_dict
    except FileNotFoundError:
        raise FileNotFoundError(f"The specified file does not exist at {path}.")
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError(
            "The specified file is not valid JSON.", e.doc, e.pos
        )


def match_within_block(
    block: List[List],
    feature_funcs: dict[str, Callable],
    col_to_idx: dict[str, int],
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
    :param col_to_idx: A dictionary mapping column names to the numeric index
      in which they occur in order in the data.
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
                feature_funcs[feature_col](
                    record_i, record_j, feature_col, col_to_idx, **kwargs
                )
                for feature_col in feature_funcs
            ]

            # If it's a match, store the result
            is_match = match_eval(feature_comps, **kwargs)
            if is_match:
                match_pairs.append((i, j))

    return match_pairs


# @TODO: Make the data parameter into a list of lists once we finish up
# statistical evaluation--alternatively, allow the function to accept both
# data types, but either way, LoL needs to be in there since that's our
# primary data type to use here.
def perform_linkage_pass(
    data: pd.DataFrame,
    blocks: List,
    feature_funcs: dict[str, Callable],
    matching_rule: Callable,
    cluster_ratio: Union[float, None] = None,
    **kwargs,
) -> dict:
    """
    Performs a partial run of a linkage algorithm using a single rule.
    Each rule in an algorithm is associated with its own pass through the
    data.

    :param data: Currently, a pandas dataframe of records to link. When we
      move out of testing, this should become a LoL.
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
    # Retrieve indices of columns
    cols = list(data.columns.values)
    col_to_idx = dict(zip(cols, range(len(cols))))

    blocked_data = block_data(data, blocks)
    matches = {}
    for block in blocked_data:
        if cluster_ratio:
            matches_in_block = _match_within_block_cluster_ratio(
                blocked_data[block],
                cluster_ratio,
                feature_funcs,
                col_to_idx,
                matching_rule,
                **kwargs,
            )
        else:
            matches_in_block = match_within_block(
                blocked_data[block], feature_funcs, col_to_idx, matching_rule, **kwargs
            )
        matches_in_block = _map_matches_to_record_ids(
            matches_in_block, blocked_data[block], cluster_ratio is not None
        )
        matches[block] = matches_in_block
    return matches


# TODO: Migrate away from pandas eventually
# TODO: If profiling ever gets rolled into the pipeline as a standard
# part of the process, we should revisit that this function is essentially
# "blocking"--the user can't do anything while the plot is shown.
def profile_log_odds(
    data: pd.DataFrame,
    true_matches: dict,
    log_odds: dict,
    exact_cols: List,
    fuzzy_cols: List,
    idx_to_col: dict,
    neg_samples: int = 50000,
) -> None:  # pragma: no cover
    """
    Basic graphical profiler for log-odds histogram analysis. Using the
    raw data and previously known true matches, the function computes one
    list of log-odds scores that that would be earned by true matches under
    a given linkage rule, and another list of scores that would be earned
    by a random sampling of non-matches under the same linkage rule. These
    lists are used to plot bimodal histograms so that the cutoff threshold
    between non-matchces and true matches can be visually determined.

    :param data: A pandas data frame holding the raw patient record data.
    :param true_matches: A dictionary of known true matches in the data.
    :param log_odds: A dictionary whose keys are the column fields of data
      and whose values are the log-odds scores that two values match relative
      to random chance.
    :param exact_cols: A list of columns to be evaluated using equality
      comparisons.
    :param fuzzy_cols: A list of columns to be evaluated using fuzzy weighted
      comparisons.
    :param idx_to_col: A dictionary mapping the number of a column in a list
      representation of the data, to the name of the column in a pandas
      representation.
    :param neg_samples: Optionally, how many non-match samples to compute a
      score for when generating the histogram.
    """
    base_pairs = list(combinations(data.index, 2))
    neg_pairs = [
        x
        for x in base_pairs
        if x[0] not in true_matches or x[1] not in true_matches[x[0]]
    ]
    if neg_samples < len(neg_pairs):
        neg_pairs = sample(neg_pairs, neg_samples)

    data = data.values.tolist()
    cols_to_idx = {}
    for idx in idx_to_col:
        cols_to_idx[idx_to_col[idx]] = idx

    true_match_scores = []
    for root_record, paired_records in true_matches.items():
        for pr in paired_records:
            score = 0.0
            for c in exact_cols:
                score += feature_match_log_odds_exact(
                    data[root_record],
                    data[pr],
                    cols_to_idx[c],
                    idx_to_col=idx_to_col,
                    log_odds=log_odds,
                )
            for c in fuzzy_cols:
                score += feature_match_log_odds_fuzzy_compare(
                    data[root_record],
                    data[pr],
                    cols_to_idx[c],
                    idx_to_col=idx_to_col,
                    log_odds=log_odds,
                )
            true_match_scores.append(score)

    non_match_scores = []
    for record_1, record_2 in neg_pairs:
        score = 0.0
        for c in exact_cols:
            score += feature_match_log_odds_exact(
                data[record_1],
                data[record_2],
                cols_to_idx[c],
                idx_to_col=idx_to_col,
                log_odds=log_odds,
            )
        for c in fuzzy_cols:
            score += feature_match_log_odds_fuzzy_compare(
                data[record_1],
                data[record_2],
                cols_to_idx[c],
                idx_to_col=idx_to_col,
                log_odds=log_odds,
            )
            non_match_scores.append(score)

    min_length = min(len(true_match_scores), len(non_match_scores))
    true_match_scores = true_match_scores[:min_length]
    non_match_scores = non_match_scores[:min_length]

    _, bins, _ = plt.hist(true_match_scores, bins=75, range=[0, 25])
    _ = plt.hist(non_match_scores, bins=bins, alpha=0.5)
    plt.show()


def read_linkage_config(config_file: pathlib.Path) -> List[dict]:
    """
    Reads and generates a record linkage algorithm configuration list from
    the provided filepath, which should point to a JSON file. A record
    linkage configuration list is a list of dictionaries--one for each
    pass in the algorithm it describes--containing information on the
    blocking fields, functions, cluster thresholds, and keyword arguments
    for that pass of the linkage algorithm. For a full example of all the
    components involved in a linkage description structure, see the doc
    string for `write_linkage_config`.

    :param config_file: A `pathlib.Path` string pointing to a JSON file
      that describes the algorithm to decode.
    :return: A list of dictionaries whose values can be passed to the
      various parts of linkage pass function.
    """
    try:
        with open(config_file) as f:
            algo_config = json.load(f)
            # Need to convert function keys back to column indices, since
            # JSON serializes dict keys as strings
            for rl_pass in algo_config.get("algorithm"):
                rl_pass["funcs"] = {
                    int(col): f for (col, f) in rl_pass["funcs"].items()
                }
            return algo_config.get("algorithm", [])
    except FileNotFoundError:
        raise FileNotFoundError(f"No file exists at path {config_file}.")
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError(
            "The specified file is not valid JSON.", e.doc, e.pos
        )


def score_linkage_vs_truth(
    found_matches: dict[Union[int, str], set],
    true_matches: dict[Union[int, str], set],
    records_in_dataset: int,
    expand_clusters_pairwise: bool = False,
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
    :param expand_clusters_pairwise: Optionally, whether we need to take
      the cross-product of members within the sets of the match list. This
      parameter only needs to be used if the linkage algorithm was run in
      cluster mode. Default is False.
    :return: A tuple reporting the sensitivity/precision, specificity/recall,
      positive prediction value, and F1 score of the linkage algorithm.
    """

    # If cluster mode was used, only the "master" patient's set will exist
    # Need to expand other permutations for accurate statistics
    if expand_clusters_pairwise:
        new_found_matches = {}
        for root_rec in found_matches:
            if root_rec not in new_found_matches:
                new_found_matches[root_rec] = found_matches[root_rec]
            for paired_record in found_matches[root_rec]:
                if paired_record not in new_found_matches:
                    new_found_matches[paired_record] = set()
                for other_record in found_matches[root_rec]:
                    if other_record > paired_record:
                        new_found_matches[paired_record].add(other_record)
        found_matches = new_found_matches

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

    print("True Positives:", true_positives)
    print("False Positives:", false_positives)
    print("False Negatives:", false_negatives)

    sensitivity = round(true_positives / (true_positives + false_negatives), 3)
    specificity = round(true_negatives / (true_negatives + false_positives), 3)
    ppv = round(true_positives / (true_positives + false_positives), 3)
    f1 = round(
        (2 * true_positives) / (2 * true_positives + false_negatives + false_positives),
        3,
    )
    return (sensitivity, specificity, ppv, f1)


def write_linkage_config(linkage_algo: List[dict], file_to_write: pathlib.Path) -> None:
    """
    Save a provided algorithm description as a JSON dictionary at the provided
    filepath location. Algorithm descriptions are lists of dictionaries, one
    for each pass of the algorithm, whose keys are parameter values for a
    linkage pass (drawn from the list `"funcs"`, `"blocks"`, `"matching_rule"`,
    and optionally `"cluster_ratio"` and `"kwargs"`) and whose values are
    as follows:

    - `"funcs"` should map to a dictionary mapping column index to the
    name of a function in the DIBBS linkage module (such as
    `feature_match_fuzzy_string`)--note that these are the actual
    functions, not string names of the functions
    - `"blocks"` should map to a list of columns to block on (e.g.
    ["MRN4", "ADDRESS4"])
    - `"matching_rule"` should map to one of the evaluation rule functions
    in the DIBBS linkage module (i.e. `eval_perfect_match`)
    - `"cluster_ratio"` should map to a float, if provided
    - `"kwargs"` should map to a dictionary of keyword arguments and their
    associated values, if provided

    Here's an example of a simple single-pass linkage algorithm that blocks
    on zip code, then matches on exact first name, exact last name, and
    fuzzy date of birth (using, say, Levenshtein similarity with a score
    threshold of 0.8) in dictionary descriptor form (for the sake of the
    example, let's assume the data has the column order first, last, DOB):

    [{
        "funcs": {
            0: feature_match_exact,
            1: feature_match_exact,
            2: feature_match_fuzzy_string,
            3: feature_match_fuzzy_string,
        },
        "blocks": ["ZIP"],
        "matching_rule": eval_perfect_match,
        "kwargs": {
            "similarity-measure": "Levenshtein",
            "threshold": 0.8
        }
    }]

    :param linkage_algo: A list of dictionaries whose key-value pairs correspond
      to the rules above.
    :param file_to_write: The path to the destination JSON file to write.
    """
    algo_json = []
    for rl_pass in linkage_algo:
        pass_json = {}
        pass_json["funcs"] = {col: f.__name__ for (col, f) in rl_pass["funcs"].items()}
        pass_json["blocks"] = rl_pass["blocks"]
        pass_json["matching_rule"] = rl_pass["matching_rule"].__name__
        if rl_pass.get("cluster_ratio", None) is not None:
            pass_json["cluster_ratio"] = rl_pass["cluster_ratio"]
        if rl_pass.get("kwargs", None) is not None:
            pass_json["kwargs"] = {
                kwarg: val for (kwarg, val) in rl_pass.get("kwargs", {}).items()
            }
        algo_json.append(pass_json)
    linkage_json = {"algorithm": algo_json}
    with open(file_to_write, "w") as out:
        out.write(json.dumps(linkage_json))


def _bind_func_names_to_invocations(algo_config: List[dict]):
    """
    Helper method that re-maps the string names of functions to their
    callable invocations as defined within the `link.py` module.
    """
    for lp in algo_config:
        feature_funcs = lp["funcs"]
        for func in feature_funcs:
            if isinstance(feature_funcs[func], str):
                feature_funcs[func] = globals()[feature_funcs[func]]
        if isinstance(lp["matching_rule"], str):
            lp["matching_rule"] = globals()[lp["matching_rule"]]
    return algo_config


def _eval_record_in_cluster(
    block: List[List],
    i: int,
    cluster: set,
    cluster_ratio: float,
    feature_funcs: dict[str, Callable],
    col_to_idx: dict[str, int],
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
            feature_funcs[feature_col](
                record_i, record_j, feature_col, col_to_idx, **kwargs
            )
            for feature_col in feature_funcs
        ]

        is_match = match_eval(feature_comps)
        if is_match:
            num_matched += 1.0
    if (num_matched / len(cluster)) >= cluster_ratio:
        return True
    return False


def _compare_records(
    record: List,
    mpi_patient: List,
    feature_funcs: dict,
    col_to_idx: dict[str, int],
    matching_rule: callable,
    **kwargs,
) -> bool:
    """
    Helper method that compares the flattened form of an incoming new
    patient record to the flattened form of a patient record pulled
    from the MPI.
    """
    # Format is patient_id, person_id, alphabetical list of FHIR keys
    # Don't use the first two ID cols when linking
    feature_comps = [
        _compare_records_field_helper(
            record[2:],
            mpi_patient[2:],
            feature_col,
            col_to_idx,
            feature_funcs,
            **kwargs,
        )
        for feature_col in feature_funcs
    ]
    is_match = matching_rule(feature_comps, **kwargs)
    return is_match


def _compare_records_field_helper(
    record: List,
    mpi_patient: List,
    feature_col: str,
    col_to_idx: dict[str, int],
    feature_funcs: dict,
    **kwargs,
) -> bool:
    if feature_col == "first_name":
        return _compare_name_elements(
            record, mpi_patient, feature_funcs, feature_col, col_to_idx, **kwargs
        )
    elif feature_col in ["address", "city", "state", "zip"]:
        return _compare_address_elements(
            record, mpi_patient, feature_funcs, feature_col, col_to_idx, **kwargs
        )
    else:
        return feature_funcs[feature_col](
            record, mpi_patient, feature_col, col_to_idx, **kwargs
        )


def _compare_address_elements(
    record: List,
    mpi_patient: List,
    feature_funcs: dict,
    feature_col: str,
    col_to_idx: dict[str, int],
    **kwargs,
) -> bool:
    """
    Helper method that compares all elements from the flattened form of an incoming
    new patient record to all elements of the flattened patient record pulled from
    the MPI.
    """
    feature_comp = False
    idx = col_to_idx[feature_col]
    for r in record[idx]:
        feature_comp = feature_funcs[feature_col](
            [r], [mpi_patient[idx]], feature_col, {feature_col: 0}, **kwargs
        )
        if feature_comp:
            break
    return feature_comp


def _compare_name_elements(
    record: List,
    mpi_patient: List,
    feature_funcs: dict,
    feature_col: str,
    col_to_idx: dict[str, int],
    **kwargs,
) -> bool:
    """
    Helper method that compares all elements from the flattened form of an incoming
    new patient record's name(s) to all elements of the flattened
    patient's name(s) pulled from the MPI.
    """
    idx = col_to_idx[feature_col]
    feature_comp = feature_funcs[feature_col](
        [" ".join(record[idx])],
        [mpi_patient[idx]],
        feature_col,
        {feature_col: 0},
        **kwargs,
    )
    return feature_comp


def _condense_extract_address_from_resource(resource: dict, field: str) -> List[str]:
    """
    Formatting function to account for patient resources that have multiple
    associated addresses. Each address is a self-contained object, replete
    with its own `line` property that can hold a list of strings. This
    function condenses that `line` into a single concatenated string, for
    each address object, and returns the result in a properly formatted
    list.

    :param resource: The patient resource to extract the address from.
    :param field: The field to extract the address from.
    :return: A list of strings, each string representing a single address.
    """
    expanded_address_fhirpath = LINKING_FIELDS_TO_FHIRPATHS[field]
    expanded_address_fhirpath = ".".join(expanded_address_fhirpath.split(".")[:-1])
    list_of_address_objects = (
        extract_value_with_resource_path(resource, expanded_address_fhirpath, "all")
        or []
    )
    if not list_of_address_objects:
        return None

    if field == "address":
        list_of_address_lists = [
            ao.get(LINKING_FIELDS_TO_FHIRPATHS[field].split(".")[-1], [])
            for ao in list_of_address_objects
        ]
        list_of_usable_address_elements = [
            " ".join(obj) for obj in list_of_address_lists
        ]
    else:
        list_of_usable_address_elements = []
        for address_object in list_of_address_objects:
            list_of_usable_address_elements.append(
                address_object.get(LINKING_FIELDS_TO_FHIRPATHS[field].split(".")[-1])
            )

    return list_of_usable_address_elements


def _find_strongest_link(linkage_scores: dict) -> str:
    """
    Helper method that determines the highest belongingness level that an
    incoming record achieved against a set of clusers based on existing
    patient records in the MPI. The cluster with the highest belongingness
    ratio is chosen as the Person to link the new record to.
    """
    best_person = max(linkage_scores, key=linkage_scores.get)
    return best_person


def _flatten_patient_resource(resource: dict, col_to_idx: dict) -> List:
    """
    Helper method that flattens an incoming patient resource into a list whose
    elements are the keys of the FHIR dictionary, reformatted and ordered
    according to our "blocking fields extractor" dictionary.
    """
    flattened_record = [
        _flatten_patient_field_helper(resource, f) for f in col_to_idx.keys()
    ]
    flattened_record = [resource["id"], None] + flattened_record
    return flattened_record


def _flatten_patient_field_helper(resource: dict, field: str) -> any:
    """
    Helper function that determines the correct way to flatten a patient's
    FHIR field based on the specific field in question. Names and Addresses,
    because their lists can hold multiple objects, are fetched completely,
    whereas other fields just have their first element used (since historical
    information doesn't matter there).

    For any field for which the value would be `None`, instead use an empty string
    (if the field isn't first_name or address) or a list with one element, the
    empty string (if the field is first_name or address). This ensures that
    future loops over the elements don't disrupt the flow of the matching
    algorithm.
    """
    if field == "first_name":
        vals = extract_value_with_resource_path(
            resource, LINKING_FIELDS_TO_FHIRPATHS[field], selection_criteria="all"
        )
        return vals if vals is not None else [""]
    elif field in ["address", "city", "zip", "state"]:
        vals = _condense_extract_address_from_resource(resource, field)
        return vals if vals is not None else [""]
    else:
        val = extract_value_with_resource_path(
            resource, LINKING_FIELDS_TO_FHIRPATHS[field], selection_criteria="first"
        )
        return val if val is not None else ""


def _group_patient_block_by_person(data_block: List[list]) -> dict[str, List]:
    """
    Helper method that partitions the block of patient data returned from the MPI
    into clusters of records according to their linked Person ID.
    """
    clusters = {}
    for mpi_patient in data_block:
        # Format is patient_id, person_id, alphabetical list of FHIR keys
        if mpi_patient[1] not in clusters:
            clusters[mpi_patient[1]] = []
        clusters[mpi_patient[1]].append(mpi_patient)
    return clusters


def _map_matches_to_record_ids(
    match_list: Union[List[tuple], List[set]], data_block, cluster_mode: bool = False
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
    feature_funcs: dict[str, Callable],
    col_to_idx: dict[str, int],
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
    :param col_to_idx: A dictionary mapping column names to the numeric index
      in which they occur in order in the data.
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
                block,
                i,
                cluster,
                cluster_ratio,
                feature_funcs,
                col_to_idx,
                match_eval,
                **kwargs,
            )
            if belongs:
                found_master_cluster = True
                cluster.add(i)
                break

        # Create a new singleton if no other cluster qualified
        if not found_master_cluster:
            clusters.append({i})
    return clusters


def _is_empty_extraction_field(block_vals: dict, field: str):
    """
    Helper method that determines when a field extracted from an incoming
    record should be considered "empty" for the purpose of blocking.
    Fields whose values are either `None` or the empty string should not
    be used when retrieving blocked records from the MPI, since that
    would impose an artificial constraint (e.g. if an incoming record
    has no `last_name` field, we don't want to retrieve only records
    from the MPI that also have no `last_name`).
    """
    # Means the value extractor found no data in the FHIR resource
    if block_vals[field] == "":
        return True
    # Alternatively, there was "data" there, but it's empty
    elif (
        block_vals[field].get("value") is None
        or block_vals[field].get("value") == ""
        or block_vals[field].get("value") == [""]
    ):
        return True  # pragma: no cover
    return False


def _write_prob_file(prob_dict: dict, file_to_write: Union[pathlib.Path, None]):
    """
    Helper method to write a probability dictionary to a JSON file, if
    a valid path is supplied.

    :param prob_dict: A dictionary mapping column names to the log-probability
      values computed for those columns.
    :param file_to_write: Optionally, a path variable indicating where to
      write the probabilities in a JSON format. Default is None (meaning this
      function would execute nothing.)
    """
    if file_to_write is not None:
        with open(file_to_write, "w") as out:
            out.write(json.dumps(prob_dict))


def add_person_resource(
    person_id: str, patient_id: str, bundle: dict = Field(description="A FHIR bundle")
) -> dict:
    """
    Adds a simplified person resource to a bundle if the patient resource in the bundle
    matches an existing record in the Master Patient Index. Returns the bundle with
    the newly added person resource.

    :param person_id: _description_
    :param patient_id: _description_
    :param bundle: _description_, defaults to Field(description="A FHIR bundle")
    :return: _description_
    """
    person_resource = {
        "fullUrl": f"urn:uuid:{person_id}",
        "resource": {
            "resourceType": "Person",
            "id": f"{person_id}",
            "link": [{"target": {"reference": f"Patient/{patient_id}"}}],
        },
        "request": {
            "method": "PUT",
            "url": f"Person/{person_id}",
        },
    }

    bundle.get("entry", []).append(person_resource)

    return bundle


def _convert_given_name_to_first_name(data: list[list]) -> list[list]:
    """
    In the list of query row results, convert the given_name column (which is a
    list of given names) to a first_name column (which is a space-delimited string
    of given names).

    :param data: List of lists block data.
    :return: List of lists with first_name column.
    """
    result = []
    if not data:
        return result  # empty list, should return an empty list

    if "given_name" not in data[0]:
        return data  # given_name not in data, should return the original

    given_name_idx = data[0].index("given_name")
    for idx, row in enumerate(data):
        val = "first_name" if idx == 0 else " ".join(row[given_name_idx])
        result.append(row[:given_name_idx] + [val] + row[given_name_idx + 1 :])
    return result
