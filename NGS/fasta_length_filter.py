"""
Usage: python fasta_length_filter.py -f <fasta file> -l <length>
The script returns all the sequences with length greator than or equal to user specified length
"""
from __future__ import print_function
import sys
from Bio import SeqIO

fasta_file = ''
min_length = 1000

try:
   myopts, args = getopt.getopt(sys.argv[1:],"f:l:")
except getopt.GetoptError as e:
   print(str(e))
   print("Usage:: %s -f 'fasta file' -l 'minimum length'" % sys.argv[0])
   sys.exit(2)   
for o, a in myopts:
   if o == '-f':
      fasta_file = str(a)
   elif o == '-l':
      min_length = int(a)
try:
	for s in SeqIO.parse(str(fasta_file), "fasta"):
		if len(s.seq) >= int(min_length):
			print("%s%s" %(">",s.id))
			print(s.seq)
		else:
			next
except IOError:
	print("Usage:: %s -f 'fasta file' -l 'minimum length'" % sys.argv[0])	
