#!/bin/bash
work_dir=/nobackup/beegfs/workspace/ks575/Data/Myzus/Myzus_mapping/Trimmed_Resequencing_Data_18_03_2019/bams
out_dir=/nobackup/beegfs/workspace/ks575/Data/Myzus/Myzus_mapping/Trimmed_Resequencing_Data_18_03_2019/VCF
ref=/nobackup/beegfs/workspace/ks575/Data/Myzus/Myzus_mapping/genome/Myzus_G006_sorted.FINAL.review.seal.filtered.5k.fasta
for each in $(find $(pwd) -name "*.dedup.bam")
do
	touch jobs.txt
	sample=$(echo $each | cut -d'/' -f11 | cut -d'.' -f1) 
	echo "gatk HaplotypeCaller --input "${each}" --output "${out_dir}/${sample}.raw.vcf" --reference "${ref}" --min-base-quality-score 25 --native-pair-hmm-threads 16 --output-mode EMIT_VARIANTS_ONLY --standard-min-confidence-threshold-for-calling 30 --emit-ref-confidence GVCF --minimum-mapping-quality 25" >> jobs.txt
done
