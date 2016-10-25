##########################################################################################
# Copyright (C) 2014 Singh KS                                                            #
# Contact : kumarsaurabh20@gmail.com                                                     #
# 									                 #             
# This file is part of PhyloGenomica package				                 #
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
# extract_seq_from_fasta_based_on_groups_file.rb                                         #
##########################################################################################
# This program fetches individual protein sequences in a group, considering groups.txt   #
# file output from OrthoMCL program, and put individual group in a separate file with    # 
# sequences. This program takes two files as input. First is groups.txt file and other is# 
# all protein fasta merged in to one file, referred here as database.fasta file.         #
#                                                                                        #
# >ruby extract_seq_from_fasta_based_on_groups_file.rb groups.txt database.fasta         #
##########################################################################################
# Author: Kumar Saurabh Singh                                                            #
# Date:   12th August 2014                                                               #
##########################################################################################

class ExtractSeqFromFasta

 def retrieve_seq
      
     #groups.txt file
     groups = ARGV[0].to_s

     #protein sequences file
     fasta  = ARGV[1].to_s
    
     #read groups file
      groups = read_file(groups)
      groups_array = groups.map {|e| e.chomp.split("\s")}      
     #read fasta file
      seqs = read_file(fasta)
      seqs_array = seqs.map {|e| e.chomp}      

    #loop through the groups data for single line elements
      group_name = ""
      groups_array.each_with_index do |group, index|        

      #The group names would be used as file names as a container of respective groups.
      group_name = group.shift.chomp(":")
      #create an output folder to create files
      path = out_path
      #main data carrier for indivudal group in groups.txt file
      match_array = []

         #loop through each orthologs to find their respective sequence
         group.each do |element|       

             #attach a fasta symbol to the sequence header for its search
             mod = ">" + element
             
             #get a start length for first group match
             startlength = seqs_array.index(mod)

             #store the elemnet of index startlength
             match_array.push(seqs_array[startlength])

             #increment the start length
             start = startlength + 1

             #define stop length
             stop = 0

             #loop through from the startlength element to the end of file
             #it will be match specific. For every match, it will start from
             #that match till the end of file
             #loop from startlength to stop i.e. protein header to protein sequence end
             #untill next header comes
	     seqs_array[start..-1].each do |ele|
                    if seqs_array.index(ele) > startlength and ele.include?(">")
                       stop =  seqs_array.index(ele) 
                       break
                    else
                       next
                    end                    
              end

              #store the matched part from start to end
              match_array.push(seqs_array.slice(start, (stop-start)))              
              #puts match_array.to_s

             outpath = File.join(path, group_name)

             #write to a file with previously sliced group name
             File.open(outpath, "w+") {|line| line.puts(match_array)}
          end  
     
     end  

   message("###############################")
   message("Files successfully written!!") 
   message("Done!!")
   message("###############################")
     

 end

 #file reader
 def read_file(filename)
    if File.exist?(filename) 
       file = IO.readlines(filename)
       return file
    else
      die("File with a provided file name does not exist in the current folder! Check again!!!")
    end
 end

 #method for stopping execution
 def die(msg)
     raise RuntimeError, msg
     #puts msg
     #exit
     #or
     #abort(msg)
 end

 def out_path 
     root = File.dirname(__FILE__)
     Dir.mkdir("output_groups") unless Dir.exist?("output_groups")
     path = File.join(root, "output_groups")
     return path
 end
 
 def message(msg)
     puts msg
 end



end

 #mains
 extract = ExtractSeqFromFasta.new
 extract.retrieve_seq
