class FormatFasta
	def nameChange
	count = 0
        file = ARGV[0].to_s
	   file = IO.readlines(file)
	   file2 = file.map {|e| e.strip}
	   file3 = file2.each_with_index do |e,i|
		   
		   if e.include?(">missing_-m_qualifer")
		      e.replace(">Hchl|#{i}")
		   else
		      next
		   end
		end
	   puts file3
	   
	end
end

check = FormatFasta.new

check.nameChange




