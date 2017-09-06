#!/bin/bash

#Contamination check on raw reads using Centriguge ##
##########################################################
/home2/ISAD/ks575/Data/Osmia_contamination_check
#Paired
#-------
/athena-home/ks575/Discovar_raw_data/1545_LIB18336_LDI15827_NoIndex_L001_R1_val_1.fq
/athena-home/ks575/Discovar_raw_data/1545_LIB18336_LDI15827_NoIndex_L001_R2_val_2.fq
#Unpaired
#--------
/athena-home/ks575/Discovar_raw_data/1545_LIB18336_LDI15827_NoIndex_L001_R1_unpaired_1.fq
/athena-home/ks575/Discovar_raw_data/1545_LIB18336_LDI15827_NoIndex_L001_R2_unpaired_2.fq
#Use centrifuge-download to download genomes from NCBI. The following two commands download the NCBI taxonomy to taxonomy/ in the current directory, and all complete archaeal, bacterial and viral genomes to library/. Low-complexity regions in the genomes are masked after download (parameter -m) using blast+'s dustmasker. centrifuge-download outputs tab-separated sequence ID to taxonomy ID mappings to standard out, which are required by centrifuge-build.
centrifuge-download -o taxonomy taxonomy
centrifuge-download -o library -m -d "archaea,bacteria,viral" refseq > seqid2taxid.map
#The human and mouse genomes can also be downloaded using centrifuge-download. They are in the domain "vertebrate_mammalian" (argument -d), are assembled at the chromosome level (argument -a) and categorized as reference genomes by RefSeq (-c). The argument -t takes a comma-separated list of taxonomy IDs - e.g. 9606 for human and 10090 for mouse:
centrifuge-download -o library -a "Chromosome" -t 9606,10090 -c 'reference genome' -d "vertebrate_mammalian" refseq >> seqid2taxid.map
#To build the index, first concatenate all downloaded sequences into a single file, and then run centrifuge-build:
cat library/*/*.fna > input-sequences.fna
## build centrifuge index with 4 threads
centrifuge-build -p 32 --conversion-table seqid2taxid.map --taxonomy-tree taxonomy/nodes.dmp --name-table taxonomy/names.dmp input-sequences.fna abv
#NCBI BLAST's nt database contains all spliced non-redundant coding sequences from multiplpe databases, inferred from genommic sequences. Traditionally used with BLAST, a download of the FASTA is provided on the NCBI homepage. Building an index with any database requires the user to creates a sequence ID to taxonomy ID map that can be generated from a GI taxid dump:
wget ftp://ftp.ncbi.nih.gov/blast/db/FASTA/nt.gz
gunzip nt.gz && mv -v nt nt.fa
# Get mapping file
wget ftp://ftp.ncbi.nih.gov/pub/taxonomy/gi_taxid_nucl.dmp.gz
gunzip -c gi_taxid_nucl.dmp.gz | sed 's/^/gi|/' > gi_taxid_nucl.map
# build index using 16 cores and a small bucket size, which will require less memory
centrifuge-build -p 32 --bmax 1342177280 --conversion-table gi_taxid_nucl.map --taxonomy-tree taxonomy/nodes.dmp --name-table taxonomy/names.dmp nt.fa nt
centrifuge -p 20 -x abv -1 /athena-home/ks575/Discovar_raw_data/1545_LIB18336_LDI15827_NoIndex_L001_R1_val_1.fq -2 /athena-home/ks575/Discovar_raw_data/1545_LIB18336_LDI15827_NoIndex_L001_R2_val_2.fq -S abv_classification_results.tab --report-file abv_centrifuge_report.tsv
#report file abv_centrifuge_report.tsv
#Number of iterations in EM algorithm: 104
#Probability diff. (P - P_prev) in the last iteration: 8.69644e-11
#Calculating abundance: 00:00:00
centrifuge -p 20 -x abv -1 /athena-home/ks575/Discovar_raw_data/1545_LIB18336_LDI15827_NoIndex_L001_R1_val_1.fq -2 /athena-home/ks575/Discovar_raw_data/1545_LIB18336_LDI15827_NoIndex_L001_R2_val_2.fq -S nt_classification_results.tab --report-file nt_centrifuge_report.tsv
#report file Osmia_nt_centrifuge_report.tsv
#Number of iterations in EM algorithm: 104
#Probability diff. (P - P_prev) in the last iteration: 8.69644e-11
#Calculating abundance: 00:00:00

