#!/usr/bin/env python2

from __future__ import print_function
from Bio import SeqIO
import sys, vcf, getopt

__author__ = 'Kumar'

sample_number = int(0)
vcf_file = ''
a = int(0)
x = int(0)
n = int(0)
position = int(0)
fold = int()

try:
	myopts, args = getopt.getopt(sys.argv[1:],"f:s:")
	for o, a in myopts:
		if o == '-f':
			vcf_file = str(a)
		elif o == '-s':
			sample_number = int(a)
except getopt.GetoptError as e:
	print(str(e))
	print("Usage:: %s -f <vcf_file> -s <sample index in case of multi-sample vcf file>" % sys.argv[0])
	sys.exit(2)   

vcf_reader = vcf.Reader(open(vcf_file, 'r'))
sf = open("outfile.sf", "w")
for record in vcf_reader:
	#print(record.samples)
	position = record.POS
	ad = record.samples[sample_number]['AD']
	#print(ad)
	if ad == None:
		continue
	else:
		a = ad[0]
		x = ad[1]
		#print("%s::::%s"% (a,x)) 
        
	n = a + x
	if a > x:
		fold = 0
	else:
		fold = 1
	header = "location\tx\tn\tfolded\n"
	
	if sf.tell() == 0:
		sf.write(header)
		sf.write("%d\t%d\t%d\t%d\n"% (position, x, n, fold))
	else:
		sf.write("%d\t%d\t%d\t%d\n"% (position, x, n, fold))
sf.close()
