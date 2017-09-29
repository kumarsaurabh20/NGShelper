#!/usr/bin/env python2
######################################
#GFF utility functions
######################################
#Author: Kumar Saurabh Singh
#Date: 28th September 2017
#ks575@exeter.ac.uk
######################################
from __future__ import print_function
from Bio import SeqIO
import gzip
import sys

def readFile(gff):
	if gff.lower().endswith(".gff"):
		row = open(gff, "r")
	elif gff.lower().endswith(".gff3"):
		row = open(gff, "r")
	elif gff.lower().endswith(".gz"):
		row = gzip.open(gff, "r")
	else:
		print "File is not gff!!"
		sys.exit(1)
	return row

#extract introns for a specified list of genes or a new gff with all introns.	
def extractIntronsForGene(gene_list):

#filter gff based on number of exons (for instance, filter all genes with single exon or multi-exon) 
def gffExtractSingleExon(gffDict, prefix = out):
	if isinstance(gffDict, dict):
		outfile = "%s.gff"%(prefix)	
		out = open(outfile, "a")
		for k, v in gffDict.iteritems():
        		if isinstance(v, dict):
                		for x, y in v.iteritems():
                        		if isinstance(y, dict):
                                		if gffDict[k][x]['exons'] == 1:
                                        		out.write("%s\tGFF_Util\tmRNA\t%d\t%d\t.\t%s\t.\tID=%s;Name=GFF_Util_prediction\n"%(k,int(gffDict[k][x]['start']),int(gffDict[k][x]['end']), gffDict[k][x]['strand'], x))
                                        		if not gffDict[k][x]['cdsStarts']:
                                                		continue
                                        		else:
                                                		out.write("%s\tGFF_Util\tCDS\t%d\t%d\t.\t%s\t.\tID=%s.cds;Parent=%s;Name=GFF_Util_prediction\n"%(k, int(''.join(str(x) for x in gffDict[k][x]['cdsStarts'])), int(''.join(str(x) for x in gffDict[k][x]['cdsEnds'])), gffDict[k][x]['strand'], x, x))
                                		else:
                                        		continue
		out.close

#extract all genes with multiple transcripts based on the locus. (Gene1 -> mRNA1 + mRNA2.......)
#write a fasta file with spliced exons for each GFF transcript
#write a fasta file with spliced CDS for each GFF transcript
def extractSplicedTranscripts(gffDict):

#check which genes are missing from A based on comparison with B
def gffIntersect(gffDict1, gffDict2):

#write a protein fasta file with the translation of CDS for each record
def translateCDSFasta(gff, fasta_file)

#discard multi-exon mRNAs that have any intron with a non-canonical splice site consensus (i.e. not GT-AG, GC-AG or AT-AC)

#discard any mRNAs that either lack initial START codon or the terminal STOP codon, or have an in-frame stop codon (only print mRNAs with a fulll, valid CDS)

#Report any mRNAs with CDS having in-frame stop codons

#expose (warn about) duplicate transcript IDs and other potential problems with the given GFF/GTF records

#replace IDs using the map file
def mapIDs(feature = "mRNA", mapFile):

#checking if CDS contains any stop codon
def countStops(cds, includeTerminal=False):
	if includeTerminal:
		triplets = [cds[i:i+3] for i in range(len(cds))[::3]]
	else:
		triplets = [cds[i:i+3] for i in range(len(cds)-3)[::3]]
	stopCount = len([t for t in triplets if t in set(["TAA","TAG","TGA"])])
	return stopCount
#
def parseGFF(gff):
	description = lambda desc: dict([x.split("=") for x in desc.strip(";").split(";")])
	mainHash = {}
	lines = readFile(gff)
	for line in lines:
		if len(line) > 1 and line[0] != "#":
			elements = line.split()
			#store all mRNA and CDS data for the particular scaffold
			scaffold = elements[0]
			if scaffold not in mainHash.keys():
				mainHash[scaffold] = {}
			if elements[2] == "mRNA" or elements[2] == "mrna" or elements[2] == "MRNA":
				#we've found a new mRNA
				try: mRNA = description(elements[-1])["ID"]
				except:
					print elements[-1]
					raise ValueError("Problem in parsing mRNA information.")
				if mRNA not in mainHash[scaffold].keys():
					mainHash[scaffold][mRNA] = {'start':int(elements[3]), 'end':int(elements[4]), 'strand':elements[6], 'exons':0, 'cdsStarts':[], 'cdsEnds':[], '5UTR_start':[], '5UTR_end':[], '3UTR_start':[], '3UTR_end':[]}
			elif elements[2] == "CDS" or  elements[2] == "cds":
				#we're reading CDSs for an existing mRNA
				mRNA = description(elements[-1])["Parent"]
				start = int(elements[3])
				end = int(elements[4])
				mainHash[scaffold][mRNA]['exons'] += 1
				mainHash[scaffold][mRNA]['cdsStarts'].append(start)
				mainHash[scaffold][mRNA]['cdsEnds'].append(end)
			elif elements[2] == "five_prime_utr" or elements[2] == "5_prime_utr" or elements[2] == "5_PRIME_UTR":
				mRNA = description(elements[-1])["Parent"]
				start = int(elements[3])
                        	end = int(elements[4])
                        	mainHash[scaffold][mRNA]['5UTR_start'].append(start)
                        	mainHash[scaffold][mRNA]['5UTR_end'].append(end)
			elif elements[2] == "three_prime_utr" or elements[2] == "3_prime_utr" or elements[2] == "3_PRIME_UTR":
				mRNA = description(elements[-1])["Parent"]
                        	start = int(elements[3])
                        	end = int(elements[4])
                        	mainHash[scaffold][mRNA]['3UTR_start'].append(start)
                        	mainHash[scaffold][mRNA]['3UTR_end'].append(end)
	print mainHash
	return mainHash

def createFastaDict(fasta_file):
	fasta_dict = {}
	for s in SeqIO.parse("myzus.fasta", "fasta"):
		fasta_dict[s.id] = str(s.seq)
	return fasta_dict

def extractSeqsFromFasta(gff, fastaFile, feature = "mRNA", prefix = "out"):
	parsedGff = parseGFF(gff)
	fastaDict = createFastaDict(fastaFile)
	#s = s[ beginning : beginning + LENGTH]
	outfile = "%s.fasta"%(prefix)	
	out = open(outfile, "a")
	for k, v in mainHash.iteritems():
        	if isinstance(v, dict):
                	for x, y in v.iteritems():
                        	if isinstance(y, dict):
                                	if feature == "mRNA":
                                        	start = int(mainHash[k][x]['start']) - 1
                                        	end = int(mainHash[k][x]['end']) - 1
                                        	length = end - start
                                        	scaffold = fastaDict[k]
                                        	seq = scaffold[start : start + length]
                                        	out.write(">%s %s\n"%(x, k))
                                        	out.write("%s\n"%(seq))
					elif feature == "CDS":
						

	out.close()
	print("%s feature fasta file, %s, is generated"%(feature, outfile))
	









