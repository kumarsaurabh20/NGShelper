####### Script to this automatically ###
#!/bin/bash
work_dir=/home/ISAD/mds207/adela_data
clean_dir=$work_dir/merged/deconseq-merged/clean
rap_dir=$work_dir/rap_clean_01
# using the merged fasta files in this case so we only need to
# use the standard nr_db compiled with an appropriate version of pre-rapsearch
# this version was compiled with rapsearch v 2.18
nr_db=$work_dir/nr_db
cd $work_dir
echo "--------------------------------------------------------------------------"
echo "Copying the nr_db and nr_db.info files if they do not exist in $work_dir"
echo "Note that the nr_db file is very big and can take a while to copy over."
echo "--------------------------------------------------------------------------"
time cp -u /home/bio_app_support/rapsearch2_db/nr_db .
time cp -u /home/bio_app_support/rapsearch2_db/nr_db.info .
echo "--------------------------------------------------------------------------"
echo "Removing the old rapsearc_jobs.txt file"
rm rapsearch_jobs.txt
echo "done"
echo "now creating a loop which will take a stock of all *R12.fasta files"
echo "in the $work_dir/merged directory"
echo "and then dump a new rapsearch_jobs.txt file with the commands we need to run"
echo "in the $work_dir path"
echo "--------------------------------------------------------------------------"
cd $clean_dir
for file in $( ls -1 *R12_clean.fa )
do
sample=$(echo $file | cut -c1-7)
echo "--------------------------------------------------------------------------"
echo "I will try to run this command to create a new results directory:"
echo "mkdir -p $PWD/rap_results/$sample"
echo "please move or delete any old results from this directory before running the third script"
echo "otherwise your results may be over written."
echo "--------------------------------------------------------------------------"
mkdir -p $rap_dir/rap_results/$sample
echo "rapsearch -q $PWD/$file -d $nr_db -z 40 -o $rap_dir/rap_results/$sample/$sample.rap -b 50 -v 50 -a t" >> $rap_dir/rapsearch_jobs.txt
# echo "Currently processing command for $file"
done
echo "----------------------------------"
echo "All Done... proceed to step three "
echo "----------------------------------"

