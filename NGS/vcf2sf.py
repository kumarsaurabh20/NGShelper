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

#file = vcf.Reader(open('test.vcf','r'))
#record = next(file)
#print(record.INFO['DP'])
#print(record.samples)

#vcf_reader = vcf.Reader(open(r'path\to\zebrafish.vcf', 'rb'))
#for record in vcf_reader:
#	for call in record.samples:
#		if call.sample=='TUB' or call.sample=='TA':
#			if call.gt_nums != '0/0':
#				print call.gt_nums

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
		
	

	#print(isinstance(ad, list))
	#print(record.FORMAT)	
	#print(record.genotype('LIB15046').data[0:]) #worked for getting sample specific information but the list is unordered/not constant
	#for sample in record.samples:
		#print(sample)

