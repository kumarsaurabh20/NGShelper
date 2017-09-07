#!/bin/bash
###########################################
# Copyright (C) 2017 Singh KS															
# Contact : k.saurabh-singh@exeter.ac.uk												
# Sample wise mean Fst Matrix                                             	
###########################################
#
fstfile=$1
#echo "$fstfile"
samples=$2
#echo "$samples"
declare -A matrix
#declare -A VALUES
#
num_rows=$samples
num_columns=$samples
#
total_cells=$(($samples**2/2-$samples/2))
echo "$total_cells"
range=$(($total_cells + 5))
#val=$total_cells - 1
#
#Filter the fst file by removing intial 5 colums and retaining all the comparison
cut -f6-$range $fstfile > filtered.fst
file="filtered.fst"
#
function ProgressBar {
        let _progress=(${1}*100/${2}*100)/100
        let _done=(${_progress}*4)/10
        let _left=40-$_done
        _done=$(printf "%${_done}s")
        _left=$(printf "%${_left}s")
printf "\rProgress : [${_done// /#}${_left// /-}] ${_progress}%%"
}
#
y=1
for ((i=1;i<=num_rows;i++)) do
    #echo "this is outer loop"
    for ((j=1+$i;j<=num_columns;j++)) do
	ProgressBar $y $total_cells
	#echo "this is inner loop"			
 	mean=`cut -f $y $file | cut -d '=' -f 2 | awk '{ total += $1 } END { print total/NR }' -`
	#echo "mean for cell $y: $mean"
 	matrix[$i,$j]=$mean
 	y=$(($y+1))
    done
done
#
f1="%$((${#num_rows}+1))s"
f2=" %9s"
#printf "$f1" ''
echo
for ((i=1;i<=num_rows;i++)) do	
    printf "$f2" $i
done
echo
#
for ((j=1;j<=num_columns;j++)) do
    printf "$f1" $j
    for ((i=1;i<=num_rows;i++)) do
        printf "$f2" ${matrix[$i,$j]}
    done
    echo
done
