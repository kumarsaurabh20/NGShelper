#!/bin/bash -l
#SBATCH --partition=hmq
#SBATCH --job-name=filterVCF
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=ks575@exeter.ac.uk
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=500gb
#SBATCH --time=240:05:00
#SBATCH --output=filterVCF_parallel_%j.log
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
gatk VariantFiltration -R /nobackup/beegfs/workspace/ks575/Data/Myzus/Myzus_mapping/genome/Myzus_G006_sorted.FINAL.review.seal.filtered.5k.fasta -V /nobackup/beegfs/workspace/ks575/Data/Myzus/Myzus_mapping/Trimmed_Resequencing_Data_18_03_2019/VCF/Myzus_100genomes_genotyped_SNPs.vcf -O /nobackup/beegfs/workspace/ks575/Data/Myzus/Myzus_mapping/Trimmed_Resequencing_Data_18_03_2019/VCF/MP100g.genotyped.SNPs.filtered.vcf --filter-name "LowQ" --filter-expression "QD < 8.0 || MQ < 40.0 || FS > 60.0 || MQRankSum < -12.5 || SOR > 3.0 || ReadPosRankSum < -8.0 || GQ <= 30 || DP < 10"
