import pandas as pd
import sys
from optspec import Options

"""
Usage:python geneAnnoFromSnps.py --snps <snp file> --gff3 <gff3 file>
The script takes a snp file in a vcf format and a gff3 file for single chromosomes. It uses SNP coordinates to fetch genes overlapping the SNP. 
The VCF file has to be filterd and retain only coordinates and id information along with the chromosome. You can do it using the command awk '{print $1, $2, $3}' test.vcf > test2.vcf

Author: Kumar Saurabh Singh (ks575@exeter.ac.uk)
"""

try:
    optmap, args = ( Options()
        .opt('g', 'gff3', required = True)
        .opt('s', 'snp', required = True)
        .parse() )

except Exception as e:
   print("Unexpected error: {0}".format(e))
   print("Usage:: %s python geneAnnoFromSnps.py --snp '<path>/test2.vcf' --gff3 '<path>/chr2.gff3'" % sys.argv[0])
   sys.exit(2)


print(optmap['gff3'])

try:
#import vcf file with all the SNPs
    snpcode = pd.read_table(optmap['snp'], comment="#", sep = "\t", names = ['seqname', 'location', 'snpid'])
    print(snpcode.head())
except Exception as e:
    print("Unexpected SNP File input error: {0}".format(e))
    print("File should be in a vcf format. Use selected SNPs only." % sys.argv[0])
    sys.exit(2)

try:
#import the gff3 file
    gencode = pd.read_table(optmap['gff3'], comment="#", sep = "\t", names = ['seqname', 'source', 'feature', 'start' , 'end', 'score', 'strand', 'frame', 'attribute'])
    print(gencode.head())

    #filter the gff3 file for only genes
    gencode_genes = gencode[(gencode.feature == "gene")][['seqname', 'start', 'end', 'attribute']].copy().reset_index().drop('index', axis=1) # Extract genes
except Exception as e:
    print("Unexpected GFF3 file input error: {0}".format(e))
    print("Use GFF3 formatted file." % sys.argv[0])
    sys.exit(2)

try:
    for index_label, row_series in gencode_genes.iterrows():
        gencode_genes.at[index_label , 'attribute'] = row_series['attribute'].split(";")[0].split("=")[1]

    def gencode_all_known_genes(a, tb):
        product = []
        for region in tb.itertuples(index=False, name='GFF'):
            start = int(region[1])
            end = int(region[2])
            gene = region[3]
            if int(a['location']) >= start and int(a['location']) <= end:
                product.append(gene)
        if len(product) > 0:
            return("".join(product))
        else:
            return("NA")

    snpcode['genes'] = snpcode.apply(lambda x: gencode_all_known_genes(x[['seqname', 'location']], gencode_genes), axis=1)

    print(snpcode.head(100))

except Exception as e:
    print("Unexpected logic error: {0}".format(e))
    sys.exit(2)