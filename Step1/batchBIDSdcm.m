%Code to convert the second batch of ACAP participants (copied off of the
%drive first)

SOURCE_DIR = '/Users/alexbarton/Documents/STUDIES/ACAP/dicom';
TAR_DIR = '/Users/alexbarton/Documents/STUDIES/ACAP';

PAR_CAL = 'ACAP1';
PAR_EDM = 'ACAP2';
PAR_MTL = 'ACAP3';
PAR_OTT = 'ACAP4';
PAR_VAN = 'ACAP5';

CAL_MTL_VAN_LIST = {'(.*)Resting_State(.*)', 'func', 'sub-%s_ses-%s_task-resting_bold', 'sub-%s_ses-%s_task-resting_run-%02d_bold';...
    '(.*)_FSPGR_(.*)', 'anat', 'sub-%s_ses-%s_T1w', 'sub-%s_ses-%s_run-%02d_T1w'};

%New MTL list for changes in structural names
%Right now I simply repeat
MTL_LIST = {'(.*)ep2d(.*)Resting_State(.*)', 'func', 'sub-%s_ses-%s_task-resting_bold', 'sub-%s_ses-%s_task-resting_run-%02d_bold';...
    '(.*)_mprage_(.*)iso0.8$', 'anat', 'sub-%s_ses-%s_T1w', 'sub-%s_ses-%s_run-%02d_T1w'};

EDM_LIST = {'(.*)bold_resting_state(.*)', 'func', 'sub-%s_ses-%s_task-resting_bold', 'sub-%s_ses-%s_task-resting_run-%02d_bold';...
    '(.*)_mprage_(.*)iso0.8$', 'anat', 'sub-%s_ses-%s_T1w', 'sub-%s_ses-%s_run-%02d_T1w'};

OTT_LIST = {'(.*)bold(.*)', 'func', 'sub-%s_ses-%s_task-resting_bold', 'sub-%s_ses-%s_task-resting_run-%02d_bold';...
    '(.*)_mprage_(.*)iso$', 'anat', 'sub-%s_ses-%s_T1w', 'sub-%s_ses-%s_run-%02d_T1w'};

%Calgary convert
BIDSdcm2nii(SOURCE_DIR,TAR_DIR,CAL_MTL_VAN_LIST,PAR_CAL,'CAL',1);

%Edmonton convert (both)
BIDSdcm2nii(SOURCE_DIR,TAR_DIR,EDM_LIST,PAR_EDM,'EDM',1);

%Montreal convert
BIDSdcm2nii(SOURCE_DIR,TAR_DIR,CAL_MTL_VAN_LIST,PAR_MTL,'MON',1);

%Ottawa convert (both)
BIDSdcm2nii(SOURCE_DIR,TAR_DIR,OTT_LIST,PAR_OTT,'OTT',1);

%Vancouver convert 
BIDSdcm2nii(SOURCE_DIR,TAR_DIR,CAL_MTL_VAN_LIST,PAR_VAN,'VAN',1);