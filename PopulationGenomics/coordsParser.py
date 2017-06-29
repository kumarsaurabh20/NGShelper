#!/usr/bin/env python2
from __future__ import print_function
import sys, argparse, re

__author__ = 'Kumar'

coords_file = "" #out_prefix = ("" for i in range(2))
ref_map, filter_map = ({} for i in range(2))
ref_start, ref_end, qry_start, qry_end, pid, ref, qry, ref_len, qry_len = ([] for i in range(9))

def string_to_hash(arg):
	dummy = {}
	pattern = re.compile("(\w+:[\d\w.]+){1,3}")
	if pattern.match(arg):
		temp = arg.split(" ")
		for e in temp:
			temp2 = e.split(":")
			dummy[str(temp2[0])] = temp2[1]
	else:
		raise argparse.ArgumentTypeError("Oops!! bad input values.")
	return dummy

##parse command line arguments
try:
	parser = argparse.ArgumentParser("Script for parsing Mummer/Nucmer based coords file.")

	parser.add_argument("-c", "--coords", action="store", required=True, help="Input mummer based coords file")
	parser.add_argument("-f", "--filter_string", type=string_to_hash, action="store", required=False, help="Set if filtering is required based on percentage identity or length or with chromosomes/scaffolds (default: no filters). -p <ID:float length:int chrom:Scaffold001>.")
	#parser.add_argument("-p", "--prefix", action="store", required=False, help="Prefix for the output files.")

	args = parser.parse_args()
	##populate global variables
	coords_file = args.coords
	#if args.prefix: out_prefix = args.prefix
	if args.filter_string: filter_map = args.filter_string

except argparse.ArgumentError as e:
	parser.print_help()
	sys.exit(1)

##parse the coords file based on regular expression (the coords file is not perfectly tab separated)
pattern = re.compile('\s+(\d+)\s+(\d+)\s+\|\s+(\d+)\s+(\d+)\s+\|\s+(\d+)\s+(\d+)\s+\|\s+(\d+.\d+)\s+\|\s+(.+)\s+(.+)[\s\n\t]')
cf = open(coords_file, "r")
for line in cf:
	result = pattern.match(line)
	if result != None:	
		#print(result.groups())
		#print(result.group(1).split(" "))
		#ref_start, ref_end = re.split("\s+", result.group(1)))
		if not filter_map:
			ref_start.append(result.group(1))
                        ref_end.append(result.group(2))
                        qry_start.append(result.group(3))
                        qry_end.append(result.group(4))
                        ref_len.append(result.group(5))
                        qry_len.append(result.group(6))
                        pid.append(result.group(7))
                        ref.append(result.group(8))
                        qry.append(result.group(9))
                        print("this is without filter")
                        print(pid)
                        #print("%s:::::%s"% (ref_start, ref_end))
                        #print("%s:::::%s"% (ref, qry))
		#	print(filter_id)
		else:
			if filter_map.has_key("length"):
				if filter_map.has_key("chrom"):
					if filter_map.has_key("ID"):
						if str(result.group(8)) == str(filter_map["chrom"]) and float(result.group(7)) >= float(filter_map["ID"]) and int(result.group(6)) >= int(filter_map["length"]):
 							ref_start.append(result.group(1))
							ref_end.append(result.group(2))
							qry_start.append(result.group(3))
							qry_end.append(result.group(4))
							ref_len.append(result.group(5))
							qry_len.append(result.group(6))
							pid.append(result.group(7))
							ref.append(result.group(8))
							qry.append(result.group(9))
							print("this is with chrom and ID and length filter")
							print(qry_len)
							#print("%s:::::%s"% (ref_start, ref_end))
							#print("%s:::::%s"% (ref, qry))
						else:
							continue
					else:
						if str(result.group(8)) == str(filter_map["chrom"]) and int(result.group(6)) >= int(filter_map["length"]):
							ref_start.append(result.group(1))
							ref_end.append(result.group(2))
							qry_start.append(result.group(3))
							qry_end.append(result.group(4))
							ref_len.append(result.group(5))
							qry_len.append(result.group(6))
							pid.append(result.group(7))
							ref.append(result.group(8))
							qry.append(result.group(9))
							print("this is with chrom and length filter")
							print(qry_len)
							#print("%s:::::%s"% (ref_start, ref_end))
							#print("%s:::::%s"% (ref, qry))	
						else:
							continue
				elif filter_map.has_key("ID"):
					if int(result.group(6)) >= int(filter_map["length"]) and float(result.group(7)) == float(filter_map["ID"]):
						ref_start.append(result.group(1))
						ref_end.append(result.group(2))
						qry_start.append(result.group(3))
						qry_end.append(result.group(4))
						ref_len.append(result.group(5))
						qry_len.append(result.group(6))
						pid.append(result.group(7))
						ref.append(result.group(8))
						qry.append(result.group(9))
						print("this is with length and ID filter")
						print(qry_len)
						#print("%s:::::%s"% (ref_start, ref_end))
						#print("%s:::::%s"% (ref, qry))
					else:
						continue
				else:
					if int(result.group(6)) >= int(filter_map["length"]):
						ref_start.append(result.group(1))
						ref_end.append(result.group(2))
						qry_start.append(result.group(3))
						qry_end.append(result.group(4))
						ref_len.append(result.group(5))
						qry_len.append(result.group(6))
						pid.append(result.group(7))
						ref.append(result.group(8))
						qry.append(result.group(9))
						print("this is with length filter")
						print(qry_len)
					else:
						continue
			elif filter_map.has_key("chrom"):
				if filter_map.has_key("ID"):
					if str(result.group(8)) == str(filter_map["chrom"]) and float(result.group(7)) == float(filter_map["ID"]):
						ref_start.append(result.group(1))
						ref_end.append(result.group(2))
						qry_start.append(result.group(3))
						qry_end.append(result.group(4))
						ref_len.append(result.group(5))
						qry_len.append(result.group(6))
						pid.append(result.group(7))
						ref.append(result.group(8))
						qry.append(result.group(9))
						print("this is with chrom and id filter")
						print(qry_len)
						#print("%s:::::%s"% (ref_start, ref_end))
						#print("%s:::::%s"% (ref, qry))
					else:
						continue
				else:
					if str(result.group(8)) == str(filter_map["chrom"]):
						ref_start.append(result.group(1))
						ref_end.append(result.group(2))
						qry_start.append(result.group(3))
						qry_end.append(result.group(4))
						ref_len.append(result.group(5))
						qry_len.append(result.group(6))
						pid.append(result.group(7))
						ref.append(result.group(8))
						qry.append(result.group(9))
						print("this is with chrom filter")
						print(qry_len)
					else:
						continue
					
			elif filter_map.has_key("ID"):	
				if float(result.group(7)) >= float(filter_map["ID"]):
					ref_start.append(result.group(1))
					ref_end.append(result.group(2))
					qry_start.append(result.group(3))
					qry_end.append(result.group(4))
					ref_len.append(result.group(5))
					qry_len.append(result.group(6))
					pid.append(result.group(7))
					ref.append(result.group(8))
					qry.append(result.group(9))
					print("this is with ID filter")
					print(qry_len)
					#print("%s:::::%s"% (ref_start, ref_end))
					#print("%s:::::%s"% (ref, qry))
				else:
					continue
			else:
				continue
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

