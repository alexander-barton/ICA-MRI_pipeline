import os, sys
#import multiprocessing
import argparse
import shutil
#import subprocess
import csv
#Necessary for the wrapper_func
#import itertools

#21-12-2017 ADDED  a workaround from StackOverflow
#Apparently the pool.map function can only take 1 argument

def MakeReorientList(Filefull, outputDir):

    #Do things that using FSL libraries/optiBET.sh
    #Need to call the system
    Rootdir,filename = os.path.split(Filefull)
    Rootdir,MOD = os.path.split(Rootdir)
    Rootdir,SES = os.path.split(Rootdir)
    Rootdir,SUB = os.path.split(Rootdir)

    
    filebase = filename[0:-7]

    #Check for and make destination directory (following BIDS format)
    Destdir = os.path.join(outputDir,SUB,SES,MOD)
    if not os.path.isdir(Destdir):
        os.makedirs(Destdir)

    
    #Copy nifti file and .json
    shutil.copy2(Filefull,Destdir)
    #Commented out for thing with no .json
    #shutil.copy2(os.path.join(Rootdir,SUB,SES,MOD,filebase + '.json'), Destdir)

    #Make string with output name of INPUTNAME + '_STD.nii.gz'
    reorientName = filebase + '_STD.nii.gz'
    finalDestination = os.path.join(Destdir,reorientName)

    #Run fslreorient2std
    #subprocess.Popen(['fslreorient2std', os.path.join(Destdir,T1file), finalDestination])

    #Return location of reorient name	
    return finalDestination

#Function that runs optiBET
#Not being used
#def extractT1(FileName, optiBET):

 #   subprocess.Popen(['bash', optiBET, '-i', FileName])



#This is a version of the StackOverflow code 
#def wrapper_funcT1(inputs):
#    return reorientExtractT1(*inputs)

#Function that removes files from list that have already been performed
def CleanFileList(Destlist,Sourcelist):

    cleanDest = []
    cleanSource = []
    
    for i in range(0,len(Destlist) - 1):

        if not os.path.isfile(Destlist[i]):

            cleanDest.append(Destlist[i])
            cleanSource.append(Sourcelist[i])

    return cleanDest, cleanSource

#Main function
if __name__ == '__main__':

    #Do things that are important
    #Also use input arguments using argparse library (see reference manual)

    parser = argparse.ArgumentParser(description='Reorient and optiBET anatomical data in BIDS format')
    parser.add_argument('-i', '--inputDir', required=True,
                        help='Directory where \'source\' folder is located')

    #automatically parses the arguments
    args = parser.parse_args()
    #TODO: add checks for inputs
    #ASWELLAS TRY/CATCH BLOCKS

    #First find all T1 files
    T1list = []
    BOLDlist = []

    #Loop through directory tree and find files of interest
    for dirName, subdirName, fileList in os.walk(os.path.join(args.inputDir,'source')):
        for names in fileList:
            if 'bold.nii.gz' in names:

                BOLDlist.append(os.path.join(dirName,names))
                

            if 'T1w.nii.gz' in names:
                T1list.append(os.path.join(dirName,names))
                

    #Make list of jobs and multi-process them
    #pool = multiprocessing.Pool(args.numProcess)

    T1dest = []
    BOLDdest = []
    for i in range(0,len(T1list) - 1):
         T1dest.append(MakeReorientList(T1list[i], os.path.join(args.inputDir,'derivative')))

    for i in range(0,len(BOLDlist) - 1):
        BOLDdest.append(MakeReorientList(BOLDlist[i],os.path.join(args.inputDir,'derivative')))
    #results = [(reorientT1([j])) for j in jobs]

    #cleaned lists without names that have already been done
    T1destC, T1listC = CleanFileList(T1dest,T1list)
    BOLDdestC, BOLDlistC = CleanFileList(BOLDdest,BOLDlist)
    
    T1f = open(os.path.join(args.inputDir,'T1ExtractInput.txt'),'a+')
    T1f2 = open(os.path.join(args.inputDir,'T1ReorientInput.txt'),'a+')

    BOLDf = open(os.path.join(args.inputDir,'BOLDExtractInput.txt'),'a+')
    BOLDf2 = open(os.path.join(args.inputDir,'BOLDReorientInput.txt'),'a+')

    #write to all the files
    for T1 in T1destC:
    	T1f.write("%s\n" % T1)
        #print result.get()
    T1f.close()

    for T1 in T1listC:
        T1f2.write("%s\n" % T1)
    T1f2.close()

    for BOLD in BOLDdestC:
        BOLDf.write("%s\n" % BOLD)
    BOLDf.close()

    for BOLD in BOLDlistC:
        BOLDf2.write("%s\n" % BOLD)
    BOLDf2.close()
    	   
    #pool.close()
    #pool.join()
    

