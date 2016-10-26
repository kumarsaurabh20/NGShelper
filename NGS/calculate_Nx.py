"""
Usage:python calculate_Nx.py <fasta_file> <minimum_length> <Nx>
The script takes a fasta file with minium sequence to consider and Nx. The default minimum sequence is 0 and Nx is N50.
"""

from __future__ import (print_function, division)
from Bio import SeqIO
import sys

fasta_list = []
fasta_file = str(sys.argv[1])
min_length = int(sys.argv[2])
nf = int(sys.argv[3])

for s in SeqIO.parse(fasta_file, "fasta"):   
         if min_length:   
            if len(s.seq) >= min_length:
               fasta_list.append(str(s.seq))
            else:
               next
         else:
            fasta_list.append(str(s.seq))   
  
fasta_list.sort(cmp=lambda x,y: cmp(len(y),len(x)))

fasta_str = "".join(fasta_list)
tot_length = len(fasta_str)
nf_length = nf * tot_length/100
temp_nf_list = []
temp_sum = 0

for e in fasta_list:
	temp_nf_list.append(e)
	temp_sum += len(e)
	if nf_length >= temp_sum:
		next
	else:
		nf_seq = int(len(e))
		break

print("N50: %i" %(nf_seq))
print("#Sequences: %i" %(len(fasta_list)))
print("Total bases: %i" %(tot_length))
