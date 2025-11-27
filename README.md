# DICOM Metadata Extraction

A small Python module to locate DICOM files (folders or zip archives), extract metadata, and save it to CSV. The extractor now strictly uses DICOM `PatientID` as `patient_ID` (no fallback to other tags) and includes additional patient and study fields.

## Features

- Search for DICOM files by `SeriesDescription` in folders or inside `.zip` archives.
- Extract metadata including:
  - `patient_ID` (strictly DICOM `PatientID`)
  - `dob` (PatientBirthDate)
  - `sex` (PatientSex)
  - `date` (StudyDate)
  - `time_series` (SeriesTime)
  - `height` (PatientSize)
  - `weight` (PatientWeight)
  - `scanner_id` (DeviceSerialNumber)
  - `SeriesDescription`
  - `StudyInstanceUID`
- Progress printouts for searches, file reads, extraction steps, and CSV save.
- Type conversions: DICOM dates parsed to timestamps; height/weight coerced to numeric where possible.

## CSV output columns

The saved CSV (default: `metadata_cmr_dicom.csv`) contains these columns:
- `FilePath`
- `patient_ID`
- `dob`
- `sex`
- `date`
- `time_series`
- `height`
- `weight`
- `scanner_id`
- `SeriesDescription`
- `StudyInstanceUID`

## Requirements

- Python 3.7+
- Required Python packages:
  - `pydicom`
  - `pandas`

Install dependencies:

    pip install pydicom pandas

## Quick usage

1. Use the finder to collect representative DICOM files (one per PatientID+StudyDate):
```
# example usage (indentation used for code block)
    from extract_dicom_metadata import MetadataExtraction
    
    # find DICOMs matching a filter in a folder
    finder = MetadataExtraction()
    dicom_map = finder.find_dicom_in_folder_by_series_description(
        r"C:\path\to\dicom_folder",
        lambda s: "stress" in s.lower()
    )
````

2. Extract metadata and save to CSV:
```
    extractor = MetadataExtraction(dicom_files=dicom_map)
    df = extractor.extract_metadata()      # prints progress
    extractor.save_metadata_to_csv()       # saves to `metadata_cmr_dicom.csv
```
    

## Notes

- `patient_ID` is set strictly from DICOM `PatientID`. If missing, the value recorded is `'NA'`.
- If other scripts expect a column named `mrn`, rename the column before further processing:

    df.rename(columns={ 'patient_ID': 'mrn' }, inplace=True)

- The extractor prints progress and warnings (e.g., missing `PatientID`) to help trace execution.

## Author

Kostas Moschonas  
Updated: 27-11-2025