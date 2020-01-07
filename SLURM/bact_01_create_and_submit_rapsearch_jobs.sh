#!/bin/bash
clear
work_dir=/home/ISAD/mds207/adela_data
clean_dir=$work_dir/merged/deconseq-merged/clean
rap_dir=$work_dir/rap_clean_02_bact
megan_out=$rap_dir/megan_rma_files
nr_db=$work_dir/2.19_bact_nr_db
NSLOTS=30
#
#
# Make the rapdir if it does not already exist:
mkdir -p $rap_dir
# change into it and start creating the rapsearch job list etc.

cd $work_dir
echo "--------------------------------------------------------------------------"
echo "Copying the nr_db and nr_db.info files if they do not exist in $work_dir"
echo "Note that the nr_db file is very big and can take a while to copy over."
echo "--------------------------------------------------------------------------"
time cp -u /home/bio_app_support/rapsearch2_db/2.19_bact_nr_db . 
time cp -u /home/bio_app_support/rapsearch2_db/2.19_bact_nr_db.info .
echo "--------------------------------------------------------------------------"
read -p "Press [Enter] key to continue..."
#
cd $rap_dir
mkdir -p $rap_dir/logs
echo "Changed to $PWD"
echo "Removing the old rapsearc_jobs.txt file"
rm rapsearch_jobs.txt
echo "done"
echo "now creating a loop which will take a stock of all *R12.fasta files"
echo "in the $clean_dir directory and then dump a new rapsearch_jobs.txt"
echo "file with the commands we need to run in the $rap_dir path"
echo "--------------------------------------------------------------------------"
cd $clean_dir
for file in $( ls -1 *R12_clean.fa )
do
sample=$(echo $file | cut -c1-7)
echo "--------------------------------------------------------------------------"
echo "mkdir -p $rap_dir/rap_results/$sample"
echo "--------------------------------------------------------------------------"
mkdir -p $rap_dir/rap_results/$sample
LINE="rapsearch -q $clean_dir/$file -d $nr_db -z 30 -o $rap_dir/rap_results/$sample/$sample.rap -b 50 -v 50 -a t"
# echo "Currently processing command for $file"
#
echo "--------------------------------------------------------------------------"
echo "Creating batch file: $rap_dir/RS2_job_$sample.sh"
echo "--------------------------------------------------------------------------"

cat << EOF > $rap_dir/RS2job_$sample.sh

#!/bin/bash
#$ -N RS2$sample
#$ -S /bin/bash
#$ -o $rap_dir/logs
#$ -e $rap_dir/logs
#$ -q all.q
#$ -pe smp 30

# Send mail at submission and completion of script
#$ -m abes
#$ -M mds207@exeter.ac.uk

. /etc/profile.d/modules.sh
module add shared rapsearch2
cd $rap_dir
export OMP_NUM_THREADS=$NSLOTS
$LINE
EOF
#
done
echo "----------------------------------"
read -p "Press [Enter] to continue submitting or Ctrl +C to quit..."
echo "----------------------------------"
#
for job in $(ls -1 $rap_dir/RS2job_*.sh); do qsub $job; done
