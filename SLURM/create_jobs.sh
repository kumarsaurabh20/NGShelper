#!/bin/bash
work_dir="/nobackup/beegfs/workspace/ks575/Data/Myzus/Myzus_mapping/Trimmed_Resequencing_Data_18_03_2019/bams"
i=1
for each in $(find $(pwd) -name "*.sorted.bam")
do
	touch jobs.txt
	sample=$(echo $each | cut -d'/' -f11 | cut -d'.' -f1) 	
	echo "gatk AddOrReplaceReadGroups --INPUT=$each --OUTPUT="$work_dir/${sample}.sorted.RG.bam" --RGID=$i --RGLB=$sample --RGPL=illumina --RGPU=unit1 --RGSM=$sample --SORT_ORDER=coordinate" >> jobs.txt
	((i++))
done
