class FastaHeader

 def mapping

     ids = file_read("ecoli.txt")
     fasta = file_read("ecoli_ori.fasta")
     count = 0
 
     fasta.map do |line| 
        
        if line.include?(">")        
	  line.replace(">#{ids[count]}") 
          count = count + 1
        else
           line
        end
     end

   File.open("out.fasta", "w+") {|e| e.puts(fasta)}

 end

 def file_read(filename)
    file = IO.readlines(filename)
    file.map {|e| e.chomp}
    return file   
 end


end

run = FastaHeader.new
run.mapping
