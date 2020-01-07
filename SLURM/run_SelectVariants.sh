#!/bin/bash -l
#SBATCH --partition=hmq
#SBATCH --job-name=selVCF
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=ks575@exeter.ac.uk
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=500gb
#SBATCH --time=240:05:00
#SBATCH --output=selectVCF_parallel_%j.log
#SBATCH --account=c.bass
##
pwd; hostname; date
export OMP_NUM_THREADS=1
pwd; hostname; date
echo "Running a program on $SLURM_JOB_NODELIST"
##
#/path/to/my/application
echo "Hello \$USER, this is running on the \$SLURM_CLUSTER_NAME cluster at \`hostname\` using PI account = \$SLURM_JOB_ACCOUNT"
module load slurm/18.08.4 Conda/Python2/2.7.15 GATK/4.1.0.0 samtools/1.9
gatk SelectVariants -V /nobackup/beegfs/workspace/ks575/Data/Myzus/Myzus_mapping/Trimmed_Resequencing_Data_18_03_2019/VCF/Myzus_100genomes_genotyped_samples.vcf --select-type-to-exclude MNP --select-type-to-exclude INDEL --select-type-to-include SNP -O /nobackup/beegfs/workspace/ks575/Data/Myzus/Myzus_mapping/Trimmed_Resequencing_Data_18_03_2019/VCF/Myzus_100genomes_genotyped_SNPs.vcf
