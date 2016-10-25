
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
# extract_orthologs_from_clustered_groups.rb                                             #
##########################################################################################
# This script checks the number of actual orthologs present in the groups.txt file       #
# User need to change the taxa names for the custom use of this script.                  #
# Short names are taxa names provided during OrthoMCL analysis.                          #
# For instance: hlcl means H halochloris, Hphil means H halophilla Hsalinarum means      #
# Halobacter salinarum and Ecoli as usual. Format means number and type of species       #
# involved. The script check this from the groups.txt file name. So if you have to       #
# search true orthologs in groups.txt file from OrthoMCL program targeting two species   #
# i.e hlcl and hphil than rename the groups.txt file as hlcl_hphil_groups.txt and proceed# 
# by providing this file name as command line argument.                                  #
##########################################################################################
# Author: Kumar Saurabh Singh                                                            #
# Date: 25th July 2014                                                                   #
##########################################################################################



class Ortho


 def read_file
    filename = ARGV[0]
    name = File.basename(filename, ".txt")
    format = 0

    	case
        when name.include?("hlcl") && name.include?("hphil") then format = 1             
        when name.include?("hlcl") && name.include?("ecoli") then format = 2            
        when name.include?("hlcl") && name.include?("salinarum") then format = 3            
        else 
             puts "Check the input file!!"            
    	end    

    ortholog_count = 0
    orthologs = Array.new
    file = IO.readlines(filename)
    file.map do |e|
        
     if format == 1        
         if e.include?("Hchl") and e.include?("Hphil")
            puts "#{e}"
            ortholog_count += 1
            orthologs << e
         end
     elsif format == 2
         if e.include?("hlcl_mira") and e.include?("Ecoli")
            puts "#{e}"
            ortholog_count += 1
            orthologs << e
         end
     elsif format == 3
         if e.include?("hlcl_mira") and e.include?("Hsalinarum")
            puts "#{e}"
            ortholog_count += 1
            orthologs << e
         end
     else
         if e.include?("Ecoli") and e.include?("Hsalinarum") and e.include?("Hphil") and e.include?("hlcl")
            puts "#{e}"
            ortholog_count += 1
            orthologs << e
        end

     end
    
  end

    puts ortholog_count.to_s
    File.open("actual_orthologs.txt", "w+") {|line| line.puts(orthologs)}

 end


end

ortho = Ortho.new
ortho.read_file
