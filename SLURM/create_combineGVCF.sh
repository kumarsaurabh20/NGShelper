#!/bin/bash
out_dir=/nobackup/beegfs/workspace/ks575/Data/Myzus/Myzus_mapping/Trimmed_Resequencing_Data_18_03_2019/VCF
ref=/nobackup/beegfs/workspace/ks575/Data/Myzus/Myzus_mapping/genome/Myzus_G006_sorted.FINAL.review.seal.filtered.5k.fasta
echo "gatk HaplotypeCaller -R $ref" > run_combineGVCF.sh
for each in $(find $(pwd)/VCF -name "*.vcf");do  echo "-V ${each}" >> run_combineGVCF.sh;done
echo "-O "${out_dir}/Myzus_100genomes_all_samples.vcf"" >> run_combineGVCF.sh
sed -i 's/\n/\s/g' run_combineGVCF.sh > run_combineGVCF2.sh
