#!/usr/bin/env python2
##############################################
#Convert gff to bed with IDs in 4th column
##############################################
#Author: Kumar Saurabh Singh
#Date: 27th September 2017
#ks575@exeter.ac.uk
##############################################
from __future__ import print_function
import gzip
import os, sys, getopt
#
gff_file = ""
prefix = ""
#
if len(sys.argv) == 1:
        print("No arguments were passed. Try again!!")
        sys.exit(1)
#
try:
	myopts, args = getopt.getopt(sys.argv[1:],"g:p:")
	for o, a in myopts:
		if o == '-g':
			gff_file = str(a)
		elif o == '-p':
			prefix = str(a)
		#else:
			#print("Usage:: %s -g <gff_file> -p <Out file prefix>" % sys.argv[0])
except getopt.GetoptError as e:
	print(str(e))
	print("Usage:: %s -g <gff_file> -p <Out file prefix>" % sys.argv[0])
	sys.exit(1) 
#
def readFile(gff):
	if gff.lower().endswith(".gff"):
		row = open(gff, "r")
	elif gff.lower().endswith(".gff3"):
		row = open(gff, "r")
	elif gff.lower().endswith(".gz"):
		row = gzip.open(gff, "r")
	else:
		print("File is not gff!!")
		sys.exit(1)
	return row
#
description = lambda e: dict([x.split("=") for x in e.strip(";").split(";")])
lines = readFile(gff_file)
outfile = "%s.bed"%(prefix)
out = open(outfile, "w")
mRNA = ""
for line in lines:
	if len(line) > 1 and line[0] != "#":
		elements = line.split()
		#store all mRNA and CDS data for the particular scaffold
		if elements[2] == "mRNA" or elements[2] == "mrna" or elements[2] == "MRNA":
			#we've found a new mRNA
			try: mRNA = description(elements[-1])["ID"]
			except:
				print(elements[-1])
				raise ValueError("Problem in parsing mRNA information.")
		out.write("%s\t%d\t%d\t%s\n" %(elements[0], int(elements[3]), int(elements[4]), mRNA))
out.close()
print("Sorting bed file....")
cmd = "sort -k1,1 -k2,2n %s.bed > %s.sorted.bed"%(prefix, prefix)
os.system(cmd)
cmd = "rm %s.bed"%(prefix)
os.system(cmd)
print("Bed file is created as %s.sorted.bed"%(prefix))
