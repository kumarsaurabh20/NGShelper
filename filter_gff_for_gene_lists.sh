#!/bin/bash
#
# @author  Kumar Saurabh Singh
# @update  22nd May 2017
# @license GNU GPL -v 3.0
#

if [[ ! $2 ]] ; then
   echo "
.DESCRIPTION
   Filters the GFF file based on gene list file(s).
   The script works ok with multiple list file.
   If you have a multiple list file, just provide an extension
   (tsv|tab|csv). The list file can be of single column with no
   headers. You can also provide single gene list file.

.USAGE
   $0 genome.gff tsv

   genome.gff	Complete genome gff file.
   tsv		file extension.
";
   exit 1;
fi

if [[ ! -r $1 ]]; then
   echo "Cannot open file: $1";
   exit 1;
fi

ext=$2
for each in *.$ext; do
	list="`echo "$each" | cut -d'.' -f1`"
	mkdir "$list"
	while read id ; do
		val="`echo "$id" | cut -d$'\r' -f1`"
		grep $val $1 > ${val}.gff
	done <$each
	#echo "Finished creating individual GFF for each gene in the list!"
	mv Ha* $list
	#echo "Moved all gffs in the list folder!"
	cat ./$list/*.gff > ./$list/$list.gff
	echo "Generated a merged GFF file for $list!"
	rm ./$list/Ha*;
done
