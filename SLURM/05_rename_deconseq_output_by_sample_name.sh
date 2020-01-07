#!/bin/bash
# rename cleaned deconseq files 
clear
basedir=/home/ISAD/mds207/adela_data
jobs_dir=$basedir/merged/deconseq-merged
cd $jobs_dir
echo "################################################################"
echo "I am in $PWD "
echo "################################################################"
echo "This script will go through all directories that start with LM   "
echo "and for each such directory that has a file ending in clean.fa2   "
echo "or cont.fa, it will rename those files based on the directory name"
echo "################################################################"
read -p "Press [Enter] key to continue..."
echo "################################################################"
echo " These are the commands I will execute, please validate them before hitting the next continue prompt."
echo "################################################################"
for subdir in LM*
 do echo "I will rename $subdir/*clean.fa as ${subdir}_R12_clean.fa";
 done
read -p "Press [Enter] key to continue..."
cd $jobs_dir
for subdir in LM*
 do 
	mv $subdir/*clean.fa ./clean/${subdir}_R12_clean.fa;
	mv $subdir/*cont.fa ./cont/${subdir}_R12_cont.fa;
done
# for file in $(ls -1 *_cont.fa); do mv $file ./cont/$file; done
# for file in $(ls -1 *_clean.fa); do mv $file ./clean/$file; done
