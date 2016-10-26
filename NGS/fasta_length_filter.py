"""
Usage: python fasta_length_filter.py <fasta file> <length>
The script returns all the sequences with lenth greator than and equal to user specified length
"""
from __future__ import print_function
import sys
from Bio import SeqIO


for s in SeqIO.parse(str(sys.argv[1]), "fasta"):
	if len(s.seq) >= int(sys.argv[2]):
		print("%s%s" %(">",s.id))
		print(s.seq)
	else:
		next
	
