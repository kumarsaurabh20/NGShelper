#!/bin/bash
clear
work_dir=$WORKSPACE/Data/Myzus/Myzus_mapping/Trimmed_Resequencing_Data_18_03_2019/batch_other
##edit this line to specify filter
scripts=$work_dir/scripts

OIFS=$IFS; IFS=$'\n'; LINES=($(<$work_dir/jobs.txt)); IFS=$OIFS
i=1
NSLOTS=16
for LINE in "${LINES[@]}"
do
echo $LINE
cat << EOF > $scripts/jobs_batch${i}.sh
#!/bin/bash -l
#SBATCH --partition=hmq
#SBATCH --job-name=trim$i
#SBATCH --mail-type=FAIL 
#SBATCH --mail-user=ks575@exeter.ac.uk
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=${NSLOTS}
#SBATCH --mem=10gb
#SBATCH --time=240:05:00
#SBATCH --output=map${i}_parallel_%j.log
#SBATCH --account=c.bass
##
pwd; hostname; date
export OMP_NUM_THREADS=$NSLOTS
pwd; hostname; date
echo "Running a program on $SLURM_JOB_NODELIST"
##
#/path/to/my/application
echo "Hello \$USER, this is running on the \$SLURM_CLUSTER_NAME cluster at \`hostname\` using PI account = \$SLURM_JOB_ACCOUNT"
module load slurm/18.08.4 Workspace/v1 Conda/Python2/2.7.15 ks575/Trim-galore/v0.6.2 
work_dir=$WORKSPACE/Data/Myzus/Myzus_mapping/Trimmed_Resequencing_Data_18_03_2019/batch_other
$LINE
EOF

((i++))
done
