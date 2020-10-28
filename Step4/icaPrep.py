import os
import nibabel
import re
import numpy as np
import nipype
import glob
import argparse

def GetSubjectSession(fileName):
    """Returns the subject ID and session ID for a file named in the BIDS convention.  Returns in the order *Subject*, *Session*"""

    #Create the regex expression to match to
    patternSub = r'sub-(.+?)([(?=_)(?=\/)(?=\\)]|$)'
    patternSes = r'ses-(.+?)([(?=_)(?=\/)(?=\\)]|$)'

    #Match patterns to string
    matchSub = re.search(patternSub,fileName)
    matchSes = re.search(patternSes,fileName)

    SUB = matchSub.group(1)
    SES = matchSes.group(1)

    return SUB, SES


def Match2List(FileList,RepeatFile):
    """Matches a *Subject* and *Session* to a .csv list to find out which run to use.
    Returns the run number that from the file."""

    #Get the subject and session from a any one of the given files (irrelevant)
    SUB, SES = GetSubjectSession(FileList[0])

    RepeatList = np.genfromtxt(RepeatFile,delimiter=',',dtype='object')

    IndexSub = RepeatList[:,0] == SUB
    IndexSes = RepeatList[:,1] == SES
    IndexBoth = np.logical_and(IndexSub,IndexSes)

    RunNum = int(RepeatList[IndexBoth,2][0])

    return RunNum

def FindT1(SubSesDir,RepeatFile=None):
    """Finds the T1w anat file for a specified subject and session.
    If there are multiple files will return the run number specified 
    in the RepeatFile (TODO:explain how it is structured).  If no Repeat
    file is given defaults to return the last T1."""


    pattern = r'[^.].+T1w.+?_brain\.nii\.gz$'

    FileList = FindFiles(os.path.join(SubSesDir,'anat'),pattern)

    #Determine if there are no T1s found, 1 T1 found, or multiple T1s found

    if len(FileList) == 0:

        return 0

    elif len(FileList) == 1:

        return FileList[0]

    #Path if there are multiple files
    else:

        #Check if RepeatFile is empty
        #If so, return last T1 run
        if RepeatFile == None:
            return FileList[-1]

        else:

            #Get Run number from csv file
            RunNum = Match2List(FileList,RepeatFile)

            #put it into pattern string
            pattern = r'[^.].+?_run-%02d_T1w.+?_brain\.nii\.gz$'
            
            return [File for File in FileList if re.match(pattern % RunNum,File)][0]


#Function that finds BOLD file?

def FindBOLD(SubSesDir, RepeatFile=None):


    #Is the '_STD' necessary?  Probably
    pattern = r'[^.].+?task-resting.+?bold_STD\.nii\.gz$'

    FileList = FindFiles(os.path.join(SubSesDir,'func'),pattern)

    if len(FileList) == 0:
        return 0
    elif len(FileList) == 1:
        return FileList[0]

    #Path if multiple files are found
    else:

        #Automatic functionality if no list given
        #Retursn the longest BOLD file
        if RepeatFile == None:

            times = []
            for bold in FileList:
                data = nibabel.load(os.path.join(SubSesDir,'func',bold))
                times.append(data.header['dim'][4])

            #Determine longest BOLD file
            MaxID = times.index(max(times))

            return FileList[MaxID]

        #What to do if RepeatFile list is specified
        else:
            
            RunNum = Match2List(FileList,RepeatFile)

            #put it into pattern string
            pattern = r'[^.].+?_task-resting.+?_run-%02d.+?_bold_STD\.nii\.gz$'
            
            return [File for File in FileList if re.match(pattern % RunNum,File)][0]            

def FindFiles(Dir,pattern):
    """Function that returns a list of files that match a regex expression
    in a given directory"""
    
    Files = os.listdir(Dir)

    Indices = [index for index,name in enumerate(Files) if re.match(pattern,name)]

    return [Files[index] for index in Indices]

