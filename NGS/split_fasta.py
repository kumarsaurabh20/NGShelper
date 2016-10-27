from __future__ import (print_function, division)
from Bio import SeqIO
import sys, getopt

__author__ = 'Kumar'
__desc__ = 'Split a multi fasta file into individual sequence files.'

prefix = ''
fasta_file= ''
count = 0
try:
	myopts, args = getopt.getopt(sys.argv[1:], "f:p:")
	for o, a in myopts:
		if o == "-f":
			fasta_file = str(a)
		elif o == "-p":
			prefix = str(a)
except getopt.GetoptError as e:
	print(str(e))
	print("Usage:%s -f <fasta file> -p <prefix>" % sys.argv[0])
	sys.exit(2)

try:
	for s in SeqIO.parse(fasta_file, "fasta"):
		count += 1
		SeqIO.write(s, "%s_%i.fasta"%(prefix,count), "fasta")
except IOError:
	print("Usage:python split_fasta.py -f <fasta file> -p <prefix>")
	sys.exit(2)

print("%i files have been written Successfully." %(count))
