# DICOM Metadata Extraction

This project provides a Python module for extracting metadata from DICOM files. It includes functionality to search for DICOM files based on their `SeriesDescription`, extract and save relevant metadata. 

## Features

- **Search DICOM Files**: Locate DICOM files in directories or zipped folders based on a specific `SeriesDescription`.
- **Extract Metadata**: Retrieve metadata such as `PatientID`, `PatientBirthDate`, `StudyDate`, `SeriesTime`, `DeviceSerialNumber`, and `SeriesDescription`.
- **Save to CSV**: Save the extracted metadata to a CSV file.

## Requirements

- Python 3.7+
- Required Python packages:
  - `pydicom`
  - `pandas`

Install the dependencies using pip:

```bash
pip install pydicom pandas
```

## Author
Kostas Moschonas
02/04/2025