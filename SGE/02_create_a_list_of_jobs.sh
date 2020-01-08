####### Script to this automatically ###
#!/bin/bash
basedir=/home/ISAD/mds207/adela_data
merged_dir=$basedir/merged
split_dir=$merged_dir/split_files
decondir=$merged_dir/decontaminate
cd $merged_dir
echo "--------------------------------------------------------------------------"
mkdir -p logs
mkdir -p joblist
mkdir -p $decondir
if [ -f joblist/jobs.txt ] ; then
echo "an earlier version of $merged_dir/joblist/jobs.txt was found"
echo "deleting it before proceeding further"
rm -f joblist/jobs.txt
fi
echo "--------------------------------------------------------------------------"
cd $split_dir
for file in $( ls -1 *fasta_c?.fasta )
do
echo "deconseq -f $file -dbs hsref,hsalt1,hsalt2 -out_dir $decondir -i 97 -c 90" >> $merged_dir/joblist/jobs.txt
# echo "Currently processing command for $file"
done
read -p "Press [Enter] key to see the new job list..."
cat $merged_dir/joblist/jobs.txt
echo "----------------------------------"
echo "All Done... proceed to step three "
echo "----------------------------------"
