from phdi.linkage import generate_hash_str


def test_generate_hash():

    salt_str = "super-legit-salt"
    patient_1 = "John-Shepard-2153/11/07-1234 Silversun Strip Zakera Ward Citadel 99999"
    patient_2 = "Tali-Zora-Vas-Normandy-2160/05/14-PO Box 1 Rock Rannoch"

    hash_1 = generate_hash_str(patient_1, salt_str)
    hash_2 = generate_hash_str(patient_2, salt_str)

    assert hash_1 == "0aa5aa1f6183a24670b2e1848864514e119ae6ca63bb35246ef215e7a0746a35"
    assert hash_2 == "102818c623290c24069beb721c6eb465d281b3b67ecfb6aef924d14affa117b9"
