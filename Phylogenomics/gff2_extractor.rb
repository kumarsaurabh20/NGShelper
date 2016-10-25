##########################################################################################
# Copyright (C) 2014 Singh KS                                                            #
# Contact : kumarsaurabh20@gmail.com                                                     #
# 									                 #             
# This file is part of PhyloGenomica package	                 			 #
# 									                 #
# PhyloGenomica is free software: you can redistribute it and/or modify                  #
# it under the terms of the GNU General Public License as published by	                 #
#  the Free Software Foundation, either version 3 of the License, or	                 #
# (at your option) any later version.					                 #
# 									                 #
# PhyloGenomica is distributed in the hope that it will be useful,	                 #
# but WITHOUT ANY WARRANTY; without even the implied warranty of	                 #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the		                 #
# GNU General Public License for more details.				                 #
# 									                 #
# You should have received a copy of the GNU General Public License	                 #
# along with PhyloGenomica.  If not, see <http://www.gnu.org/licenses/>.                 #
##########################################################################################

##########################################################################################
# gff2_extractor.rb                                             			 #
##########################################################################################
# This script takes a .gff2 file and extracts CDS/protein sequences out of it. It can    #
# retrieve any region out of the gff2 file with some modification.                       #
##########################################################################################
# Author: Kumar Saurabh Singh                                                            #
# Date  : 15th July 2014                                                                 #
##########################################################################################

class ReadGff

require 'rubygems'
require 'progressbar'
#require 'ruby-progressbar'

	def getProtein
		  start = []
		  endl = []
           in_file = ARGV[0].to_s       
		  begin

		    File.open(in_file).each do |line|
                           
		           if line.start_with?("##Protein")
		            dummy = $.  
		            start.push(dummy) 		             		    
			   elsif line.start_with?("##end-Protein")
		              mummy = $.
			      endl.push(mummy)
			   else
		              next
			   end
                         
		       end
		   getOutput(start, endl, in_file, "Protein")
		   rescue Exception => e
		          e.message
		   end
	end

       def getOutput(start_line, end_line, file, pattern)
	
                begin
                bar = ProgressBar.new("Writing Out", 3500)			         
	           count = start_line.length
                   
		    File.open("output.fasta", "w+") do |file|
     			  for i in 0..count 
                           
			   file.write `sed -n '#{start_line[i]},#{end_line[i]}p' halochloris_unmapped.fasta.gff | sed s/^##// | sed '/^end-Protein/ d' | sed 's/^Protein/\>Protein/'`
                             
                            if i < count
                              bar.inc
                            else
                              bar.finish
                            end                              
                   
		          end
                       
                  end
                               		
		rescue Exception => e
			e.message
		end		
   
           puts "#{pattern } fasta file is created successfully on" + " " + File.stat("output.fasta").mtime.to_s  
              
	end

end


read = ReadGff.new
read.getProtein





#f = File.new("hellousa.rb") 
#f.seek(12, IO::SEEK_SET)  
#print f.readline  
#f.close  
#Ruby supports the notion of a file pointer. The file pointer indicates the current location in the file. The File.new #method opens the file 'hellousa.rb' in read-only mode (default mode), returns a new File object and the file pointer is #positioned at the beginning of the file. In the above program, the next statement is f.seek(12, IO::SEEK_SET). The seek #method of class IO, moves the file pointer to a given integer distance (first parameter of seek method) in the stream #according to the value of the second parameter in the seek method.
#
#IO::SEEK_CUR - Seeks to first integer number parameter plus current position
#IO::SEEK_END - Seeks to first integer number parameter plus end of stream (you probably want a negative value for first #integer number parameter)
#IO::SEEK_SET - Seeks to the absolute location given by first integer number parameter
