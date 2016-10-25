"""
Usage: python fasta_length_filter.py <fasta file> <length>
The script returns all the sequences with lenth greator than and equal to user specified length
"""
from __future__ import print_function
import Bio, sys
from Bio import SeqIO

fasta_file = str(sys.argv[1])
#print(fasta_file)
seq_length = int(sys.argv[2])
#print(seq_length)

for s in SeqIO.parse(fasta_file, "fasta"):
	if len(s.seq) >= seq_length:
		print("%s%s" %(">",s.id))
		print(s.seq)
	else:
		next

	
