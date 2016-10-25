######################################################################################
#create_substitution_matrix.rb
######################################################################################
#Author: Kumar Saurabh Singh
#Date: 28th July 2014
######################################################################################

require 'bio'
require 'matrix'

# Reads in a ClustalW-formatted multiple sequence alignment
# from a file named "infile_clustalw.aln" and stores it in 'report'.
report = Bio::ClustalW::Report.new(File.read('test_clustal_file.aln'))

# Accesses the actual alignment.
msa = report.alignment.to_a

#giving a symbol to spaces in concensus as hash 
concensus = report.match_line.gsub(/\s/m, '#')

#add concensus symbol on original alignment array
msa.push(concensus)

new_msa = []

#putting individual element in new array
 msa.each do |e|
    new_msa.push(e.split(""))
 end

#creating a matrix with row vectors as individual sequences with gaps and concensus symbols
msaMat = Matrix.rows(new_msa)

#converting rows of sequences in to columns of bases
msa_column = msaMat.transpose
puts msa_column.inspect







######################################################################################
#File.open("output.aln", "a") {|e| e.write(msa.to_a)}
##output fasta formatted out alignment
##puts msa.output_fasta
#seq = report.get_sequence(0)
#header = report.header
#concensus = report.match_line
#puts seq
#puts msa
#returns an Bio aligment object
#<Bio::Alignment::OriginalAlignment:0x0000000184b290>
# Goes through all sequences in 'msa' and prints the
# actual molecular sequence.
#msa.each do |entry|
 # puts entry.seq
  #File.open("output.aln", "a") {|e| e.write(entry.seq)}
#end
#puts concensus
######################################################################################
