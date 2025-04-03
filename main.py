"""
Script to extract metadata from DICOM files in zipped folders and save it to a CSV file.

This script uses the `MetadataExtraction` class to find DICOM files based on their Series Description,
extract metadata, and save the metadata to a CSV file.

Author: Kostas Moschonas
Date: 02/04/2025
"""

from extract_dicom_metadata import MetadataExtraction
import pandas as pd

# USER DEFINED VARIABLES
zip_folder_path = "input/zipped"
stress_sequences = "stress"
rest_sequences = "rest"

# Create an instance of MetadataExtraction
metadata_extractor = MetadataExtraction()

# Stress sequences
# Find DICOM files
stress_dicom_files = metadata_extractor.find_dicom_in_zip_folder_by_series_description(zip_folder_path, stress_sequences)
metadata_extractor.dicom_files = stress_dicom_files
# Extract metadata
stress_metadata_df = metadata_extractor.extract_metadata()

# Rest sequences
# Find DICOM files
rest_dicom_files = metadata_extractor.find_dicom_in_zip_folder_by_series_description(zip_folder_path, rest_sequences)
metadata_extractor.dicom_files = rest_dicom_files
# Extract metadata
rest_metadata_df = metadata_extractor.extract_metadata()

# Merge the two dataFrames
merged_metadata_df = pd.concat([stress_metadata_df, rest_metadata_df], ignore_index=True)

# Save the merged dataFrame to a CSV file
merged_metadata_df.to_csv("output/merged_metadata_cmr.csv", index=False)
# print("CSV saved: output/merged_metadata_cmr.csv")
