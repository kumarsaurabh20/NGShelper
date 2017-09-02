#!/bin/bash

#Popoolation2 Analysis
#======================
#1. Aligning all the samples against reference using BWA
#Index
#-----
#Resistant
#**********

#5191A	- LIB15046
#-------------------
bwa mem -M -t 20 -R '@RG\tID:LIB15046\tSM:5191A' /home2/ISAD/ks575/Data/myzus_dnaseq/G006b_filled.fa /home2/ISAD/ks575/Data/myzus_dnaseq/LIB15046/1404_LIB15046_LDI12644_CTTGTA_L006_R1_val_1.fq /home2/ISAD/ks575/Data/myzus_dnaseq/LIB15046/1404_LIB15046_LDI12644_CTTGTA_L006_R2_val_2.fq | samtools view -b -S -F 4 -o LIB15046.bam -

#5410R	- LIB18342
#-------------------
bwa mem -M -t 20 -R '@RG\tID:LIB18342\tSM:5410R' /home2/ISAD/ks575/Data/myzus_dnaseq/G006b_filled.fa /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18342_new/all_LIB18342_R1.fastq /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18342_new/all_LIB18342_R2.fastq | samtools view -b -S -F 4 -o LIB18342.bam -

#5410G	- LIB18343
#------------------
bwa mem -M -t 20 -R '@RG\tID:LIB18343\tSM:5410G' /home2/ISAD/ks575/Data/myzus_dnaseq/G006b_filled.fa  /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18343/LIB18343_LDI15834_AGTTCC_R1_val_1.fq /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18343/LIB18343_LDI15834_AGTTCC_R2_val_2.fq | samtools view -b -S -F 4 -o LIB18343.bam -

#926B	- LIB18344
#-------------------
bwa mem -M -t 20 -R '@RG\tID:LIB18344\tSM:926B' /home2/ISAD/ks575/Data/myzus_dnaseq/G006b_filled.fa /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18344/LIB18344_LDI15835_ATGTCA_R1_val_1.fq /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18344/LIB18344_LDI15835_ATGTCA_R2_val_2.fq | samtools view -b -S -F 4 -o LIB18344.bam -

#57	- LIB18346
#-------------------
bwa mem -M -t 20 -R '@RG\tID:LIB18346\tSM:57' /home2/ISAD/ks575/Data/myzus_dnaseq/G006b_filled.fa /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18346/LIB18346_LDI15837_GTCCGC_R1_val_1.fq /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18346/LIB18346_LDI15837_GTCCGC_R2_val_2.fq | samtools view -b -S -F 4 -o LIB18346.bam -

#124	- LIB18347
#------------------
bwa mem -M -t 20 -R '@RG\tID:LIB18347\tSM:124' /home2/ISAD/ks575/Data/myzus_dnaseq/G006b_filled.fa /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18347/LIB18347_LDI15838_GTGAAA_R1_val_1.fq /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18347/LIB18347_LDI15838_GTGAAA_R2_val_2.fq | samtools view -b -S -F 4 -o LIB18347.bam -

#Susceptible
#************
#4106A	- LIB15045
#------------------
bwa mem -M -t 20 -R '@RG\tID:LIB15045\tSM:4106A' /home2/ISAD/ks575/Data/myzus_dnaseq/G006b_filled.fa /home2/ISAD/ks575/Data/myzus_dnaseq/LIB15045/1404_LIB15045_LDI12643_GCCAAT_L006_R1_val_1.fq /home2/ISAD/ks575/Data/myzus_dnaseq/LIB15045/1404_LIB15045_LDI12643_GCCAAT_L006_R2_val_2.fq | samtools view -b -S -F 4 -o LIB15045.bam -

#1X	- LIB18337
#------------------
bwa mem -M -t 20 -R '@RG\tID:LIB18337\tSM:1X' /home2/ISAD/ks575/Data/myzus_dnaseq/G006b_filled.fa  /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18337_new/all_LIB18337_R1.fastq /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18337_new/all_LIB18337_R2.fastq | samtools view -b -S -F 4 -o LIB18337.bam -

#4255A	- LIB18339
#------------------
bwa mem -M -t 20 -R '@RG\tID:LIB18339\tSM:4255A' /home2/ISAD/ks575/Data/myzus_dnaseq/G006b_filled.fa /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18339/LIB18339_LDI15830_GCCAAT_R1_val_1.fq /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18339/LIB18339_LDI15830_GCCAAT_R2_val_2.fq | samtools view -b -S -F 4 -o LIB18339.bam -

