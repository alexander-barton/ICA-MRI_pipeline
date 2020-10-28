import os
import re
import glob
import argparse
import shutil

def GetSubjectSession(fileName):

    patternSub = r'sub-(.+?)[(?=_)(?=\/)(?=\\)]'
    patternSes = r'ses-(.+?)[(?=_)(?=\/)(?=\\)]'

    matchSub = re.search(patternSub,fileName)
    matchSes = re.search(patternSes,fileName)

    SUB = matchSub.group(1)
    SES = matchSes.group(1)

    return SUB, SES

def GetBOLDList(ROOT):

    WildcardPath = os.path.join(ROOT,'raw','sub*','ses*','func','*bold.nii.gz')
    return glob.glob(WildcardPath)

def GetT1List(ROOT):

    WildcardPath = os.path.join(ROOT,'raw','sub*','ses*','anat','*T1w.nii.gz')
    return glob.glob(WildcardPath)

def MakeReorientList(FullFile, ROOT, Modality):

    RootDir, filename = os.path.split(FullFile)

    sub, ses = GetSubjectSession(FullFile)
    
    filebase = filename[0:-7]

    DestDir = os.path.join(ROOT,'derivative','sub-' + sub, 'ses-' + ses, Modality)
    if not os.path.isdir(DestDir):
        os.makedirs(DestDir)

    #Copy to new dir
    shutil.copy2(FullFile,DestDir)

    #Copy .json?

    ReorientName = filebase + '_STD.nii.gz'

    ReorientPath = os.path.join(DestDir,ReorientName)
    InputPath = os.path.join(DestDir,filename)

    return InputPath, ReorientPath

def RemoveOldFiles(InputList,ReorientList):

    CleanedInput = []
    CleanedReorient = []

    for i in range(0,len(InputList)):

        if not os.path.isfile(ReorientList[i]):

            CleanedInput.append(InputList[i])
            CleanedReorient.append(ReorientList[i])

    return CleanedInput, CleanedReorient

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Make a list of Inputs and Outputs for fslreorient2std and BIDS.  Also copies files to \'derivative\' folder.')
    parser.add_argument('-i','--inputDir',required=True,help='Root Directory of the BIDS folders.')

    args = parser.parse_args()
    ROOT = args.inputDir

    BOLDs = GetBOLDList(ROOT)
    T1s = GetT1List(ROOT)

    T1input = []
    BOLDinput = []

    T1Reorient = []
    BOLDReorient = []
    for path in BOLDs:
        Input, Reorient = MakeReorientList(path,ROOT,'func')
        BOLDinput.append(Input)
        BOLDReorient.append(Reorient)

    for path in T1s:
        Input, Reorient = MakeReorientList(path,ROOT,'anat')
        T1input.append(Input)
        T1Reorient.append(Reorient)

    T1inputC, T1ReorientC = RemoveOldFiles(T1input,T1Reorient)
    BOLDinputC, BOLDReorientC = RemoveOldFiles(BOLDinput,BOLDReorient)

    T1f = open(os.path.join(args.inputDir,'T1ExtractInput.txt'),'a+')
    T1f2 = open(os.path.join(args.inputDir,'T1ReorientInput.txt'),'a+')

    BOLDf = open(os.path.join(args.inputDir,'BOLDExtractInput.txt'),'a+')
    BOLDf2 = open(os.path.join(args.inputDir,'BOLDReorientInput.txt'),'a+')

    #write to all the files
    for T1 in T1ReorientC:
    	T1f.write("%s\n" % T1)
        #print result.get()
    T1f.close()

    for T1 in T1inputC:
        T1f2.write("%s\n" % T1)
    T1f2.close()

    for BOLD in BOLDReorientC:
        BOLDf.write("%s\n" % BOLD)
    BOLDf.close()

    for BOLD in BOLDinputC:
        BOLDf2.write("%s\n" % BOLD)
    BOLDf2.close()

    
