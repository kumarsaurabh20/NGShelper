#!/usr/bin/env python2
from __future__ import (print_function, division)
from Bio import SeqIO
import sys, os, textwrap, getopt

__author__ = 'Kumar'
__desc__ = 'This scripts reads a fasta file and wraps the sequences in to any input line width (Default is 60 characters per line).'

width = int(60)
fasta_file = ''
outfile = ''

try:
	myopts, args = getopt.getopt(sys.argv[1:], "f:w:o:")
	for o, a in myopts:
		if o == "-f":
			fasta_file = str(a)
		elif o == "-w":
			width = int(a)
		elif o == "-o":
			outfile = str(a)

except getopt.GetoptError as e:
	print(str(e))
	print("Usage: %s -f <fasta file> -w <character width> -o <outfile>"%(sys.argv[0]))
	sys.exit(2)	
try:
	f = open(outfile, "w")
	for s in SeqIO.parse(fasta_file, "fasta"):
		f.write(">%s\n"%(s.id))
		f.write("%s\n"%(textwrap.fill(str(s.seq), width)))
	f.close
except IOError:
	print("Usage: %s -f <fasta file> -w <character width> -o <outfile>"%(sys.argv[0]))
	sys.exit(2)
print("Finished wrapping!!")