#NS	- LIB18338
#------------------
bwa mem -M -t 20 -R '@RG\tID:LIB18338\tSM:NS' /home2/ISAD/ks575/Data/myzus_dnaseq/G006b_filled.fa /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18338/LIB18338_LDI15829_ACAGTG_R1_val_1.fq /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18338/LIB18338_LDI15829_ACAGTG_R2_val_2.fq | samtools view -b -S -F 4 -o LIB18338.bam -

#US1L	- LIB18340
#------------------
bwa mem -M -t 20 -R '@RG\tID:LIB18340\tSM:US1L' /home2/ISAD/ks575/Data/myzus_dnaseq/G006b_filled.fa /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18340/LIB18340_LDI15831_CAGATC_R1_val_1.fq /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18340/LIB18340_LDI15831_CAGATC_R2_val_2.fq | samtools view -b -S -F 4 -o LIB18340.bam -

#23	- LIB18341
#------------------
bwa mem -M -t 20 -R '@RG\tID:LIB18341\tSM:23' /home2/ISAD/ks575/Data/myzus_dnaseq/G006b_filled.fa /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18341/LIB18341_R1_sickle_20.fastq /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18341/LIB18341_R2_sickle_20.fastq | samtools view -b -S -F 4 -o LIB18341.bam -

cat /home2/ISAD/ks575/Data/myzus_dnaseq/1545_LIB18341_LDI15832_CTTGTA_L002_R1.fastq.gz 1549_LIB18341_LDI15832_CTTGTA_L001_R1.fastq.gz /home2/ISAD/ks575/Data/myzus_dnaseq/1549_LIB18341_LDI15832_CTTGTA_L002_R1.fastq.gz > all_LIB18341_merged_R1.fastq.gz
cat /home2/ISAD/ks575/Data/myzus_dnaseq/1545_LIB18341_LDI15832_CTTGTA_L002_R2.fastq.gz 1549_LIB18341_LDI15832_CTTGTA_L001_R2.fastq.gz /home2/ISAD/ks575/Data/myzus_dnaseq/1549_LIB18341_LDI15832_CTTGTA_L002_R2.fastq.gz > all_LIB18341_merged_R2.fastq.gz
#
trim_galore --phred33 --illumina --length 20 --paired --retain_unpaired --dont_gzip -o . all_LIB18341_merged_R1.fastq.gz all_LIB18341_merged_R2.fastq.gz
#
bwa mem -M -t 20 -R '@RG\tID:LIB18341\tSM:23' /home2/ISAD/ks575/Data/myzus_dnaseq/G006b_filled.fa /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18341/new/all_LIB18341_merged_R1_val_1.fq /home2/ISAD/ks575/Data/myzus_dnaseq/LIB18341/new/all_LIB18341_merged_R2_val_2.fq  | samtools view -b -S -F 4 -o LIB18341.bam -
#
#2. Filter the reads based on quality using samtools (-q 20)
samtools view --threads 10 -q 20 -b LIB15045.bam | samtools sort --threads 10 -o LIB15045.sorted.bam -
samtools view --threads 10 -q 20 -b LIB15046.bam | samtools sort --threads 10 -o LIB15046.sorted.bam -
samtools view --threads 10 -q 20 -b LIB18337.bam | samtools sort --threads 10 -o LIB18337.sorted.bam -
samtools view --threads 10 -q 20 -b LIB18338.bam | samtools sort --threads 10 -o LIB18338.sorted.bam -
samtools view --threads 10 -q 20 -b LIB18339.bam | samtools sort --threads 10 -o LIB18339.sorted.bam -
samtools view --threads 10 -q 20 -b LIB18340.bam | samtools sort --threads 10 -o LIB18340.sorted.bam -
samtools view --threads 10 -q 20 -b LIB18341.bam | samtools sort --threads 10 -o LIB18341.sorted.bam -
samtools view --threads 10 -q 20 -b LIB18342.bam | samtools sort --threads 10 -o LIB18342.sorted.bam -
samtools view --threads 10 -q 20 -b LIB18343.bam | samtools sort --threads 10 -o LIB18343.sorted.bam -
samtools view --threads 10 -q 20 -b LIB18344.bam | samtools sort --threads 10 -o LIB18344.sorted.bam -
samtools view --threads 10 -q 20 -b LIB18346.bam | samtools sort --threads 10 -o LIB18346.sorted.bam -
samtools view --threads 10 -q 20 -b LIB18347.bam | samtools sort --threads 10 -o LIB18347.sorted.bam -

