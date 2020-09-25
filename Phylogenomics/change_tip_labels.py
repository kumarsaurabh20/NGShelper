#from string import strip
from ete3 import Tree
import sys
# load taxonomy table (assuming that the two idname and taxonomy
# columns are tab delimited) as python dictionary
#name2tax = dict([map(strip, line.split("\t")) for line in open("Buchnera.map")])
name2tax = {}
with open(sys.argv[2]) as f:
	for line in f:
		temp = line.split()
		name2tax[temp[0]] = temp[1]
print(name2tax)
# loads your tree
t = Tree(sys.argv[1])
print(t)
#     /-JN178341
#----|
#     \-GQ898616

# replace leaf names
for leaf in t.iter_leaves():
	leaf.name = name2tax[leaf.name]

# check that everything is ok
print(t)
t.show()
#     /-Bacteria;__Verrucomicrobia;__OPB35_soil_group;__o;__f;__g
#----|
#     \-Bacteria;__Firmicutes;__Clostridia;__Clostridiales;__Ruminococcaceae;    

# export newick (note that you may need to replace some spacial characters from node names (i.e. ";")
print(t.write(outfile=sys.argv[3]))
