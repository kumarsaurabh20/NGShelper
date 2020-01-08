####### Script to this automatically ###
#!/bin/bash
clear
basedir=/home/ISAD/mds207/adela_data
jobs_dir=$basedir/merged/joblist
cd $jobs_dir
for i in $(ls -1 DECONSEQ_jobs_batch*.sh); do qsub $i ; done
