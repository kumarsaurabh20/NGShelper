#!/bin/bash

clear
basedir=/home/ISAD/mds207/adela_data
jobs_dir=$basedir/merged/joblist

OIFS=$IFS; IFS=$'\n'; LINES=($(<$jobs_dir/jobs.txt)); IFS=$OIFS
i=1
NSLOTS=4
totlines=`cat $jobs_dir/jobs.txt | wc -l`
echo $totlines

for LINE in "${LINES[@]}"
do
   echo $LINE

cat << EOF > $jobs_dir/DECONSEQ_jobs_batch$i.sh

#!/bin/bash
#$ -N dcseq$i
#$ -S /bin/bash
#$ -o /home/ISAD/mds207/adela_data/merged/logs
#$ -e /home/ISAD/mds207/adela_data/merged/logs
#$ -q all.q
#$ -pe openmpi_ib 4

# Send mail at submission and completion of script
#$ -m abes
#$ -M mds207@exeter.ac.uk
. /etc/profile.d/modules.sh
module add shared sge prinseq deconseq
cd /home/ISAD/mds207/adela_data/merged/split_files
$LINE
EOF

((i++))

done
