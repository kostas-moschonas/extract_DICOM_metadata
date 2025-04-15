import pydicom

dcm = pydicom.dcmread("input/MHCM07_20240723/series0001-Body/img0001--2.dcm")

dcm_cvi = pydicom.dcmread("input/fromCVI.dcm")

dcm_pacs = pydicom.dcmread("input/fromPACS.dcm")