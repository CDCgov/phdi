# DEFAULT DIBBS ALGORITHMS
# These algorithms and log odds scores are the updated values developed after
# substantial statistical tuning.

LOG_ODDS_SCORES = {
    "address": 8.438284928858774,
    "birthdate": 10.126641103800338,
    "city": 2.438553006137189,
    "first_name": 6.849475906891162,
    "last_name": 6.350720397426025,
    "mrn": 0.3051262572525359,
    "sex": 0.7510419059643679,
    "state": 0.022376768992488694,
    "zip": 4.975031471124867,
}
FUZZY_THRESHOLDS = {
    "first_name": 0.9,
    "last_name": 0.9,
    "birthdate": 0.95,
    "address": 0.9,
    "city": 0.92,
    "zip": 0.95,
}

DIBBS_BASIC = [
    {
        "funcs": {
            "first_name": "feature_match_fuzzy_string",
            "last_name": "feature_match_exact",
        },
        "blocks": [
            {"value": "birthdate"},
            {"value": "mrn", "transformation": "last4"},
            {"value": "sex"},
        ],
        "matching_rule": "eval_perfect_match",
        "cluster_ratio": 0.9,
        "kwargs": {"thresholds": FUZZY_THRESHOLDS},
    },
    {
        "funcs": {
            "address": "feature_match_fuzzy_string",
            "birthdate": "feature_match_exact",
        },
        "blocks": [
            {"value": "zip"},
            {"value": "first_name", "transformation": "first4"},
            {"value": "last_name", "transformation": "first4"},
            {"value": "sex"},
        ],
        "matching_rule": "eval_perfect_match",
        "cluster_ratio": 0.9,
        "kwargs": {"thresholds": FUZZY_THRESHOLDS},
    },
]

DIBBS_ENHANCED = [
    {
        "funcs": {
            "first_name": "feature_match_log_odds_fuzzy_compare",
            "last_name": "feature_match_log_odds_fuzzy_compare",
        },
        "blocks": [
            {"value": "birthdate"},
            {"value": "mrn", "transformation": "last4"},
            {"value": "sex"},
        ],
        "matching_rule": "eval_log_odds_cutoff",
        "cluster_ratio": 0.9,
        "kwargs": {
            "similarity_measure": "JaroWinkler",
            "thresholds": FUZZY_THRESHOLDS,
            "true_match_threshold": 12.2,
            "log_odds": LOG_ODDS_SCORES,
        },
    },
    {
        "funcs": {
            "address": "feature_match_log_odds_fuzzy_compare",
            "birthdate": "feature_match_log_odds_fuzzy_compare",
        },
        "blocks": [
            {"value": "zip"},
            {"value": "first_name", "transformation": "first4"},
            {"value": "last_name", "transformation": "first4"},
            {"value": "sex"},
        ],
        "matching_rule": "eval_log_odds_cutoff",
        "cluster_ratio": 0.9,
        "kwargs": {
            "similarity_measure": "JaroWinkler",
            "thresholds": FUZZY_THRESHOLDS,
            "true_match_threshold": 17.0,
            "log_odds": LOG_ODDS_SCORES,
        },
    },
]
