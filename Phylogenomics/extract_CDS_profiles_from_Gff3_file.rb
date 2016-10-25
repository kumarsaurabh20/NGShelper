file = IO.readlines("hsalinarum.gff3")
nfile = file.map {|w| w.chomp.strip.split("\t")}
nfile.map {|e| e.pop}
final = nfile.each_with_index {|e,i| e.push("ID=#{i}")}
nfinal = final.map {|e| e.push(";")}
nextfinal = nfinal.map {|e| e.join(",").gsub(",","\t")}

nextfinal.delete_if {|e| e.include?("assembly_gap")}
nextfinal.delete_if {|e| e.include?("gene")}
nextfinal.delete_if {|e| e.include?("exons")}
nextfinal.delete_if {|e| e.include?("transcript")}
nextfinal.delete_if {|e| e.include?("mRNA")}
nextfinal.delete_if {|e| e.include?("rRNA")}
nextfinal.delete_if {|e| e.include?("tRNA")}
nextfinal.delete_if {|e| e.include?("tmRNA")}
nextfinal.delete_if {|e| e.include?("ncRNA")}
nextfinal.delete_if {|e| e.include?("region")}
nextfinal.delete_if {|e| e.include?("repeat region")}
nextfinal.delete_if {|e| e.include?("pseudogene")}
nextfinal.delete_if {|e| e.include?("pseudogenic_exon")}
nextfinal.delete_if {|e| e.include?("pseudogenic_region")}
nextfinal.delete_if {|e| e.include?("pseudotmRNA")}
nextfinal.delete_if {|e| e.include?("mobile_element")}
nextfinal.delete_if {|e| e.include?("STS")}
nextfinal.delete_if {|e| e.include?("processed_transcript")}
nextfinal.delete_if {|e| e.include?("origin_of_replication")}



File.open("hsalinarum.gff3", "w+") {|entry| entry.puts(nextfinal)}
