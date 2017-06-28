#!/usr/bin/env python2
from __future__ import print_function
import sys, argparse, re

__author__ = 'Kumar'

coords_file = ''
ref_map, filter_id, filter_len, filter_chrom = ({} for i in range(4))
ref_start, ref_end, qry_start, qry_end, pid, ref, qry, ref_len, qry_len = ([] for i in range(9))

def string_to_hash(arg):
        temp = {}
        pattern = re.compile("\w+:[\w\d\.]+")
        if pattern.match(arg):
                value = str(arg).split(":")
                if value[0] == "ID":
                        temp["ID"] = float(value[1])
                elif value[0] == "length":
                        temp["length"] = int(value[1])
                elif value[0] == "chrom":
                        temp["chrom"] = str(value[1])
                else:
                        pass
        else:
                raise argparse.ArgumentTypeError("Oops!! bad input values.")
        return temp

##parse command line arguments
try:
	parser = argparse.ArgumentParser("Script for parsing Mummer/Nucmer based coords file.")

	parser.add_argument("-c", "--coords", action="store", required=True, help="Input mummer based coords file")
	parser.add_argument("-p", "--filter_id", type=string_to_hash, action="store", required=False, help="Set if filtering is required based on percentage identity (default: no filters). -p <ID:float> ")
	parser.add_argument("-l", "--filter_len", type=string_to_hash,  action="store", required=False, help="Set if filtering is required based on reference/query alignment lengths (default: no filters). -l <lenth:int>")
	parser.add_argument("-s", "--filter_chrom",type=string_to_hash, action="store", required=False, help="Set if filtering is required based on a particular scaffold/contig/chromosome from reference (default: no filters). -s <chrom:str>")

	args = parser.parse_args()
	##populate global variables
	coords_file = args.coords
	
	if args.filter_id: filter_id = args.filter_id
	if args.filter_len: filter_len = args.filter_len
	if args.filter_chrom: filter_chrom = args.filter_chrom

except argparse.ArgumentError as e:
	parser.print_help()
	sys.exit(2)

##parse the coords file based on regular expression (the coords file is not perfectly tab separated)
pattern = re.compile('\s+(\d+)\s+(\d+)\s+\|\s+(\d+)\s+(\d+)\s+\|\s+(\d+)\s+(\d+)\s+\|\s+(\d+.\d+)\s+\|\s+(.+)\s+(.+)[\s\n\t]')
cf = open(coords_file, "r")
for line in cf:
	result = pattern.match(line)
	if result != None:	
		if filter_id.has_key("ID"):
			if float(result.group(7)) >= float(filter_id["ID"]):
				ref_start.append(result.group(1))
				ref_end.append(result.group(2))
				qry_start.append(result.group(3))
				qry_end.append(result.group(4))
				ref_len.append(result.group(5))
				qry_len.append(result.group(6))
				pid.append(result.group(7))
				ref.append(result.group(8))
				qry.append(result.group(9))
			else:
				continue
		else:
			ref_start.append(result.group(1))
			ref_end.append(result.group(2))
			qry_start.append(result.group(3))
			qry_end.append(result.group(4))
			ref_len.append(result.group(5))
			qry_len.append(result.group(6))
			pid.append(result.group(7))
			ref.append(result.group(8))
			qry.append(result.group(9))
	else:
		continue

##create a ref query map file
uniq_ref = [x for x in set(ref)]
uniq_ref.sort()
for element in uniq_ref:
	qry_list = []
	for index, item in enumerate(ref):
		if element == ref[index]:
			qry_list.append(qry[index])
		else:
			continue 		 	
	ref_map[element] = qry_list

##out file 1
mapping_header = "Reference\tQuery\n"
map_ref_file = open("reference_query.mapping", "w")
for k,v in ref_map.iteritems():
	if map_ref_file.tell() == 0:
		map_ref_file.write(mapping_header)
		map_ref_file.write("%s\t%s\n"% (k,','.join(v)))
		
	else:
		map_ref_file.write("%s\t%s\n"% (k,','.join(v)))
map_ref_file.close()	

##out file 2
count_file_header = "Reference\tQuery_counts\n"
map_count_file = open("reference_query.counts", "w")
for k,v in ref_map.iteritems():
        if map_count_file.tell() == 0:
                map_count_file.write(count_file_header)
                map_count_file.write("%s\t%d\n"% (k,len(v)))

        else:
                map_count_file.write("%s\t%d\n"% (k,len(v)))
map_count_file.close()

