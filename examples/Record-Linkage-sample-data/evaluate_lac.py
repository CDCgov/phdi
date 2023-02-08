import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

import pandas as pd

from phdi.linkage import lac_validation_linkage, score_linkage_vs_truth

DATA_SIZE = 50000


def determine_true_matches_in_pd_dataset(data: pd.DataFrame):
    pass


data = pd.read_csv("./sample_record_linkage_data_scrambled.csv", dtype="string")
cols_to_keep = [
    "Id",
    "BIRTHDATE",
    "FIRST",
    "LAST",
    "GENDER",
    "ADDRESS",
    "CITY",
    "STATE",
    "ZIP",
]
data = data.loc[:DATA_SIZE]
data = data.drop(columns=[c for c in data.columns if not c in cols_to_keep])

print("-------Identifying True Matches for Evaluation-------")
true_matches = {}
tuple_data = tuple(data.groupby("Id"))
for master_patient, sub_df in tuple_data:
    sorted_idx = sorted(sub_df.index)
    for idx in range(len(sorted_idx)):
        r_idx = sorted_idx[idx]
        if not r_idx in true_matches:
            true_matches[r_idx] = set()
        for i in range(idx + 1, len(sorted_idx)):
            true_matches[r_idx].add(sorted_idx[i])
data["ID"] = data.index
data = data.drop(columns=["Id"])

matches = lac_validation_linkage(data, None)
sensitivitiy, specificity, ppv, f1 = score_linkage_vs_truth(
    matches, true_matches, DATA_SIZE
)
print("Sensitivity:", sensitivitiy)
print("Specificity:", specificity)
print("PPV:", ppv)
print("F1:", f1)
