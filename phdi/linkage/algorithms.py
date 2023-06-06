# Predefined columns that map to the DIBBs MPI
IDX_TO_COL = {
    0: "address",
    1: "birthdate",
    2: "city",
    3: "first_name",
    4: "last_name",
    5: "mrn",
    6: "sex",
    7: "state",
    8: "zip",
}

# Pre-computed log-odds points values for each of the DIBBs MPI
# supported columns (derived from representative synthetic data)
LOG_ODDS_SCORES = {
    "birthdate": 9.944142836217619,
    "first_name": 8.009121400325398,
    "last_name": 5.327681398982514,
    "sex": 0.6964525713514773,
    "address": 5.769942276960749,
    "city": 1.8002552875091014,
    "state": 0.0,
    "zip": 4.909466232098861,
    "mrn": 1.464232660081324,
}


DIBBS_BASIC = [
    {
        "funcs": {
            1: "feature_match_fuzzy_string",
            3: "feature_match_fuzzy_string",
            4: "feature_match_fuzzy_string",
        },
        "blocks": [
            {"value": "mrn", "transformation": "last4"},
            {"value": "address", "transformation": "first4"},
        ],
        "matching_rule": "eval_perfect_match",
        "cluster_ratio": 0.9,
    },
    {
        "funcs": {
            0: "feature_match_fuzzy_string",
            2: "feature_match_fuzzy_string",
        },
        "blocks": [
            {"value": "first_name", "transformation": "first4"},
            {"value": "last_name", "transformation": "first4"},
        ],
        "matching_rule": "eval_perfect_match",
        "cluster_ratio": 0.9,
    },
]


DIBBS_ENHANCED = [
    {
        "funcs": {
            1: "feature_match_log_odds_fuzzy_compare",
            3: "feature_match_log_odds_fuzzy_compare",
            4: "feature_match_log_odds_fuzzy_compare",
        },
        "blocks": [
            {"value": "mrn", "transformation": "last4"},
            {"value": "address", "transformation": "first4"},
        ],
        "matching_rule": "eval_log_odds_cutoff",
        "cluster_ratio": 0.9,
        "kwargs": {
            "similarity_measure": "JaroWinkler",
            "threshold": 0.7,
            "true_match_threshold": 16.5,
            "idx_to_col": IDX_TO_COL,
            "log_odds": LOG_ODDS_SCORES,
        },
    },
    {
        "funcs": {
            0: "feature_match_log_odds_fuzzy_compare",
            2: "feature_match_log_odds_fuzzy_compare",
        },
        "blocks": [
            {"value": "first_name", "transformation": "first4"},
            {"value": "last_name", "transformation": "first4"},
        ],
        "matching_rule": "eval_log_odds_cutoff",
        "cluster_ratio": 0.9,
        "kwargs": {
            "similarity_measure": "JaroWinkler",
            "threshold": 0.7,
            "true_match_threshold": 7.0,
            "idx_to_col": IDX_TO_COL,
            "log_odds": LOG_ODDS_SCORES,
        },
    },
]
