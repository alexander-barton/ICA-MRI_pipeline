%% Scrip to convert raw DICOMs to BIDS format 
%% Source dir: location where dicoms are stored
%% Source name: name of source file/directory
%% Target dir: location where you will be saving your BIDS formatted NifTi files
%% Target name: name of new target file
%% Par name: naming convention of participants that is common between them

%TODO: CHANGE HOW SOURCE_NAME IS STRUCTURED
%CURRENTLY JUST A CELL STRING ARRAY, BUT PERHAPS BETTER IF IT'S A TABLE

%%TODO: CONVERT ALL INSTANCES OF STRCAT TO FULLFILE
%%AS FULLFILE WILL WORK REGARDLESS OF OS

%%TODO: CHANGE SO THAT THE INPUT NAMES ARE IN WILDCARD FORMAT
%%AND NOT THAT THE FUNCTION ADDS THE WILDCARDS ITSELF

function BIDSdcm2nii(SOURCE_DIR,TAR_DIR,SOURCE_NAME,PAR_NAME,LOG_NAME,NUMS)

    %Fill these in with your matching tuples
    %Make sure they are the same length
    %BETTER AS INPUT
    %SOURCE_NAME = {};
    %TAR_NAME = {};
    
    
    logDir = fullfile(TAR_DIR,'logs/conversion');
    makedir(logDir);
    
    logSUCCESS = fullfile(logDir,sprintf('%s_SUCCESS_LOG.txt',LOG_NAME));
    logERROR = fullfile(logDir,sprintf('%s_ERROR_LOG.txt',LOG_NAME));
    logREP = fullfile(logDir,sprintf('%s_REPEAT_LOG.txt',LOG_NAME));
    
    fidSUCCESS = fopen(logSUCCESS,'a');
    fidERROR = fopen(logERROR,'a');
    fidREP = fopen(logREP,'a');
    
    logtempS = ['~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'...
        '~~~~~~~~~~~~~~~~~~~~~STARTED %s~~~~~~~~~~~~~~~~~~~~~\n'...
        '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n'];
    logtempF = ['\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'...
        '~~~~~~~~~~~~~~~~~~~~COMPLETED %s~~~~~~~~~~~~~~~~~~~~\n'...
        '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n'];
    
    logstart = sprintf(logtempS,datestr(datetime('now')));
    
    
    fprintf(fidSUCCESS,logstart);
    fprintf(fidERROR,logstart);
    fprintf(fidREP,logstart);
    
    %Make directories for the main files
    %comment out if you do not want
    
    tarPath = fullfile(TAR_DIR,'raw');
    makedir(tarPath);

    %Get listing of participants
    dirList = dir(fullfile(SOURCE_DIR,strcat(PAR_NAME,'*')));
    dirList = dirList([dirList.isdir]);

    splitList = cell(length(dirList),2);
    %Filter dirList into a list of unique participant names
    for n = 1 : length(dirList)
        
        
        %'splitList' is the list of Participant names and longitudinal
        %timepoints split into two columns
        splitList(n,:) = strsplit(dirList(n).name,'_');

        %NOTE: thought about saving the timepoints here (instead of
        %repeated later, but seems to add more heartbreak than it is worth
        
        
    end
    
    parList = unique(splitList(:,1));
    
    
    %For loop to run through all the participants
    for n = 1 : length(parList)
       
        %PARTICIPANT NUM/NAME
        PARTICIPANT = parList(n);
        PARTICIPANT = char(PARTICIPANT);
        
        %Make Participant Directory
        parPath = fullfile(tarPath,strcat('sub-',PARTICIPANT));
        makedir(parPath);
        
        %LONGITUDINAL TIMPOINT
        LONG_TIMES = find(strcmp(splitList,PARTICIPANT));
        
        for m = 1 : length(LONG_TIMES)
           
            TIMEPOINT = splitList(LONG_TIMES(m),2);
            TIMEPOINT = char(TIMEPOINT);
            
            %Make session Directory
            sesPath = fullfile(parPath,strcat('ses-',TIMEPOINT));
            makedir(sesPath)
            
            %Make directories for each type of scan in the session
            %directory
            anatPath = fullfile(sesPath,'anat');
            makedir(anatPath);
            funcPath = fullfile(sesPath,'func');
            makedir(funcPath);
            dwiPath = fullfile(sesPath,'dwi');
            makedir(dwiPath);
            
            %start file conversion
            
            %Loop through the different measures being used
            for k = 1 : size(SOURCE_NAME,1)
               
                sourceForm = SOURCE_NAME(k,1);
                sourceForm = char(sourceForm);
                destFolder = SOURCE_NAME(k,2);
               
                
                 try

                    source = fullfile(SOURCE_DIR,strcat(PARTICIPANT,'_',TIMEPOINT));
                    source = char(source);
                    dest = fullfile(sesPath,destFolder);
                    dest = char(dest);

                    %Get the list of all directories in the Participant directory
                    sourceList = dir(source);
                    sourceList = sourceList([sourceList.isdir]);
                    
                    %Get the directories only matching the regex
                    allDir = {sourceList.name};
                    
                    %Switch this line w/ the commented one if there are no
                    %numbers preceding the name (i.e. not on Marina's
                    %server)
                    
                    if NUMS == 1
                        
                        indices = ~cellfun(@isempty,regexpi(allDir,strcat('^[0-9]{1,2}-',sourceForm)));
                    else
                        
                        indices = ~cellfun(@isempty,regexpi(allDir,sourceForm));
                    end
                    
                    targetDirs = allDir(indices);
                    


                    %CHECK IF MORE THAN 1 RUN FOUND OF FILE
                    if isempty(targetDirs)
                        
                        fprintf(fidERROR,'PARTICIPANT %s_%s, FOLDER %s COULD NOT BE FOUND!\n',PARTICIPANT,TIMEPOINT,sourceForm);
                    
                    elseif length(targetDirs) > 1
                        
                        fprintf(fidREP,'PARTICIPANT %s_%s, FOLDER %s, has %d RUNS!\n',PARTICIPANT,TIMEPOINT,...
                            sourceForm,length(targetDirs));

                        %Loop through number of runs per measure
                        for j = 1 : length(targetDirs)


                            DCM_DIR = fullfile(SOURCE_DIR,strcat(PARTICIPANT,'_',TIMEPOINT),targetDirs(j));
                            DCM_DIR = char(DCM_DIR);
                            dicm2nii(DCM_DIR,dest,1);

                            
                            %Get list of dcm files to get the metadata for
                            %renaming
                            dcmList = dir(DCM_DIR);
                            dcmList = dcmList(~[dcmList.isdir]);
                            %Commented out as the dicom files did not end
                            %in .dcm
%                             dcmIndex = ~cellfun(@isempty,regexpi({dcmList.name},'(.*)\.dcm$'));
%                             dcmList = dcmList(dcmIndex);
                            info = dicominfo(fullfile(DCM_DIR,dcmList(1).name));
                            oldName = char(info.SeriesDescription);
                            oldName(~isstrprop(oldName, 'alphanum')) = '_';
                            

                            %String Print the new name for the dicm2nii output to
                            %be converted to
                            newName = sprintf(char(SOURCE_NAME(k,4)),PARTICIPANT,TIMEPOINT,j);

                            %Convert Output name to source format
                            convertName(oldName,dest,newName);
                            
                            
                            %add2JSON();
                        end
                        
                        fprintf(fidSUCCESS,'PARTICIPANT %s_%s, FOLDER %s SUCCESS!\n',PARTICIPANT,TIMEPOINT,sourceForm);


                    else


                        DCM_DIR = fullfile(SOURCE_DIR,strcat(PARTICIPANT,'_',TIMEPOINT),targetDirs);
                        DCM_DIR = char(DCM_DIR);
                        dicm2nii(DCM_DIR,dest,1);

                        %Get list of dcm files to get the metadata for
                        %renaming
                        dcmList = dir(DCM_DIR);
                        dcmList = dcmList(~[dcmList.isdir]);

                           %Commented out as the dicom files did not end in
                           %.dcm for some reason
%                         dcmIndex = ~cellfun(@isempty,regexpi({dcmList.name},'(.*)\.dcm$'));
% 
%                         dcmList = dcmList(dcmIndex);

                        info = dicominfo(fullfile(DCM_DIR,dcmList(1).name));
                        oldName = char(info.SeriesDescription);
                        % reference line from dicm2nii:
                        % a(~isstrprop(a, 'alphanum')) = '_'
                        oldName(~isstrprop(oldName, 'alphanum')) = '_';
                            
                            
                        %String Print the new name for the dicm2nii output to
                        %be converted to
                        newName = sprintf(char(SOURCE_NAME(k,3)),PARTICIPANT,TIMEPOINT);

                        %Convert Output name to BIDS format
                        convertName(oldName,dest,newName);
                        
                        fprintf(fidSUCCESS,'PARTICIPANT %s_%s, FOLDER %s SUCCESS!\n',PARTICIPANT,TIMEPOINT,sourceForm);
                        
                        %add2JSON();
                        

                    end
                
                 catch
                    
                    %TODO: ADD A FUNCTION TO OUTPUT ERROR MESSAGES WHEN
                    %THINGS GO WRONG
                   
                    %MAKE SURE THIS WORKS
                    disp('OOOPS')
                    fprintf(fidERROR,'PARTICIPANT %s_%s, FOLDER %s FAILED!\n',PARTICIPANT,TIMEPOINT,sourceForm);
                    
                 end
                
                
            end
            
            
        end
        
        
    end
    
    logend = sprintf(logtempF,datestr(datetime('now')));
    
    fprintf(fidSUCCESS,logend);
    fprintf(fidERROR,logend);
    fprintf(fidREP,logend);
    
    fclose(fidSUCCESS);
    fclose(fidERROR);
    fclose(fidREP);

end


%Simple function to check if a directory exists and, if not, to make it
function makedir(path)

    if ~exist(path,'dir')
       mkdir(path); 
    end

end


%Function to convert the name of the from the old format to the new format
%(BIDS)
%Does this for '.nii.gz','.json','.bvec','.bval'
function convertName(template,destination,newName)

    %Remove line terminating metacharacter if there
    if strcmp(template(end),'$')
        
        template = template(1:end-1);
        
    end
    
    searchDir = char(destination);
    
    fileList = dir(searchDir);
    fileList = fileList(~[fileList.isdir]);
    
    nameList = {fileList.name};
    
    %rename .nii.gz file
    try 
        index = ~cellfun(@isempty,regexpi(nameList,strcat(template,'.nii.gz$')));
        file = nameList(index);

        original = fullfile(destination,file);
        original = char(original);
        newfile = fullfile(destination,strcat(newName,'.nii.gz'));
        newfile = char(newfile);
    
        movefile(original,newfile);
    
    catch
        
        disp('OOOOPS')
        
    end
    
    %rename .json file
    try 
        index = ~cellfun(@isempty,regexpi(nameList,strcat(template,'.json$')));
        file = nameList(index);
    
        original = fullfile(destination,file);
        original = char(original);
        newfile = fullfile(destination,strcat(newName,'.json'));
        newfile = char(newfile);
    
        movefile(original,newfile);
    
    catch
        
    end
        
    %rename .bvec file
    try 
        index = ~cellfun(@isempty,regexpi(nameList,strcat(template,'.bvec$')));
        file = nameList(index);
    
        original = fullfile(destination,file);
        original = char(original);
        newfile = fullfile(destination,strcat(newName,'.bvec'));
        newfile = char(newfile);
    
        movefile(original,newfile);
    
    catch
        
    end
    
    %rename .bval file
    try 
        index = ~cellfun(@isempty,regexpi(nameList,strcat(template,'.bval$')));
        file = nameList(index);
    
        original = fullfile(destination,file);
        original = char(original);
        newfile = fullfile(destination,strcat(newName,'.bval'));
        newfile = char(newfile);
    
        movefile(original,newfile);
    
    catch
        
    end

    


end


% function add2JSON()
% 
% 
% end