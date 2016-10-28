##
# pysam.cigar: the tuple [ (0,3), (1,5), (0,2) ] refers to an alignment with 3 matches, 5 insertions and another 2 matches.
# @ args min_gap is a parameter that specifies the length of the softclip/split 
# in order for the function get_split_positions to return it as a valid split.
# e.g. min_gap =3 returns all breakpoints for where the unaligned part is longer than 2 base pairs.

def get_split_positions(read, min_gap):
    """Parse cigar string for detection of break points in a read 
    Break point is a position where a read is aligned to a reference, 
    but the position in the read following this position is no longer aligned. 
    Break points can be caused by softclipping (ends are not aligned), 
    or by an alignment that has split the read up into disjoint segments aligned on different places.
    """
    cigar = read.cigar
    # Cigar string is a list of tuples:
    if len(read.cigar) <= 1:
        return [] # no break points = empty list of break point positions

    ##
    # read has break points if cigar string is longer than 1

    # This is a list with the breakpoint tuples
    list_of_break_point_positions = []

    # set the current position on the genome
    if cigar[0][0] == 0:
        current_pos = int(read.positions[0])
    else:
        current_pos = int(read.positions[0]) - cigar[0][1]

    # Search for breakpoints in cigar and get the corresponding position on the genome

    i = 0
    for info_tuple in cigar:
        # If current segment in cigar string is aligned.
        if info_tuple[0] == 0:
            # Special case when at first segment:
            if i == 0 and cigar[1][1] >= min_gap: # first end-split
                list_of_break_point_positions.append((current_pos + info_tuple[1] , True))

            # Special case when at last segment:
            elif i == len(cigar) - 1 and cigar[i - 1][1] >= min_gap:
                list_of_break_point_positions.append((current_pos, False))

            # Internal segments:
            elif cigar[i - 1][1] >= min_gap and cigar[i + 1][1] >= min_gap:
                if cigar[i - 1][1] >= min_gap:
                    list_of_break_point_positions.append((current_pos, False))
                if cigar[i + 1][1] >= min_gap:
                    list_of_break_point_positions.append((current_pos + info_tuple[1] - 1, True))
        i += 1

        current_pos += info_tuple[1]

    return(list_of_break_point_positions)







if __name__ == "__main__":
    from svest.util import bamio
    import sys
    bamfile = bamio.open_bam_file(sys.argv[1])
    for read in bamfile:
        #print read.cigar
        if not read.is_unmapped and len(read.cigar) > 1:
            #print read.cigar
            print get_split_positions(read, 0)

Status 