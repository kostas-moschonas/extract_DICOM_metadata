"""
Module for extracting metadata from DICOM files.

This module provides a class `MetadataExtraction` that can find DICOM files based on their Series Description,
extract metadata from these files, and save the metadata to a CSV file.

Author: Kostas Moschonas
Date: 23/09/2025
"""
import os
import zipfile
import tempfile
import pydicom
import pandas as pd
from typing import Dict

class MetadataExtraction:
    """
    A class to extract metadata from DICOM files in a directory structure or from a dictionary of DICOM files.

    This class provides methods to find DICOM files based on their Series Description,
    extract metadata from these files, and save the metadata to a CSV file.

    Attributes:
        dicom_files (Dict[str, pydicom.dataset.FileDataset]): A dictionary where keys are file paths and values are DICOM files.
        root_directory (str): The root directory to search for DICOM files.
        metadata (pd.DataFrame): A DataFrame containing the extracted metadata.

    Methods:
        find_dicom_by_series_description(folder_path: str, search_string: str):
            Finds a DICOM file in the specified folder whose Series Description contains the given search string.

        find_dicom_in_zip_by_series_description(zip_path: str, search_string: str):
            Finds a DICOM file in a zipped folder whose Series Description contains the given search string.

        find_dicom_in_zip_folder_by_series_description(zip_folder_path: str, search_string: str):
            Finds DICOM files in each zipped folder within the specified folder whose Series Description contains the given search string.

        extract_metadata() -> pd.DataFrame:
            Extracts metadata from the DICOM files and returns it as a pandas DataFrame.

        save_metadata_to_csv(filename: str = "metadata_cmr_dicom.csv"):
            Saves the extracted metadata to a CSV file.
    """

    def __init__(self, dicom_files: Dict[str, pydicom.dataset.FileDataset] = None, root_directory: str = None):
        self.dicom_files = dicom_files
        self.root_directory = root_directory
        self.metadata = None

    def find_dicom_by_series_description(self, folder_path: str, search_string: str):
        """
        Finds a DICOM file **in the specified folder** whose Series Description contains the given search string.
        """
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                dicom_path = os.path.join(root, file)
                try:
                    dicom_file = pydicom.dcmread(dicom_path)
                    series_description = dicom_file.get('SeriesDescription', 'NA')
                    if search_string.lower() in series_description.lower():
                        print(f"Found DICOM file with SeriesDescription containing '{search_string}': {dicom_path}")
                        return dicom_file
                except pydicom.errors.InvalidDicomError as e:
                    print(f"Error reading DICOM file {dicom_path}: {e}")
        print(f"No DICOM file with SeriesDescription containing '{search_string}' found in folder {folder_path}")
        return None

    def find_dicom_in_zip_by_series_description(self, zip_path: str, search_string: str):
        """
        Finds a DICOM file in **a zipped folder** whose Series Description contains the given search string.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                return self.find_dicom_by_series_description(temp_dir, search_string)

    def find_dicom_in_zip_folder_by_series_description(self, zip_folder_path: str, search_string: str):
        """
        Finds DICOM files in **each zipped folder within the specified folder** whose Series Description contains the given search string.
        """
        dicom_files = {}
        for root, dirs, files in os.walk(zip_folder_path):
            for file in files:
                if file.endswith(".zip"):
                    zip_path = os.path.join(root, file)
                    dicom_file = self.find_dicom_in_zip_by_series_description(zip_path, search_string)
                    if dicom_file:
                        dicom_files[zip_path] = dicom_file
        if not dicom_files:
            print(f"No DICOM file with Series Description containing '{search_string}' found in any zip file in folder {zip_folder_path}")
        return dicom_files

    def find_dicom_in_folder_by_series_description(self, folder_path: str, filter_function=None):
        """
        Finds DICOM files in the specified folder whose Series Description matches the criteria
        defined by the provided filter_function. Stops after finding one correct DICOM file
        for each unique pair of PatientID and StudyDate.

        Args:
            folder_path (str): The path to the folder to search for DICOM files.
            filter_function (callable, optional): A function that takes a Series Description as input
                and returns True if the file should be included, False otherwise.

        Returns:
            dict: A dictionary where keys are file paths and values are DICOM files.
        """
        dicom_files = {}
        processed_study_keys = set()  # Track (PatientID, StudyDate) pairs

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    dicom_file = pydicom.dcmread(file_path)
                    series_description = dicom_file.get('SeriesDescription', 'NA')
                    if filter_function and not filter_function(series_description):
                        continue
                    patient_id = dicom_file.get('PatientID', 'NA')
                    study_date = dicom_file.get('StudyDate', 'NA')
                    study_key = (patient_id, study_date)
                    if study_key not in processed_study_keys:
                        print(f"Found DICOM file with SeriesDescription matching filter: {file_path}")
                        dicom_files[file_path] = dicom_file
                        processed_study_keys.add(study_key)
                except pydicom.errors.InvalidDicomError as e:
                    print(f"Error reading DICOM file {file_path}: {e}")
                    continue

        if not dicom_files:
            print(f"No DICOM files matching the filter found in folder {folder_path}")
        return dicom_files

    # def find_dicom_in_folder_by_series_description(self, folder_path: str, search_string: str):
    #     """
    #     Finds DICOM files in each folder (zipped or not) within the specified folder
    #     whose Series Description contains the given search string. Stops after finding
    #     one correct DICOM file for each study (based on PatientID).
    #     """
    #     dicom_files = {}
    #     processed_patient_ids = set()
    #
    #     for root, dirs, files in os.walk(folder_path):
    #         for file in files:
    #             file_path = os.path.join(root, file)
    #
    #             # Check if the file is a zip file
    #             if file.endswith(".zip"):
    #                 dicom_file = self.find_dicom_in_zip_by_series_description(file_path, search_string)
    #             else:
    #                 # Process non-zipped files directly
    #                 try:
    #                     dicom_file = pydicom.dcmread(file_path)
    #                     series_description = dicom_file.get('SeriesDescription', 'NA')
    #                     if search_string.lower() in series_description.lower():
    #                         patient_id = dicom_file.get('PatientID', 'NA')
    #                         if patient_id not in processed_patient_ids:
    #                             print(f"Found DICOM file with SeriesDescription containing '{search_string}': {file_path}")
    #                             dicom_files[file_path] = dicom_file
    #                             processed_patient_ids.add(patient_id)
    #                             continue
    #                 except pydicom.errors.InvalidDicomError as e:
    #                     print(f"Error reading DICOM file {file_path}: {e}")
    #                     continue


    def _extract_metadata_from_dicom(self, dicom_file: pydicom.dataset.FileDataset) -> Dict:
        return {
            'mrn': dicom_file.get('PatientID', 'NA'),
            'dob': dicom_file.get('PatientBirthDate', 'NA'),
            'date': dicom_file.get('StudyDate', 'NA'),
            'time_series': dicom_file.get('SeriesTime', 'NA'),
            'scanner_id': dicom_file.get('DeviceSerialNumber', 'NA'),
            'SeriesDescription': dicom_file.get('SeriesDescription', 'NA'),
        }

    def extract_metadata(self) -> pd.DataFrame:
        """
        Extracts metadata from the DICOM files and returns it as a pandas DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing the extracted metadata with columns:
                - FilePath: The path to the DICOM file.
                - mrn: The medical record number of the patient.
                - dob: The date of birth of the patient.
                - date: The study date.
                - time_series: The study time_series.
                - scanner_id: The ID of the scanner used.
                - SeriesDescription: The series description of the DICOM file.
        """
        file_paths, mrn, dob, date, time_series = [], [], [], [], []
        scanner_id, series_description = [], []

        for file_path, dicom_file in self.dicom_files.items():
            dicom_metadata = self._extract_metadata_from_dicom(dicom_file)
            file_paths.append(file_path)
            mrn.append(dicom_metadata['mrn'])
            dob.append(dicom_metadata['dob'])
            date.append(dicom_metadata['date'])
            time_series.append(dicom_metadata['time_series'])
            scanner_id.append(dicom_metadata['scanner_id'])
            series_description.append(dicom_metadata['SeriesDescription'])

        df = pd.DataFrame({
            'FilePath': file_paths,
            'mrn': mrn, 'dob': dob, 'date': date,
            'time_series': time_series, 'scanner_id': scanner_id,
            'SeriesDescription': series_description,
        })
        self.metadata = self._convert_column_formats(df)
        return self.metadata

    def _convert_column_formats(self, df: pd.DataFrame) -> pd.DataFrame:
        str_cols = ['FilePath', 'mrn', 'scanner_id', 'SeriesDescription']
        df[str_cols] = df[str_cols].astype(str)
        date_cols = ['dob', 'date']
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], format='%Y%m%d', errors='coerce')
        return df

    def save_metadata_to_csv(self, filename: str = "metadata_cmr_dicom.csv"):
        if self.metadata is None:
            print("No metadata extracted. Run extract_metadata() first.")
            return
        self.metadata.to_csv(filename, index=False)
        print(f"CSV saved: {filename}")