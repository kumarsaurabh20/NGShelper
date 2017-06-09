#!/usr/bin/env python2
"""
Usage:python calculate_Nx.py <fasta_file> <minimum_length> <Nx>
The script takes a fasta file with minium sequence to consider and Nx. The default minimum sequence is 0 and Nx is N50.
"""

from __future__ import (print_function, division)
from Bio import SeqIO
import sys, getopt

__author__ = 'Kumar'

fasta_file = ''
min_length = int(0)
nf = int(50)
fasta_list = []

try:
	myopts, args = getopt.getopt(sys.argv[1:],"f:l:n:")
	for o, a in myopts:
		if o == '-f':
			fasta_file = str(a)
		elif o == '-l':
			min_length = int(a)
		elif o == '-n':
			nf = int(a)
#N50
except getopt.GetoptError as e:
   print(str(e))
   print("Usage:: %s -f 'fasta file' -l 'minimum length' -n Nx" % sys.argv[0])
   sys.exit(2)   

try:
	for s in SeqIO.parse(fasta_file, "fasta"):   
		if min_length:   
			if len(s.seq) >= min_length:
				fasta_list.append(str(s.seq))
			else:
				continue
		else:
			fasta_list.append(str(s.seq))   
except IOError:
	print("Usage::python calculate_Nx.py -f 'fasta file' -l 'minimum length' -n Nx")
	sys.exit(2)
  
fasta_list.sort(cmp=lambda x,y: cmp(len(y),len(x)))

fasta_str = "".join(fasta_list)
tot_length = len(fasta_str)
nf_length = nf * tot_length/100
temp_nf_list = []
temp_sum = int(0)

for e in fasta_list:
	temp_nf_list.append(e)
	temp_sum += len(e)
	if temp_sum >= nf_length:
		nf_seq = int(len(e))
		break
	else:
		continue 

print("N%i: %i" %(nf,nf_seq))
print("#Sequences: %i" %(len(fasta_list)))
print("Total bases: %i" %(tot_length))
