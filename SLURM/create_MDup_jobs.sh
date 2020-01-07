#!/bin/bash
work_dir=/nobackup/beegfs/workspace/ks575/Data/Myzus/Myzus_mapping/Trimmed_Resequencing_Data_18_03_2019/bams
for each in $(find $(pwd) -name "*.sorted.RG.bam")
do
	touch jobs.txt
	sample=$(echo $each | cut -d'/' -f11 | cut -d'.' -f1) 
	echo "samtools sort -@ 16 -m 6G -n -o "${work_dir}/${sample}.readsorted.bam" "${each}";samtools fixmate -m -@ 16 "${work_dir}/${sample}.readsorted.bam" "${work_dir}/${sample}.fixmate.bam";samtools sort -@ 16 -m 6G -o "${work_dir}/${sample}.fx.sorted.bam" "${work_dir}/${sample}.fixmate.bam";samtools markdup -s -@ 16 "${work_dir}/${sample}.fx.sorted.bam" "${work_dir}/${sample}.dedup.bam";samtools index -@ 16 "${work_dir}/${sample}.dedup.bam"" >> jobs.txt
done
