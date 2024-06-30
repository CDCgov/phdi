import pandas as pd
import random
from faker import Faker

# Sample data from the user
source_data_with_copies = pd.DataFrame({
    'Id': [10000, 10001, 10002, 10003, 10004],
    'BIRTHDATE': ['11-5-10', '6-8-08', '12-22-15', '8-21-87', '11-28-76'],
    'DEATHDATE': [None] * 5,
    'SSN': ['999-96-4656', '999-12-5114', '999-25-4120', '999-78-4008', '999-14-7102'],
    'DRIVERS': [None, None, None, 'S99932967', 'S99921070'],
    'PASSPORT': [None, None, None, 'X71799863X', 'X17545263X'],
    'PREFIX': [None, None, None, 'Ms.', 'Mr.'],
    'FIRST': ['Aubrey', 'David', 'Sofia', 'Amiee', 'Antwan'],
    'MIDDLE': ['Buddy', 'Alvin', 'Lourdes', 'Dennise', 'Jeff'],
    'LAST': ['Kunde', 'Boyle', 'Lucero', 'Friesen', 'Kreiger'],
    'SUFFIX': [None] * 5,
    'Column1': [None] * 5,
    'MARITAL': [None, None, None, 'S', 'S'],
    'RACE': ['white', 'white', 'white', 'asian', 'white'],
    'ETHNICITY': ['nonhispanic', 'nonhispanic', 'hispanic', 'nonhispanic', 'nonhispanic'],
    'GENDER': ['M', 'M', 'F', 'F', 'M'],
    'BIRTHPLACE': ['Stockport  New York  US', 'New York  New York  US', 'Puebla  Puebla  MX', 'Shanghai  Shanghai Municipality  CN', 'Greenlawn  New York  US'],
    'ADDRESS': ['104 Bergstrom Corner', '964 Heidenreich Gate Unit 39', '439 Yundt Well Unit 53', '639 Wunsch Mews', '699 Schiller Row Unit 54'],
    'CITY': ['New York', 'New York', 'New York', 'New York', 'New York'],
    'STATE': ['New York', 'New York', 'New York', 'New York', 'New York'],
    'COUNTY': ['New York County', 'New York County', 'New York County', 'New York County', 'New York County'],
    'FIPS': [36061, 36085, 36081, 36047, 36047],
    'ZIP': [10172, 10301, 11694, 11220, 11237],
    'INCOME': [3418, 16343, 193518, 52353, 128959]
})

faker = Faker()
seed = 42

PROPOTION_COMMONLY_SHORT_NAMES = 0.5

# Assuming the short-names CSV file contains the following structure:
# Name,Nickname1,Nickname2,...
short_names_df = pd.DataFrame({
    'Name': ['AUBREY', 'DAVID', 'SOFIA', 'AMIEE', 'ANTWAN'],
    'Nickname1': ['Bree', 'Dave', 'Soph', 'Amy', 'Tony'],
    'Nickname2': ['Aub', 'D', 'S', 'Aim', 'Ant']
})

# Extract the 'Name' column into a list and convert to uppercase
short_names_list = short_names_df['Name'].str.upper().tolist()

# Convert 'FIRST' column to uppercase for case-insensitive comparison
source_data_with_copies['FIRST'] = source_data_with_copies['FIRST'].str.upper()

# Debug: Print source data and short names list
print("Source data 'FIRST' column:\n", source_data_with_copies['FIRST'])
print("Short names list:", short_names_list)

# Manual match check
matched_indices = []
for index, row in source_data_with_copies.iterrows():
    if row['FIRST'] in short_names_list:
        matched_indices.append(index)
        print(f"Match found: {row['FIRST']} at index {index}")

# Filter the source dataset to only include records with 'FIRST' name in the short-names list
filtered_data = source_data_with_copies.loc[matched_indices]
print("Filtered data:\n", filtered_data)

# Check if there is any data left after filtering
if filtered_data.empty:
    print("No records match the short names.")
else:
    # Create samples
    commonlyShortNames = filtered_data.sample(frac=PROPOTION_COMMONLY_SHORT_NAMES, random_state=seed).copy()
    for index, row in commonlyShortNames.iterrows():
        # Check if there's a match in short_names_df
        matching_row = short_names_df[short_names_df['Name'].str.upper() == row['FIRST']]
        if not matching_row.empty:
            # Select variations (nicknames) for the matched name
            variations = matching_row.iloc[:, 1:].values.flatten().tolist()  # Assuming variations are in columns from the second onward
            if variations:
                selected_variation = random.choice(variations)
                commonlyShortNames.at[index, 'FIRST'] = selected_variation
            else:
                commonlyShortNames.at[index, 'FIRST'] = row['FIRST'][:2]  # Use first two letters if no variations exist
        else:
            commonlyShortNames.at[index, 'FIRST'] = row['FIRST'][:2]  # Use first two letters if no match is found

    commonlyShortNames['GroundTruth'] = 'Match'
    commonlyShortNames['Description'] = "commonlyShortNames"
    commonlyShortNames['Scenario #'] = "8"
    
    print(commonlyShortNames)  # Debug: Print the result