#3. Mark duplicates
#FilterSamReads
#MarkDuplicates
#Usage example: java -jar picard.jar MarkDuplicates I=input.bam O=marked_duplicates.bam M=marked_dup_metrics.txt
#java -Xmx20g -jar /home2/ISAD/ks575/software/picard/2.2.4/picard.jar MarkDuplicates I=input.bam O=marked_duplicates.bam M=marked_dup_metrics.txt
#(VALIDATION_STRINGENCY=STRICT)
java -Xmx20g -jar /home2/ISAD/ks575/software/picard/2.2.4/picard.jar MarkDuplicates REMOVE_DUPLICATES=true I=LIB15045.sorted.bam O=LIB15045.sorted.dedup.bam M=LIB15045_marked_dup_metrics.txt
java -Xmx20g -jar /home2/ISAD/ks575/software/picard/2.2.4/picard.jar MarkDuplicates REMOVE_DUPLICATES=true I=LIB15046.sorted.bam O=LIB15046.sorted.dedup.bam M=LIB15046_marked_dup_metrics.txt
java -Xmx20g -jar /home2/ISAD/ks575/software/picard/2.2.4/picard.jar MarkDuplicates REMOVE_DUPLICATES=true I=LIB18337.sorted.bam O=LIB18337.sorted.dedup.bam M=LIB18337_marked_dup_metrics.txt
java -Xmx20g -jar /home2/ISAD/ks575/software/picard/2.2.4/picard.jar MarkDuplicates REMOVE_DUPLICATES=true I=LIB18338.sorted.bam O=LIB18338.sorted.dedup.bam M=LIB18338_marked_dup_metrics.txt
java -Xmx20g -jar /home2/ISAD/ks575/software/picard/2.2.4/picard.jar MarkDuplicates REMOVE_DUPLICATES=true I=LIB18339.sorted.bam O=LIB18339.sorted.dedup.bam M=LIB18339_marked_dup_metrics.txt
java -Xmx20g -jar /home2/ISAD/ks575/software/picard/2.2.4/picard.jar MarkDuplicates REMOVE_DUPLICATES=true I=LIB18340.sorted.bam O=LIB18340.sorted.dedup.bam M=LIB18340_marked_dup_metrics.txt
java -Xmx20g -jar /home2/ISAD/ks575/software/picard/2.2.4/picard.jar MarkDuplicates REMOVE_DUPLICATES=true I=LIB18341.sorted.bam O=LIB18341.sorted.dedup.bam M=LIB18341_marked_dup_metrics.txt
java -Xmx20g -jar /home2/ISAD/ks575/software/picard/2.2.4/picard.jar MarkDuplicates REMOVE_DUPLICATES=true I=LIB18342.sorted.bam O=LIB18342.sorted.dedup.bam M=LIB18342_marked_dup_metrics.txt
java -Xmx20g -jar /home2/ISAD/ks575/software/picard/2.2.4/picard.jar MarkDuplicates REMOVE_DUPLICATES=true I=LIB18343.sorted.bam O=LIB18343.sorted.dedup.bam M=LIB18343_marked_dup_metrics.txt
java -Xmx20g -jar /home2/ISAD/ks575/software/picard/2.2.4/picard.jar MarkDuplicates REMOVE_DUPLICATES=true I=LIB18344.sorted.bam O=LIB18344.sorted.dedup.bam M=LIB18344_marked_dup_metrics.txt
java -Xmx20g -jar /home2/ISAD/ks575/software/picard/2.2.4/picard.jar MarkDuplicates REMOVE_DUPLICATES=true I=LIB18346.sorted.bam O=LIB18346.sorted.dedup.bam M=LIB18346_marked_dup_metrics.txt
java -Xmx20g -jar /home2/ISAD/ks575/software/picard/2.2.4/picard.jar MarkDuplicates REMOVE_DUPLICATES=true I=LIB18347.sorted.bam O=LIB18347.sorted.dedup.bam M=LIB18347_marked_dup_metrics.txt