def MakeFSF(BOLD,T1,FSF_TEMPLATE,ROOT):
    """Function that takes a RS-Bold file, a T1 file, and a .fsf template to make
    the subject specific .fsf template.  .fsf template must contain 'xxxOUTPUxxx',
    'xxxTRxxx', 'xxxNVOLxxx', 'xxxNVOXELxxx', 'xxxBOLDxxx', 'xxxT1xxx'."""

    #Load FSF_TEMPLATE as data
    with open(FSF_TEMPLATE) as data:
        template = data.read()


    BOLD_nii = nibabel.load(os.path.join(ROOT,'func',BOLD))
    TR = BOLD_nii.header['pixdim'][4]
    NVOLS = BOLD_nii.header['dim'][4]
    #Calculate total number of voxels in the 
    NVOX = int(BOLD_nii.header['dim'][1]) * int(BOLD_nii.header['dim'][2]) * int(BOLD_nii.header['dim'][3]) * int(NVOLS)

    #Make file paths
    OUTPUT = os.path.join(ROOT,'single-session')
    #[0:-7] removes the '.nii.gz' from the file
    BOLD_PATH = os.path.join(ROOT,'func',BOLD[0:-7])
    T1_PATH = os.path.join(ROOT,'anat',T1[0:-7])
    
    #Create dictionary of replacements, keys are in the template file, values are the replacements
    replace = {'xxxOUTPUTxxx': OUTPUT, 'xxxTRxxx': str(TR), 'xxxNVOLxxx': str(NVOLS),
               'xxxNVOXELxxx': str(NVOX), 'xxxBOLDxxx': BOLD_PATH, 'xxxT1xxx': T1_PATH}
    #Gets rid of escape characters?
    replace = dict((re.escape(k), v) for k, v in replace.items())
    pattern = re.compile('|'.join(replace.keys()))
    #Makes the new data to be saved
    FSF_NEW = pattern.sub(lambda m: replace[re.escape(m.group(0))], template)


    #~~~~~~~~~~~~~~~#
    #Make the actual .fsf file
    #Makes the subject specific name, and saves the data to the named file

    sub,ses = GetSubjectSession(BOLD)
    FSF_Name = r'singleSession_ICA_sub-%s_ses-%s.fsf'

    FSF_FILE = os.path.join(ROOT, FSF_Name % (sub, ses))

    with open(FSF_FILE, 'w') as file:
        file.write(FSF_NEW)

    #Return file path at the end?
    

def GetSubjectList(ROOT):
    """Returns a list of all subject/session directories when given a root directory.  Root is the root location of the BIDS folders."""
    TemplatePath = os.path.join(ROOT,'derivative','sub-*','ses-*')

    return glob.glob(TemplatePath)


def Main(ROOT,FSF_Loc,T1Repeat=None,BOLDRepeat=None):
    """Main function that is called if this script is called from the command line.  Finds the list of people in the 'derivative'
    folder of the BIDS hierarchy, finds T1, and BOLD [and does error handling] and makes .fsf from a template file."""
    SubjectSession_List = GetSubjectList(ROOT)

    #Loop through each subject, find T1 and BOLD, make FSF
    for People in SubjectSession_List:

        SUB, SES = GetSubjectSession(People)
        
        T1 = FindT1(People,T1Repeat)

        if T1 == 0:
            ##TODO: Error handling to log file
            print("No T1 found for this participant")

        #What to do with the T1file
        else:
            BOLD = FindBOLD(People,BOLDRepeat)

            if BOLD == 0:
                print("No BOLD he-yah!")

            else:

                #Function to run if everything goes well
                MakeFSF(BOLD,T1,FSF_Loc,People)

                
if __name__ == "__main__":

    #Take input arguments
    parser = argparse.ArgumentParser(description='Script that makes the .FSF files for feat/melodic processing.')
    parser.add_argument('root', help='Root directory of the BIDS structure.')
    parser.add_argument('--T1Repeat','-t', required=False,
                        help='.csv file with 3 columns [Participant,Session,Run] info which specifies which T1 image to use. Default behaviour is to use the last T1.')
    parser.add_argument('--BOLDRepeat','-b', required=False,
                        help='.csv file with 3 columns [Participant,Session,Run] info which specifies which BOLD image to use.  Default behaviour is to use the longest BOLD.')
    parser.add_argument('--fsf','-f', required=True,
                        help='.fsf Template file for making each participants file.  See MakeFSF() for specifics of template.')

    args = parser.parse_args()

    FSF_Loc = args.fsf
    ROOT = args.root

    if args.T1Repeat:
        T1Repeat = args.T1Repeat
    else:
        T1Repeat = None

    if args.BOLDRepeat:
        BOLDRepeat = args.BOLDRepeat
    else:
        BOLDRepeat = None

    Main(ROOT,FSF_Loc,T1Repeat,BOLDRepeat)

    #Add code to make list of .fsf files??
