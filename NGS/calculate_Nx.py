#!/usr/bin/env python
"""
Usage:python calculate_Nx.py <fasta_file> <minimum_length> <Nx>
The script takes a fasta file with minium sequence to consider and Nx. The default minimum sequence is 0 and Nx is N50.
"""

from __future__ import (print_function, division)
from Bio import SeqIO
import sys, getopt
import numpy

__author__ = 'Kumar'

fasta_file = ''
min_length = int(0)
nf = int(50)
fasta_list = []
nCount = 0

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
				ncount = str(s.seq).lower().count('n')
				nCount += ncount
			else:
				continue
		else:
			fasta_list.append(str(s.seq))  
except IOError:
	print("Usage::python calculate_Nx.py -f 'fasta file' -l 'minimum length' -n Nx")
	sys.exit(2)
  
#fasta_list.sort(lambda x,y: cmp(len(y),len(x)))
fasta_list.sort(key=len, reverse=True)
fasta_str = "".join(fasta_list)
tot_length = len(fasta_str)
nf_length = nf * tot_length/100
temp_nf_list = []
temp_sum = int(0)
nCount_rounded = round(nCount,2)

#Calculate other sequence stats
shortest = len(fasta_list[-1])
largest = len(fasta_list[0])
GC_content = round(float((fasta_str.lower().count('g') + fasta_str.lower().count('c'))) / (tot_length - nCount) * 100,2)
GC_rounded = round(GC_content,2)
mean_len = numpy.mean([len(x) for x in fasta_list])
median_len = numpy.median([len(x) for x in fasta_list])
#Calculate N50 and L50
count = 0
for e in fasta_list:
	temp_nf_list.append(e)
	temp_sum += len(e)
	if temp_sum >= nf_length:
		n50 = int(len(e))
		l50 = count
		break
	else:
		count += 1
		continue 

print(" ")
print("########## Assembly Stats  ##########")
print(" ")
print("N%i: %i" %(nf,n50))
print(" ")
print("L%i: %i" %(nf,l50))
print(" ")
print("Shortest seq: %i" %(shortest))
print(" ")
print("Longest seq: %i" %(largest))
print(" ")
print("Mean length: %i" %(mean_len))
print(" ")
print("Median length: %i" %(median_len))
print(" ")
print("Total sequences: %i" %(len(fasta_list)))
print(" ")
print("Total bases: %i" %(tot_length))
print(" ")
print("GC content: %.2f" %(GC_content))
print(" ")
print("# of Ns: %.2f" %(nCount))
print(" ")
print("Total ungapped length: %.2f" %(tot_length - nCount))
print("#########################################")
print(" ")
