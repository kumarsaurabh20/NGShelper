#Define arrays for query and target data
#queryList -- id	desc	snp_position
#targetList -- id	desc	start	end	etc	ID
#scaffold_589	EVM	gene	611	11072	.	+	.	ID=evm.TU.scaffold_589.1;Name=HaOG214172;Note=BMORI:LOW QUALITY PROTEIN: actin, cytoplasmic A3a-like
#scaffold_0	38	1	1.000	13.0	1:2=0.03680904	1:3=0.05555556	1:4=0.05555556	2:3=0.13043478	2:4=0.13043478	3:4=0.00000000

query = ARGV[0]
target = ARGV[1]

queryList = Array.new
targetList = Array.new

temp = IO.readlines(query)
queryList = temp.map {|x| x.chomp.split("\t")}  
#puts queryList.to_s

temp2 = IO.readlines(target)
targetList = temp2.map {|x| x.chomp.split("\t")}  
#puts targetList.to_s

#File.open(query, "r") do |f|
#	f.each_line do |line|
#		queryList << line.split("\t").map(&:to_i)
#	end
#end

#File.open(target, "r") do |f|
#	f.each_line do |line|
#		targetList << line.split("\t").map(&:to_i)
#	end	
#end

queryList.each_index do |i|
	targetList.each_index do |j|
		if(queryList[i][0] == targetList[j][0])
			if (queryList[i][1].to_i >= targetList[j][3].to_i and queryList[i][1].to_i <= targetList[j][4].to_i)
				puts queryList[i].join("\t") + "\t" + targetList[j][8].to_s
			else
				next 
			end  
		else
			next
		end	
	end 	
end	
