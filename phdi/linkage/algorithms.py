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
        },
    },
]