#4. Create a Synchronized file
samtools mpileup -B ../../LIB15045.sorted.dedup.bam ../../LIB18337.sorted.dedup.bam ../../LIB18338.sorted.dedup.bam ../../LIB18339.sorted.dedup.bam ../../LIB18340.sorted.dedup.bam ../../LIB18341.sorted.dedup.bam ../../LIB15046.sorted.dedup.bam ../../LIB18342.sorted.dedup.bam ../../LIB18343.sorted.dedup.bam ../../LIB18344.sorted.dedup.bam ../../LIB18346.sorted.dedup.bam ../../LIB18347.sorted.dedup.bam > all_dnaseq_samples.mpileup
#
java -ea -Xmx20g -jar /home2/ISAD/ks575/software/popoolation2/popoolation2_1201/mpileup2sync.jar --input all_dnaseq_samples.mpileup --output all_dnaseq_samples.sync --fastq-type sanger --min-qual 20 --threads 32 

#Site frequency spectrum
#-------------------------
perl /home2/ISAD/ks575/software/popoolation2/popoolation2_1201/snp-frequency-diff.pl --input all_dnaseq_samples.sync --output-prefix myzus_all_samples --min-count 3 --min-coverage 6 --max-coverage 200
#This script creates two output files having two different extensions:
#
#_rc: this file contains the major and minor alleles for every SNP in a concise format
#_pwc: this file contains the differences in allele frequencies for every pairwise comparision of the populations present in the synchronized file
#The allele frequency differences can be found in the _pwc file, a small sample:
##chr   pos     rc      allele_count    allele_states   deletion_sum    snp_type        most_variable_allele    diff:1-2
#2R      4459    N       2       C/T     0       pop     T       0.133
#2R      9728    N       2       T/C     0       pop     T       0.116
#
#The last column contains the obtained differences in allele frequencies for the allele provided in column 8. Note that in this example the last column refers to a pairwise comparision between population 1 vs 2, in case several populations are provided all pairwise comparisions will be appended in additional columns.

#Calculate Fst for every SNP
perl /home2/ISAD/ks575/software/popoolation2/popoolation2_1201/fst-sliding.pl --input all_dnaseq_samples.sync --output myzus_all_samples.fst --min-count 3 --min-coverage 6 --max-coverage 200 --pool-size 500 --window-size 100 --step-size 100 --suppress-noninformative
#column 1: reference contig
#column 2: position of the window (middle)
#column 3: SNPs identified in the window
#column 4: fraction of window having sufficient coverage
#column 5: average minimum coverage
#column >5: Fst values for all pairwise comparisons; For example "2:3=0.02" states that the Fst for comparing population 2 with population 3 (using the order of the synchronized file) is 0.2

#Perform Fisher-exact test using Allele frequency
perl /home2/ISAD/ks575/software/popoolation2/popoolation2_1201/fisher-test.pl --input all_dnaseq_samples.sync --output myzus_all_samples.fet --min-count 3 --min-coverage 6 --max-coverage 200 --suppress-noninformative


#Cochran-Mantel-Haenszel test: detect consistent allele frequency changes in several biological replicates
#-----------------------------------------------------------------------------------------------------------
#The cmh-test (http://stat.ethz.ch/R-manual/R-devel/library/stats/html/mantelhaen.test.html) is used for detecting significant and consistent changes in allele frequencies when independent measurements of the allele frequencies have been obtained (e.g.: biological replicates). For example when you are interested in the SNPs responsible for plant height, you may obtain several measurements of the allele frequencies of tall and small plants from different ecological regions. Using the cmh-test you may want to detect consistent differences (consistent between small and tall) in allele frequency for the following comparisions: small_alaska vs tall_alaska + small_norway vs tall_norway + small_sibiria vs tall_sibiria
perl /home2/ISAD/ks575/software/popoolation2/popoolation2_1201/cmh-test2.pl --input all_dnaseq_samples.sync --output Within_Susceptible_1_vs_all.cmh --min-count 3 --min-coverage 6 --max-coverage 200 --population 1-7,1-8,1-9,1-10,1-11,1-12,2-7,2-8,2-9,2-10,2-11,2-12,3-7,3-8,3-9,3-10,3-11,3-12,4-7,4-8,4-9,4-10,4-11,4-12,5-7,5-8,5-9,5-10,5-11,5-12,6-7,6-8,6-9,6-10,6-11,6-12 --remove-temp

