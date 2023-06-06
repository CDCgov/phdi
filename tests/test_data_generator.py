class TestDataGenerator:
    def generate_list_patients_contact(self):
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

    def generate_similar_address(self):
        record = [
            ["123"],
            ["1"],
            ["John", "Paul", "George"],
            ["1980-01-01"],
            ["123 Main St"],
        ]
        record2 = [
            ["123"],
            ["1"],
            ["John", "Paul", "George"],
            ["1980-01-01"],
            ["123 Main St", "9 North Ave"],
        ]
        mpi_patient1 = [
            ["456"],
            ["2"],
            ["John", "Paul", "George", "Ringo"],
            ["1980-01-01"],
            ["756 South St", "123 Main St", "489 North Ave"],
        ]
        mpi_patient2 = [
            ["789"],
            ["3"],
            ["Pierre"],
            ["1980-01-01"],
            ["6 South St", "23 Main St", "9 North Ave"],
        ]

        return record, record2, mpi_patient1, mpi_patient2
