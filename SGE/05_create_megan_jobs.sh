#!/bin/bash
clear
work_dir=/home/ISAD/mds207/adela_data
clean_dir=$work_dir/merged/deconseq-merged/clean
rap_dir=$work_dir/rap_clean_01
megan_out=$rap_dir/megan_rma_files
#
#

NSLOTS=16
#
mkdir -p $rap_dir/megan_rma_files
cd $rap_dir/rap_results
echo "I am currently working in $PWD"
read -p "Press [Enter] to run the loop and generate MEGAN commands text and batch files..."
for sample in LM_*
	do

cat << EOF > $rap_dir/megan_commands_$sample.txt
load taxGIFile='/cm/shared/apps/megan/5.3.0/gi_taxid_prot.bin';
load keggGIFile='/cm/shared/apps/megan/5.3.0/gi2kegg.map';
import blastFile=$rap_dir/$sample/$sample.rap.aln meganFile=$megan_out/$sample.rap.rma maxMatches=100 minScore=50.0 maxExpected=1.0 topPercent=10 minSupport=5 minComplexity=0.44 useMinimalCoverageHeuristic=false useSeed=false useCOG=false useKegg=true paired=false useIdentityFilter=false textStoragePolicy=0 blastFormat=RapSearch mapping='Taxonomy:GI_MAP=true,KEGG:GI_MAP=true';
quit;
EOF


cat << EOF > $rap_dir/MEGAN_job_$sample.sh

#!/bin/bash
#$ -N MEG_$sample
#$ -S /bin/bash
#$ -o $rap_dir/logs
#$ -e $rap_dir/logs
#$ -q all.q
#$ -pe openmpi_ib 16

# Send mail at submission and completion of script
#$ -m abes
#$ -M mds207@exeter.ac.uk
. /etc/profile.d/modules.sh
module add shared megan
cd $rap_dir
export OMP_NUM_THREADS=$NSLOTS
xvfb-run -a MEGAN -MC 16 -g -c $rap_dir/megan_commands_$sample.txt
EOF

((i++))
	done