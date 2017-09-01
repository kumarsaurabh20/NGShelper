from __future__ import print_function
from Bio import SeqIO
import sys,getopt

__author__ = 'Kumar'
__desc__ = 'Kmer counter'

fasta_file = ''
kmer = 0
outfile = ''
try:
	myopts, args = getopt.getopt(sys.argv[1:], "f:k:o:")
	for o, a in myopts:
		if o == "-f":
			fasta_file = str(a)
		if o == "-k":
			kmer = int(a)
		if o == "-o":
			outfile = str(a)

except getopt.GetoptError as e:
	print(str(e))
	print("Usage: %s -f <fasta file> -k <kmer length> -o <outfile>" %(sys.argv[0]))
	sys.exit(2)

fasta_list = []
kmer_hash = {}
try:
	for s in SeqIO.parse(fasta_file, "fasta"):
		fasta_list.append(str(s.seq))
except IOError:
	print("Usage: %s -f <fasta file> -k <kmer length> -o <outfile>" %(sys.argv[0]))
	sys.exit(2)

fasta_list.sort(cmp=lambda x,y: cmp(len(y),len(x)))				
fasta_str = str("".join(fasta_list))

for i in range(0, len(fasta_str) - kmer + 1):
	temp = fasta_str[i:i+kmer]
	if temp in kmer_hash:
                kmer_hash[temp] += 1
        else:
                kmer_hash[temp] = 1

count = 0
f = open(outfile, 'w')
for key, value in kmer_hash.iteritems():
	if count == 0:
		f.write("Distinct_Kmer\tFrequency\n")
		f.write("%s\t%i\n" %(key, value))
		count += 1
	else:
		f.write("%s\t%i\n" %(key, value))
f.close
print("%i distict K-mers were found. Check the output file!!"%(len(kmer_hash)))
