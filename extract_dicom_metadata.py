"""
Module for extracting metadata from DICOM files.

Author: Kostas Moschonas
Updated: 27-11-2025
"""
import os
import zipfile
import tempfile
import re
from typing import Dict, Optional

import pydicom
import pandas as pd


class MetadataExtraction:
    """
    Extract metadata from DICOM files found in folders or zip archives.

    Progress print statements are added to each step so the user can follow execution.
    """

    def __init__(self, dicom_files: Optional[Dict[str, pydicom.dataset.FileDataset]] = None,
                 root_directory: Optional[str] = None):
        # Provided mapping of file path -> pydicom dataset or None to be filled by finder methods
        self.dicom_files = dicom_files
        # Optional root directory (not used directly in current methods but kept for API compatibility)
        self.root_directory = root_directory
        # Will hold the final pandas DataFrame after extraction
        self.metadata: Optional[pd.DataFrame] = None

    def find_dicom_by_series_description(self, folder_path: str, search_string: str):
        """
        Walk `folder_path` and return the first DICOM dataset whose SeriesDescription contains `search_string`.

        Prints progress for each file inspected and when a match is found.
        """
        print(f"Searching folder `{folder_path}` for SeriesDescription containing: `{search_string}`")
        for root, _, files in os.walk(folder_path):
            for file in files:
                dicom_path = os.path.join(root, file)
                try:
                    # Attempt to read as DICOM; `force=False` lets pydicom validate file structure
                    dicom_file = pydicom.dcmread(dicom_path, force=False)
                    series_description = str(dicom_file.get('SeriesDescription', 'NA'))
                    # Inform about the file checked (kept concise)
                    print(f"  checked: {dicom_path} -> SeriesDescription: {series_description}")
                    if search_string.lower() in series_description.lower():
                        print(f"  FOUND match: {dicom_path}")
                        return dicom_file
                except pydicom.errors.InvalidDicomError:
                    # File is not a valid DICOM; skip and show a short message
                    print(f"  skipped (not a DICOM): {dicom_path}")
                    continue
        print(f"No matching DICOM found in `{folder_path}`.")
        return None

    def find_dicom_in_zip_by_series_description(self, zip_path: str, search_string: str):
        """
        Extract a zip to a temporary directory and search inside for the requested SeriesDescription.
        """
        print(f"Searching zip file `{zip_path}` for SeriesDescription containing: `{search_string}`")
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            # Delegate to folder search and return first matching dataset
            result = self.find_dicom_by_series_description(temp_dir, search_string)
            if result is not None:
                print(f"  match found inside zip `{zip_path}`")
            else:
                print(f"  no match inside zip `{zip_path}`")
            return result

    def find_dicom_in_zip_folder_by_series_description(self, zip_folder_path: str, search_string: str):
        """
        Walk `zip_folder_path` looking for .zip files and search each zip for a matching SeriesDescription.
        Returns a dict mapping `zip_path` -> matching pydicom dataset (for zips that contain a match).
        """
        print(f"Searching folder `{zip_folder_path}` for zip files to inspect...")
        dicom_files = {}
        for root, _, files in os.walk(zip_folder_path):
            for file in files:
                if file.lower().endswith(".zip"):
                    zip_path = os.path.join(root, file)
                    print(f" Inspecting zip: {zip_path}")
                    dicom_file = self.find_dicom_in_zip_by_series_description(zip_path, search_string)
                    if dicom_file is not None:
                        dicom_files[zip_path] = dicom_file
                        print(f"  recorded match from `{zip_path}`")
        if not dicom_files:
            print(f"No matches found in any zip file under `{zip_folder_path}`.")
        return dicom_files

    def find_dicom_in_folder_by_series_description(self, folder_path: str, filter_function=None):
        """
        Find one representative DICOM dataset per (PatientID, StudyDate) pair in `folder_path`.
        Uses `filter_function(series_description)` to decide whether a file qualifies.
        Returns a dict mapping file_path -> pydicom dataset.
        """
        print(f"Scanning folder `{folder_path}` for DICOM files matching filter...")
        dicom_files = {}
        processed_study_keys = set()
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    dicom_file = pydicom.dcmread(file_path, force=False)
                except pydicom.errors.InvalidDicomError:
                    print(f"  skipped (not DICOM): {file_path}")
                    continue

                series_description = str(dicom_file.get('SeriesDescription', 'NA'))
                if filter_function and not filter_function(series_description):
                    # Skip files that don't match the provided filter
                    continue

                patient_id = dicom_file.get('PatientID', 'NA')
                study_date = dicom_file.get('StudyDate', 'NA')
                study_key = (patient_id, study_date)
                # Keep one file per patient/study combination
                if study_key not in processed_study_keys:
                    dicom_files[file_path] = dicom_file
                    processed_study_keys.add(study_key)
                    print(f"  recorded: {file_path} (PatientID={patient_id}, StudyDate={study_date})")
        if not dicom_files:
            print(f"No DICOM files matching the filter found in `{folder_path}`.")
        return dicom_files

    def _normalize_numeric(self, value):
        """
        Convert a possibly messy numeric value (e.g., '170 cm', '70.5') to a numeric type or pd.NA.
        """
        if value is None:
            return pd.NA
        # Try direct numeric conversion first
        try:
            return pd.to_numeric(value)
        except Exception:
            pass
        # Otherwise extract the first numeric token from a string
        s = str(value).strip()
        m = re.search(r'[-+]?\d*\.?\d+', s)
        if m:
            try:
                # Keep as float for measurements
                return float(m.group(0))
            except Exception:
                return pd.NA
        return pd.NA

    def _extract_metadata_from_dicom(self, dicom_file: pydicom.dataset.FileDataset) -> Dict:
        """
        Extract the fields of interest from a single pydicom dataset.
        Strictly uses `PatientID` for the `patient_ID` field (no fallback).
        """
        # Compose a simple dict of raw values (conversion/parsing happens later)
        return {
            'patient_ID': dicom_file.get('PatientID', 'NA'),
            'dob': dicom_file.get('PatientBirthDate', 'NA'),
            'sex': dicom_file.get('PatientSex', 'NA'),
            'date': dicom_file.get('StudyDate', 'NA'),
            'time_series': dicom_file.get('SeriesTime', 'NA'),
            'height': dicom_file.get('PatientSize', 'NA'),
            'weight': dicom_file.get('PatientWeight', 'NA'),
            'scanner_id': dicom_file.get('DeviceSerialNumber', 'NA'),
            'SeriesDescription': dicom_file.get('SeriesDescription', 'NA'),
            'StudyInstanceUID': dicom_file.get('StudyInstanceUID', 'NA'),
        }

    def extract_metadata(self) -> pd.DataFrame:
        """
        Iterate over `self.dicom_files` (a dict of file_path -> pydicom dataset),
        extract metadata for each file, convert column formats, and return a DataFrame.
        Prints progress as files are processed.
        """
        source = self.dicom_files or {}
        total = len(source)
        print(f"Beginning metadata extraction for {total} files.")

        file_paths, patient_ids, dob_list, sex_list, date_list, time_series_list = [], [], [], [], [], []
        height_list, weight_list, scanner_id_list, series_description_list, study_uid_list = [], [], [], [], []

        for idx, (file_path, dicom_file) in enumerate(source.items(), start=1):
            print(f"[{idx}/{total}] Extracting metadata from: {file_path}")
            meta = self._extract_metadata_from_dicom(dicom_file)

            # Warn if PatientID is missing (since strict behavior was requested)
            if meta['patient_ID'] in (None, 'NA', ''):
                print(f"  WARNING: missing PatientID for file `{file_path}` -> recorded as 'NA'")

            file_paths.append(file_path)
            patient_ids.append(meta['patient_ID'])
            dob_list.append(meta['dob'])
            sex_list.append(meta['sex'])
            date_list.append(meta['date'])
            time_series_list.append(meta['time_series'])
            height_list.append(meta['height'])
            weight_list.append(meta['weight'])
            scanner_id_list.append(meta['scanner_id'])
            series_description_list.append(meta['SeriesDescription'])
            study_uid_list.append(meta['StudyInstanceUID'])

        # Build DataFrame from collected lists
        df = pd.DataFrame({
            'FilePath': file_paths,
            'patient_ID': patient_ids,
            'dob': dob_list,
            'sex': sex_list,
            'date': date_list,
            'time_series': time_series_list,
            'height': height_list,
            'weight': weight_list,
            'scanner_id': scanner_id_list,
            'SeriesDescription': series_description_list,
            'StudyInstanceUID': study_uid_list,
        })

        print("Converting column formats (strings, dates, numerics)...")
        self.metadata = self._convert_column_formats(df)
        print("Metadata extraction complete.")
        return self.metadata

    def _convert_column_formats(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize data types:
        - Coerce key string columns to string and normalize 'None'/'nan' to 'NA'
        - Parse DICOM date fields (YYYYMMDD) into pandas timestamps
        - Convert height and weight to numeric where possible
        """
        # Columns expected to be strings
        str_cols = ['FilePath', 'patient_ID', 'scanner_id', 'SeriesDescription', 'sex', 'StudyInstanceUID', 'time_series']
        for col in str_cols:
            # Convert and replace common null representations
            df[col] = df[col].astype(str).replace({'None': 'NA', 'nan': 'NA'})

        # Parse DICOM-style dates (format YYYYMMDD); invalid parse -> NaT
        for col in ['dob', 'date']:
            print(f"  parsing date column: {col}")
            df[col] = pd.to_datetime(df[col], format='%Y%m%d', errors='coerce')

        # Normalize numeric measurements and report counts of successful conversions
        print("  normalizing numeric measurements: height, weight")
        df['height'] = df['height'].apply(self._normalize_numeric)
        df['weight'] = df['weight'].apply(self._normalize_numeric)

        # Show brief summary counts (non-null) to track conversions
        try:
            non_null_height = df['height'].notna().sum()
            non_null_weight = df['weight'].notna().sum()
            print(f"  height non-null count: {non_null_height}, weight non-null count: {non_null_weight}")
        except Exception:
            # Be silent if something unexpected happens here
            pass

        return df

    def save_metadata_to_csv(self, filename: str = "metadata_cmr_dicom.csv"):
        """
        Save the last extracted metadata DataFrame to CSV.
        """
        if self.metadata is None:
            print("No metadata available. Run `extract_metadata()` first.")
            return
        print(f"Saving metadata to CSV: `{filename}`")
        self.metadata.to_csv(filename, index=False)
        print(f"CSV saved: `{filename}`")