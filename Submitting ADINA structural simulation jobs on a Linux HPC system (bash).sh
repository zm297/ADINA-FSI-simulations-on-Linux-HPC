#!/bin/bash

DATFILE_DIRECTORY=/home/zm297/rds/rds-meddings-sl2-cpu-tboN4gouV5s/_solid_robustness_/solid_robustness_datfile_bin/

cd $DATFILE_DIRECTORY

filenames=`ls *.dat`
for eachfile in $filenames
do
   cd $DATFILE_DIRECTORY
   echo doing $eachfile ...
   DATFILE=$eachfile
   DATPATH=/home/zm297/rds/rds-meddings-sl2-cpu-tboN4gouV5s/_solid_robustness_/solid_robustness_result_bin/$eachfile
   mkdir -p $DATPATH
   cp $eachfile $DATPATH

   cd $DATPATH

   # if there's no porfile there, then submit. 
   if ! [ -f *.por ]; then
   ### invoke solution-running script.
     screen -dm -S s /bin/bash -c "source /home/zm297/rds/hpc-work/solid_test.sh $DATFILE $DATPATH"
     echo no porfile here for $eachfile so job was submitted. 
     echo datfile was $DATFILE and datpath was $DATPATH
   #sleep 1m
   fi
done

###################################### in the normal (single param set) study ########################################

DATFILE_DIRECTORY=/home/zm297/rds/rds-meddings-sl2-cpu-tboN4gouV5s/_solid_standard_/datfile_bin/

cd $DATFILE_DIRECTORY


filenames=`ls *.dat`
for eachfile in $filenames
do
   cd $DATFILE_DIRECTORY
   echo doing $eachfile ...
   DATFILE=$eachfile
   DATPATH=/home/zm297/rds/rds-meddings-sl2-cpu-tboN4gouV5s/_solid_standard_/result_bin/$eachfile
   mkdir -p $DATPATH
   cp $eachfile $DATPATH

   cd $DATPATH

   # if there's no porfile there, then submit. 
   if ! [ -f *.por ]; then
   ### invoke solution-running script.
     screen -dm -S s /bin/bash -c "source /home/zm297/rds/hpc-work/solid_test.sh $DATFILE $DATPATH"
     echo no porfile here for $eachfile so job was submitted. 
     echo datfile was $DATFILE and datpath was $DATPATH
   #sleep 1m
   fi
done

######################################################################################################################








######################################         
####################################                        
####################################                               
### Starting with the result. ########                                  
####################################                             
####################################           
####################################
DATFOLDER_DIRECTORY=/home/zm297/rds/rds-meddings-sl2-cpu-tboN4gouV5s/_solid_robustness_/solid_robustness_result_bin/

cd $DATFOLDER_DIRECTORY

foldernames=`ls -d 16521*.dat/`
for eachfolder in $foldernames
do
   cd $DATFOLDER_DIRECTORY
   echo doing $eachfolder ...

   DATPATH=/home/zm297/rds/rds-meddings-sl2-cpu-tboN4gouV5s/_solid_robustness_/solid_robustness_result_bin/$eachfolder
   cd $DATPATH 

   DATFILE=`ls 16521*.dat`
   # if there's no porfile there, then submit. 
   if ! [ -f *.por ]; then
    # find . -name "*.por" -type f -delete
    screen -dm -S s /bin/bash -c "source /home/zm297/rds/hpc-work/solid_test.sh $DATFILE $DATPATH"
    echo no porfile here for $eachfile so job was submitted. 
   #sleep 1m
   fi
done


16521






