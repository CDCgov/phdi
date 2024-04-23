# Copied from phdi/tests/test_data_generator.py
# TODO: Move this to dibbs SDK when it is created


def generate_list_patients_contact():
    patient_data = [
        ["11-7-2153", "John", "Shepard", "", "", "", "", "90909", 1],
        ["11-7-2153", "Jhon", "Sheperd", "", "", "", "", "90909", 5],
        ["11-7-2153", "Jon", "Shepherd", "", "", "", "", "90909", 11],
        ["11-7-2153", "Johnathan", "Shepard", "", "", "", "", "90909", 12],
        ["11-7-2153", "Nathan", "Shepard", "", "", "", "", "90909", 13],
        ["01-10-1986", "Jane", "Smith", "", "", "", "", "12345", 14],
        ["12-12-1992", "Daphne", "Walker", "", "", "", "", "23456", 18],
        ["1-1-1980", "Alejandro", "Villanueve", "", "", "", "", "15935", 23],
        ["1-1-1980", "Alejandro", "Villanueva", "", "", "", "", "15935", 24],
        ["2-2-1990", "Philip", "", "", "", "", "", "64873", 27],
        ["1-1-1980", "Alejandr", "Villanueve", "", "", "", "", "15935", 31],
        ["1-1-1980", "Aelxdrano", "Villanueve", "", "", "", "", "15935", 32],
    ]
    return patient_data


def generate_eicr_results():
    eicr_result = {
        "root": "2.16.840.1.113883.9.9.9.9.9",
        "extension": "db734647-fc99-424c-a864-7e3cda82e704",
    }
    return eicr_result


def generate_ecr_msg_ids():
    msg_ids = {
        "internal_message": {"id1": ["ID1"], "id2": "SecondID"},
        "external_id": ["extID"],
        "last_id": "123",
    }
    return msg_ids
