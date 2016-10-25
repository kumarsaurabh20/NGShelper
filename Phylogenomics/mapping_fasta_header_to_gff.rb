class MappingFastaHeader

 def mapping(filename="")
 
   headers = Array.new

   f = File.open(filename,"r")
   f.each_line do |line|
       headers.push(line) if line.match(/^>.+/)      
   end

   dummy = headers.map {|e| e.split("|")}
   dummy.map {|e| e.pop}
   mod_headers = dummy.map {|e| e.join("|")}
   write_method("headers.txt", mod_headers)
   
   return mod_headers

 end

 def cds_extract

        headers = mapping("hchl.fasta")

	file = IO.readlines("hchl.gff")
	
        nfile = file.map {|w| w.chomp.strip.split("\t")}
	nfile.map {|e| e.pop}
        nfile.shift(5)
	final = nfile.each_with_index {|e,i| e.push("ID=#{headers[i]}")}
	
        nfinal = final.map {|e| e.push(";")}
	nextfinal = nfinal.map {|e| e.join(",").gsub(",","\t")}

	nextfinal.delete_if {|e| e.include?("assembly_gap")}
	nextfinal.delete_if {|e| e.include?("gene")}
	nextfinal.delete_if {|e| e.include?("exons")}
	nextfinal.delete_if {|e| e.include?("transcript")}
	nextfinal.delete_if {|e| e.include?("mRNA")}
	nextfinal.delete_if {|e| e.include?("rRNA")}
	nextfinal.delete_if {|e| e.include?("tRNA")}
	nextfinal.delete_if {|e| e.include?("region")}

        write_method("hsalinarum.gff3", nextfinal)

 end

 def write_method (name="", value=[])
     File.open(name, "w+") {|entry| entry.puts(value)}
 end


end


 mfh = MappingFastaHeader.new
 mfh.cds_extract

##======================================================================================================================
##Using the CSV library, you can access each column using the name it has in the headers. So if you always have the same ##headers albeit in a different order, you could do that:
##
##CSV.foreach(csv_file, :col_sep => "," :headers => true) do |row|  
 ## do_whatever_you_want_with(row['your_header'])
##end
