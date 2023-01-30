from phdi.linkage.link import generate_hash_str, block_parquet_data
import os
import pandas as pd


def test_generate_hash():

    salt_str = "super-legit-salt"
    patient_1 = "John-Shepard-2153/11/07-1234 Silversun Strip Zakera Ward Citadel 99999"
    patient_2 = "Tali-Zora-Vas-Normandy-2160/05/14-PO Box 1 Rock Rannoch"

    hash_1 = generate_hash_str(patient_1, salt_str)
    hash_2 = generate_hash_str(patient_2, salt_str)

    assert hash_1 == "0aa5aa1f6183a24670b2e1848864514e119ae6ca63bb35246ef215e7a0746a35"
    assert hash_2 == "102818c623290c24069beb721c6eb465d281b3b67ecfb6aef924d14affa117b9"


def test_block_parquet_data():
    # Create data for testing
    test_data = {
        "id": [0, 1, 2, 3],
        "first_name": ["Marc", "Mark", "Jose", "Eliza"],
        "last_name": ["Gutierrez", "Smith", "Garcia", "Jones"],
        "zip": [90210, 90210, 90210, 90006],
        "year_of_birth": [1980, 1992, 1992, 1992],
    }
    test_data_df = pd.DataFrame.from_dict(test_data)

    if os.path.isfile("./test.parquet"):  # pragma: no cover
        os.remove("./test.parquet")
    test_data_df.to_parquet(path="./test.parquet", engine="pyarrow")

    blocked_test_data = block_parquet_data(path="./test.parquet", blocks=["zip"])

    for key, value in blocked_test_data.items():
        print("ZIP:", key)
        print(value)
        print()
    # Test output data types are correct
    assert isinstance(blocked_test_data, dict)
    assert isinstance(blocked_test_data[90006], list)

    # Test that the number of blocks is the same as the distinct number of zip codes
    assert len(blocked_test_data.keys()) == test_data_df["zip"].nunique()

    # Test blocks with multiple block columns
    blocked_test_data = block_parquet_data(
        path="./test.parquet", blocks=["zip", "year_of_birth"]
    )
    assert len(blocked_test_data[(90210, 1992)]) == 2

    # Clean up
    if os.path.isfile("./test.parquet"):  # pragma: no cover
        os.remove("./test.parquet")
