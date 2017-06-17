#!/usr/bin/ruby

###################################
#This script was written to create a Name ID and description of gene in to two separate columns.
#Ususally the gff file contains the geneID under the description column and this gene ID is different from the scaffold ID.
#To create a n input for this scriptm just extract the description column i.e. column 9 and to a new file.
#The new file is just a one column file with gff3 description. Feed the file in to this script and the script will create 
# a new file with gene name in column 1 and description/functional annotation in column 2.
#
# USAGE: ruby fetchIDs.rb <file.list>
###################################
def fetchIDs

	File.open(ARGV[0].to_s, "r") do |file|

		
		book = Hash.new

		file.each_line do |line|

			container = Array.new

			if line.include? "Name"

				container = line.split(";")
				container.map { |e| book["#{e.gsub!("Name=", "")}"] = line if e.include? "Name=" } 

			else
				next
			end	
		end

		#puts book.inspect
		file_write("Helicoverpa.out", book)
	end		
end		

def file_write(outputFile, seqObject)
			
	puts "Writing final data to a list file..."
			
	File.open(outputFile.to_s, 'a') do |file|
				
		seqObject.each_pair do |key, value|
				
		file.write "#{key}\t#{value}\n"
				
		end				
	end	
end

fetchIDs