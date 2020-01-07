#!/bin/bash
clear
work_dir=/home/ISAD/mds207/adela_data
clean_dir=$work_dir/merged/deconseq-merged/clean
rap_dir=$work_dir/rap_clean_01

cd $rap_dir
for i in $(ls -1 RS2_jobs_batch*.sh); do qsub $i ; done


