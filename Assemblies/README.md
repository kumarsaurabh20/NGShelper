# Asscripts


##Assembly_fragmentation.rb
This program takes the scaffolds file in fasta format produced from any assembler. It first merges all the scaffolds and creates a single big scaffold, eventually producing multiple 2.5kb fragments with 500bp overlapping ends. The script is generated keeping hybrid assemblies in mind. The script was used to create 2.5kb overlapping artificial reads for a hybrid assembly together with ionTorrent reads (assembled using Newbler).  
