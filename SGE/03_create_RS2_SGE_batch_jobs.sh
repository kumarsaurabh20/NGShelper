#!/bin/bash
# clear
work_dir=/nobackup/beegfs/workspace/ks575/Data/Myzus/Myzus_mapping/Trimmed_Resequencing_Data_18_03_2019
#
#
OIFS=$IFS; IFS=$'\n'; LINES=($(<$work_dir/jobs.txt)); IFS=$OIFS
i=1
NSLOTS=44
totlines=`cat ${work_dir}/jobs.txt | wc -l`
echo "I have just read ${work_dir}/jobs.txt and it seems to have"
echo "$totlines lines in it."
read -p "Press [Enter] key continue creating the batch files..."

for LINE in "${LINES[@]}"
do
   #echo "Welcome $i times"
   #myline="${LINES[$i]}"
   echo $LINE

cat << EOF > $work_dir/RS2_jobs_batch$i.sh

#!/bin/bash
#$ -N rap$i
#$ -S /bin/bash
#$ -o $rap_dir/logs
#$ -e $rap_dir/logs
#$ -q all.q
#$ -pe openmpi_ib 44

# Send mail at submission and completion of script
#$ -m abes
#$ -M mds207@exeter.ac.uk

. /etc/profile.d/modules.sh
module add shared rapsearch2
cd $rap_dir
export OMP_NUM_THREADS=$NSLOTS
$LINE
EOF

((i++))

done
