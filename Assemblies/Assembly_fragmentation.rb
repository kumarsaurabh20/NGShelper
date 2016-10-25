#!/bin/ruby
#########################################################################################
# Copyright (C) 2014 Singh KS															
# Contact : kumar.saurabh@rothamsted.ac.uk												
# Assembly_fragmentation.rb                                                         	
#########################################################################################
# This program takes the scaffolds file in fasta format produced from any assembler. It	
# first merges all the scaffolds and creates a single big scaffold and then produce    	
# multiple 2.5kb fragments with 500 bp overlapping ends. The script is generated keeping
# hybrid assemblies in mind. The script was used to create 2.5kb overlapping reads    	 
# used in a hybrid assembly with ionTorrent reads (assembled using Newbler)           	
#                                                                                     	
#$ Assembly_fragments_generator.rb <Assembly_scaffold_file.fasta> <outfile_name>      	
#########################################################################################
# Author: Kumar Saurabh Singh                                                          	
# Date:   5th October 2015                                                            	
#########################################################################################

#============================VARIABLES DEFINITION===========================#
scaffolds = ARGV[0].to_s
outfile = ARGV[1].to_s
complete_assembly = ""

#===========================Function Definitions============================#

def file_write(outputFile, seqObject)
	puts "Writing final fragments to a fasta file..."
	File.open(outputFile.to_s, 'a') do |file|
		seqObject.each_with_index do |element, index|
			file.write ">OsmiaSEQ#{index}\n#{element}\n"
		end	
	end	
end

def file_read(seqObject, inputFile)
	puts "Reading Assembly file and merging it together..."
	sequence = seqObject.to_s

	File.open(inputFile.to_s, "r") do |f|
  		f.each_line do |line|

  			if line.match('>')
  				next
  			else
  				sequence.concat(line.chomp)
  			end	
  		end
	end
	return sequence
end

def fragment(mergedSequenceObject)
	puts "Generating overlapping fragments from the Assembly file..."
	arrayMap = Array.new
	k = 0 #initial value
	j = 2500 #initial value
	for i in 0..(mergedSequenceObject.length/2000).round 

			if arrayMap.empty? 
				arrayMap.push(mergedSequenceObject.slice(k..j))
				#puts "The value of K is #{k} and J is #{j}" 
				#puts arrayMap.inspect.to_s
			else
				arrayMap.push(mergedSequenceObject.slice(k..j))
				#puts "The value of K is #{k} and J is #{j}"
				#puts arrayMap.inspect.to_s
			end	
	k += 2000 
	j += 2000 #fragment length would be 1500bp since the initial value of is 1500
	end 
	return(arrayMap)
end	

#============================WORKFLOW=======================================#
merged_sequence = file_read(complete_assembly, scaffolds)
fragmentsContainer = fragment(merged_sequence)
file_write(outfile, fragmentsContainer)
#===========================OUTPUT==========================================#
puts "\n"
puts "The merged sequence length is #{merged_sequence.length}"
puts "\n"
puts "Total number of fragments generated are #{fragmentsContainer.size}"
puts "\n"
puts "Done!!"
puts "\n"
string = %{
ATAGAGATGATAGACAGATAGACAGTAGACAGATAGACAGTAGACAGATAGACAGTAGACAGATAGACAGATAGCAGATAGACAGATACAGATAGACAGTAGACAGATAGA
ATAGAGATGATAGACAGATAG 
               AGATAGACAGTAGACAGATAG 
                              AGATAGACAGTAGACAGATAG
                                             AGATAGACAGTAGACAGATAG
                                                            AGATAGACAGATAGCAGATAG
                                                                          AGATAGACAGATACAGATAGA
                                                                                         GATAGACAGTAGACAGATAGA 
}  

puts "Generated fragments look like this..."
puts "\n"
puts string
puts "\n"  
puts "Good Bye!!"                                                                                                                                                                            
