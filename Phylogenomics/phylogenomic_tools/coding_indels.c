// coding_indels -- inspect pair-wise axt files of human-vs-other alignments,
// with three other species, to find exons where:
// (1) in each of the three alignments, the exon is in a single local alignment,
// (2) there is no gap in the alignment to species 1,
// (3) alignments to species 2 and to species 3 have gaps in precisely the
//     same places, and all gaps have a multiple-of-three length

#include "lib.h"

// rediculously liberal maximum length of any local alignment
#define M 200000

// Think of species 1-3 as armadillo, elephant and opossum; 'a', 'e', and 'o'.
// Each local alignment has 4 lines (last is empty).
char a1[M], a2[M], a3[M], a4[M], 
     e1[M], e2[M], e3[M], e4[M],
     o1[M], o2[M], o3[M], o4[M];

int debug = 0;

// find columns corresponding to positions b and e; pos = starting position
void find_cols(char *l2, int b, int e, int pos, int *beg_col, int *end_col) {
	int col;
	char x;

	// positions are 0-based, half-open, and we want the same with columns
	for (col = 0; pos <= e; ++col)
		if ((x = l2[col]) == '\0')
			fatalf("ran off end at b = %d, e = %d, col = %d",
			  b, e, col);
		else if (x != '-') {
			if (pos == b)
				*beg_col = col;
			if (pos == e)
				*end_col = col;
			++pos;
		}
}

void print_align(int b, int e, int B1, char *l2, char *l3) {
	int col, beg_col, end_col; 

	find_cols(l2, b, e, B1, &beg_col, &end_col);

	for (col = beg_col; col < end_col; ++col)
		putchar(l2[col]);
	putchar('\n');
	for (col = beg_col; col < end_col; ++col)
		putchar(l3[col]);
	putchar('\n');
}

// Indicate the quality of an exon's alignment, with returned values:
//    0 = contains Ns, 1 = no gaps in interval, 2 = bad gaps, 3 = 3-gaps
int ck_align(int b, int e, int B1, char *l2, char *l3) {
	int col, gap_len, beg_col, end_col, gaps;

	find_cols(l2, b, e, B1, &beg_col, &end_col);
	
	// we will ignore exons containing 'N'
	gaps = 0;
	for (col = beg_col; col < end_col;  ++col) {
		if (l2[col] == '-' || l3[col] == '-')
			gaps = 1;
		if (toupper(l2[col]) == 'N' || toupper(l3[col]) == 'N')
			return 0;
	}
	if (gaps == 0)
		return 1;

	// look for bad gaps in the first sequence
	for (col = beg_col; col < end_col; ++col)
		if (l2[col] == '-') {
			for (gap_len = 1, ++col;
			  col <= end_col && l2[col] == '-';
			  ++gap_len, ++col)
				;
			if (gap_len % 3 != 0)
				return 2;
		}

	// look for bad gaps in the second sequence
	for (col = beg_col; col < end_col; ++col)
		if (l3[col] == '-') {
			for (gap_len = 1, ++col;
			  col <= end_col && l3[col] == '-';
			  ++gap_len, ++col)
				;
			if (gap_len % 3 != 0)
				return 2;
		}
	
	return 3;
}

int get_align(FILE *fp, char *x1, char *x2, char *x3, char *x4, int *B1,
  int *E1) {
	char *status;
	static int done = 0;

	if (done) {
		*B1 = *E1 = 0;
		return 0;
	}

	while ((status = fgets(x1, M, fp)) != NULL && x1[0] == '#')
		;
	if (status == NULL) {
		done = 1;
		*B1 = *E1 = 0;
		return 0;
	}
	if (sscanf(x1, "%*s %*s %d %d", B1, E1) != 2)
		fatalf("alignment: %s", x1);
	// translate from 1-based closed to 0-based open
	(*B1)--;
	if (fgets(x2, M, fp) == NULL ||
	    fgets(x3, M, fp) == NULL ||
	    fgets(x4, M, fp) == NULL ||
	    x4[0] != '\n')
		fatal("out of synch");

	return 1;
}

int same_gaps(int b, int e, int b1, char *l2, char *l3, int B1, char *L2,
   char *L3) {
	int i, col, Col, beg_col, end_col, Beg_col, End_col;

	find_cols(l2, b, e, b1, &beg_col, &end_col);
	find_cols(L2, b, e, B1, &Beg_col, &End_col);
	if (debug) {
		putchar('\n');
		print_align(b, e, b1, l2, e3);
		print_align(b, e, B1, L2, L3);
		printf("beg_col = %d, Beg_col = %d, end_col = %d, End_col = %d\n",
		   beg_col, Beg_col, end_col, End_col);
	}
	
	for (i = 0; i < end_col - beg_col; ++i) {
		col = i + beg_col;
		Col = i + Beg_col;
		if ((l2[col] == '-' && L2[Col] != '-') ||
		    (l2[col] != '-' && L2[Col] == '-') ||
		    (l3[col] == '-' && L3[Col] != '-') ||
		    (l3[col] != '-' && L3[Col] == '-')) {
			if (debug)
				printf("mismatch at i = %d\n", i);
			return 0;
		}
	}
	if (debug)
		printf("hit\n");
	return 1;
}

int main(int argc, char **argv) {
	FILE *fp, *ap, *ep, *op;
	char buf[500];
	int b, e, cool_exon, hum_exon, aligned_exon, aB1, aE1, eB1, eE1, oB1,
	  oE1;

	argv0 = "coding_indels";
	if (argc == 6 && same_string(argv[5], "debug")) {
		debug = 1;
		--argc;
	}
	if (argc != 5)
		fatal("args: chr-exons seq1-axt seq2-axt outgroup-axt [debug]");
	
	fp = ckopen(argv[1], "r");
	ap = ckopen(argv[2], "r");
	ep = ckopen(argv[3], "r");
	op = ckopen(argv[4], "r");

	cool_exon = hum_exon = aligned_exon = aE1 = eE1 = oE1 = 0;
	while (fgets(buf, 500, fp)) { 
		if (sscanf(buf, "%*s %d %d", &b, &e) != 2)
			fatalf("ends: %s", buf);
		++hum_exon;
		while (aE1 < b && get_align(ap, a1, a2, a3, a4, &aB1, &aE1))
			;
		while (eE1 < b && get_align(ep, e1, e2, e3, e4, &eB1, &eE1))
			;
		while (oE1 < b && get_align(op, o1, o2, o3, o4, &oB1, &oE1))
			;
		if (aB1 <= b && e <= aE1 &&
		    eB1 <= b && e <= eE1 &&
		    oB1 <= b && e <= oE1) {
			++aligned_exon;
			if (ck_align(b, e, aB1, a2, a3) == 1 &&
			    ck_align(b, e, eB1, e2, e3) == 3 &&
			    same_gaps(b, e, eB1, e2, e3, oB1, o2, o3)) {
				++cool_exon;
				printf("%s", buf);
				print_align(b, e, aB1, a2, a3);
				print_align(b, e, eB1, e2, e3);
				print_align(b, e, oB1, o2, o3);
				putchar('\n');
			}
		}
	}
	fprintf(stderr,
	  "%d coding exons, %d completely aligned, %d look interesting\n",
	  hum_exon, aligned_exon, cool_exon);

	return 0;
}
