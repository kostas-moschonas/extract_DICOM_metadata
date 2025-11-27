import os
import pydicom
from pydicom.dataset import Dataset

def anonymize_dicom_file(input_path, output_path):
    """
    Loads a DICOM file, anonymizes it, and saves it to a new location.

    :param input_path: Path to the original DICOM file.
    :param output_path: Path to save the anonymized DICOM file.
    """
    try:
        # Load the DICOM file
        ds = pydicom.dcmread(input_path)

        # List of tags to anonymize by blanking the value
        tags_to_anonymize = [
            'PatientName',
            'PatientID',
            'PatientBirthDate',
            'PatientSex',
            'PatientAge',
            'PatientAddress',
            'PatientTelephoneNumbers',
            'ReferringPhysicianName',
            'InstitutionName',
            'OperatorsName',
            'StudyID',
            'AccessionNumber',
            'StudyInstanceUID', # Replace with a new one if needed for consistency
            'SeriesInstanceUID',# Replace with a new one if needed for consistency
            'SOPInstanceUID' # Replace with a new one if needed for consistency
        ]

        for tag_name in tags_to_anonymize:
            if tag_name in ds:
                # Get the tag object from the name
                tag = ds.data_element(tag_name)
                if tag:
                    # Blank the value
                    tag.value = ''

        # Remove private tags
        ds.remove_private_tags()

        # Generate new UIDs to break link to original study
        ds.StudyInstanceUID = pydicom.uid.generate_uid()
        ds.SeriesInstanceUID = pydicom.uid.generate_uid()
        ds.SOPInstanceUID = pydicom.uid.generate_uid()

        # Save the anonymized dataset
        ds.save_as(output_path)

    except Exception as e:
        print(f"Could not process file {input_path}: {e}")


def process_directory(input_dir, output_dir):
    """
    Anonymizes all DICOM files in a directory.

    :param input_dir: Directory containing original DICOM files.
    :param output_dir: Directory to save anonymized files.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        if os.path.isfile(input_path):
            print(f"Anonymizing {input_path} -> {output_path}")
            anonymize_dicom_file(input_path, output_path)

if __name__ == '__main__':
    # --- Configuration ---
    # Create dummy directories and a file for demonstration
    if not os.path.exists('dicom_input'):
        os.makedirs('dicom_input')

    # Create a dummy DICOM file for testing
    file_meta = pydicom.dataset.FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
    file_meta.MediaStorageSOPInstanceUID = "1.2.3"
    file_meta.ImplementationClassUID = "1.2.3.4"

    ds = Dataset()
    ds.file_meta = file_meta
    ds.PatientName = "Test^Patient"
    ds.PatientID = "123456"
    ds.PatientBirthDate = "20000101"
    ds.is_little_endian = True
    ds.is_implicit_VR = True
    ds.save_as('dicom_input/test_dicom.dcm', write_like_original=False)
    # --- End of dummy file creation ---

    input_directory = 'dicom_input'
    output_directory = 'dicom_output_anonymized'

    process_directory(input_directory, output_directory)
    print("\nAnonymization complete.")