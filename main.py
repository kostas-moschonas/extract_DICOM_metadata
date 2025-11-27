"""
Script to extract metadata from DICOM files in zipped folders and save it to a CSV file.

This script uses the `MetadataExtraction` class to find DICOM files based on their Series Description,
extract metadata, and save the metadata to a CSV file.

Author: Kostas Moschonas
Updated: 27-11-2025
"""

from extract_dicom_metadata import MetadataExtraction
import pandas as pd
import re

# ## Series descriptions
# stress_sequences = "stress"
# rest_sequences = "rest"

# More thorough filtering for series descriptions
# More thorough filtering for series descriptions
def is_stress_sequence(series_description):
    """Check if the series description contains both stress and perf,
    to avoid picking other stress sequences like stress cine, etc."""
    # Normalize by converting to lower case and removing spaces and underscores
    normalized_description = re.sub(r'[\s_]+', '', series_description.lower())
    return "stress" in normalized_description and "perf" in normalized_description

def is_rest_sequence(series_description):
    """Check if the series description contains both rest and perf,
        to avoid picking other rest sequences inadvertedly labelled rest"""
    # Normalize by converting to lower case and removing spaces and underscores
    normalized_description = re.sub(r'[\s_]+', '', series_description.lower())
    return "rest" in normalized_description and "perf" in normalized_description

def is_perf_only_sequence(series_description):
    """Check if the series description contains perf, but not stress or rest."""
    normalized_description = re.sub(r'[\s_]+', '', series_description.lower())
    return "perf" in normalized_description and "stress" not in normalized_description and "rest" not in normalized_description

# USER DEFINED VARIABLES ----
## Folder paths, choose appropriate methods below for zipped and non-zipped folders accordingly
# zip_folder_path = "input/zipped"
folder_path = r"D:\cmrs\mavacamten_study\test"

# Path and name of the output CSV file
output_csv_path = "output/test.csv"

# RUNNING CODE ----
# Create an instance of MetadataExtraction
metadata_extractor = MetadataExtraction()

# Stress sequences
# Find DICOM files
# for zipped folder:
# stress_dicom_files = metadata_extractor.find_dicom_in_zip_folder_by_series_description(zip_folder_path, stress_sequences)
# for non zipped folder:
stress_dicom_files = metadata_extractor.find_dicom_in_folder_by_series_description(
    folder_path, filter_function=is_stress_sequence
)

# If no stress files found, search for "perf" only sequences
if not stress_dicom_files:
    stress_dicom_files = metadata_extractor.find_dicom_in_folder_by_series_description(
        folder_path, filter_function=is_perf_only_sequence
    )

metadata_extractor.dicom_files = stress_dicom_files

# Extract metadata
stress_metadata_df = metadata_extractor.extract_metadata()

# Rest sequences
# Find DICOM files
# for zipped folder:
# rest_dicom_files = metadata_extractor.find_dicom_in_zip_folder_by_series_description(zip_folder_path, rest_sequences)
# for non zipped folder:
rest_dicom_files = metadata_extractor.find_dicom_in_folder_by_series_description(
    folder_path, filter_function=is_rest_sequence
)

if not rest_dicom_files:
    rest_dicom_files = metadata_extractor.find_dicom_in_folder_by_series_description(
        folder_path, filter_function=is_perf_only_sequence
    )

metadata_extractor.dicom_files = rest_dicom_files

# Extract metadata
rest_metadata_df = metadata_extractor.extract_metadata()

# Merge the two dataFrames
merged_metadata_df = pd.concat([stress_metadata_df, rest_metadata_df], ignore_index=True)

# Save the merged dataFrame to a CSV file
merged_metadata_df.to_csv(output_csv_path, index=False)
# print("CSV saved: output/merged_metadata_cmr.csv")
