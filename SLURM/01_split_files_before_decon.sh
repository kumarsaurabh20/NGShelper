####### Script to this automatically ###
#!/bin/bash
decondir=/home/ISAD/mds207/adela_data/merged/decon
merged_dir=/home/ISAD/mds207/adela_data/merged
split_dir=$merged_dir/split_files
cd $merged_dir
echo "##############################################################"
echo "We have the following merged samples in this directory:"
ls -1 *.fasta | cut -c1-11 | sort -u
echo "##############################################################"
NFiles=$(ls -1 *.fasta | cut -c1-11 | sort -u | wc -l)
echo " As per the above list, you have $NFiles files."
read -p "Press [Enter] key to continue..."
echo ""
echo "now we will split all these files into 5 pieces each to"
echo "allow processing via multiple jobs on the cluster"
mkdir -p split_files
cd split_files
for file in $( ls -1 $merged_dir/*R12*.fasta )
do
echo "splitting file $file...."
perl ../splitFasta.pl -verbose -i $file -n 5 
echo "............................................."
done
# Files did not get created in the split_files directory. Perhaps the perl script
# needs to be moved inside? Anyway, lets move the buggers..
#
mv *_c?.fasta /home/ISAD/mds207/adela_data/merged/split_files