"""
Optional -- this script replaces the anonymised study IDs with original MRNs
using a keys csv file in "input/keys" (gitignored)

Ensure the column of study IDs in both csv files are named the same way.

Author: Kostas Moschonas
Date: 16-04-2025
"""

import pandas as pd

# Load data
main_data = pd.read_csv("output/mavacamten_20250415.csv")
# Load keys
keys_df = pd.read_csv("keys/keys_mava_27.csv")

# rename the column containing the anonymised study IDs in main data to "study_id"
main_data.rename(columns={"mrn": "study_id"}, inplace=True)

# Perform the join on the common column (e.g., 'StudyID')
# Replace 'common_column' with the actual column name used for joining
merged_df = main_data.merge(keys_df, on="study_id", how="left")

# Save the resulting DataFrame to a new CSV file
merged_df.to_csv("output/mavacamten_mrns_20250415.csv", index=False)