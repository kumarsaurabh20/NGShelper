// cool_exons17 -- inspect many-way maf files to find exons where:
// (1) in each of the three implied pairwise alignments, the exon is in a
//	single local alignment (maybe split across 17-way blocks),
// (2) alignments to species 2 and to species 3 have a single gap in precisely
//	the same places, and its length is a multiple of three,
// (3) there is no gap in the alignment to species 1 near the gap relative to
//      species 2 and 3.

#include "lib.h"
#include "maf.h"

#define FUDGE 10	// no human-seq1 gap this far from the seq2,3 gap
#define SIZE 100000	// plenty big for covering an exon

char human[SIZE], seq1[SIZE], seq2[SIZE], seq3[SIZE],
  *seq1_name, *seq2_name, *seq3_name;
int n_col;

void print_row(char *s, int n) {
	int i;

	for (i = 0; i < n; ++i)
		putchar(s[i]);
	putchar('\n');
}

void print_align() {
	print_row(human, n_col);
	print_row(seq1, n_col);
	print_row(seq2, n_col);
	print_row(seq3, n_col);
}

// read mafs until a human exon is covered; save non-dash columns for 4 species
int get_align(struct mafFile *mf, int b, int e) {
	static struct mafAli *a = NULL;
	static int eof = 0;
	struct mafComp *h, *c;
	int i, pos, next_pos1, next_pos2, next_pos3, fit;
	char *s, *t, *t1, *t2, *t3;

	if (eof)
		return 0;
	if (a == NULL)
		a = mafNext(mf);	// initialize

	// find the maf containing human position b
//printf("get_align: b = %d, e = %d\n", b, e);
	for ( ; ; ) {
		h = a->components;
		if (strncmp(h->src, "hg", 2) == 0 &&
		    h->start + h->size > b)
			break;
		mafAliFree(&a);
		a = mafNext(mf);
		if (a == NULL) {
			eof = 1;
			return 0;
		}
	}
	if (h->start > b)
		return 0;

//mafWrite(stdout, a);
	// return 0 if the alignment does not contain the 3 other species
	t1 = t2 = t3 = NULL;
	for (c = h; c != NULL; c = c->next) {
		s = c->src;
		if (strstr(s, seq1_name)) {
			next_pos1 = c->start + c->size;
			t1 = c->text;
		} if (strstr(s, seq2_name)) {
			next_pos2 = c->start + c->size;
			t2 = c->text;
		} if (strstr(s, seq3_name)) {
			next_pos3 = c->start + c->size;
			t3 = c->text;
		}
	}
	if (t1 == NULL || t2 == NULL || t3 == NULL)
		return 0;
 
	// find alignment column containing human position b
	t = h->text;
	for (pos = h->start - 1, i = 0; i < a->textSize; ++i)
		if (t[i] != '-' && ++pos >= b)
			break;
	if (i == a->textSize)
		fatal("ran off human text in get_align");

	// now pos = b; in what follow, pos is the next human position
	// record non-dash columns until human position e or end of maf
	for (n_col = 0; i < a->textSize; ++i) {
		if (t[i] != '-' || t1[i] != '-' ||
		    t2[i] != '-' || t3[i] != '-') {
			human[n_col] = t[i];
			seq1[n_col] = t1[i];
			seq2[n_col] = t2[i];
			seq3[n_col] = t3[i];
			++n_col;
		}
		if (t[i] != '-' && ++pos == e)
			break;
	}

	// if necessary, read more mafs to reach human position e
//print_align();
//printf("pos = %d, e = %d\n", pos, e);
	while (pos < e) {
		// like for the first maf, minus scanning for position b,
		// plus a contiguity check for all four species
		mafAliFree(&a);
		if ((a = mafNext(mf)) == NULL) {
			eof = 1;
			return 0;
		}
		h = a->components;
		if (strncmp(h->src, "hg", 2) != 0 || h->start != pos)
			return 0;
//mafWrite(stdout, a);
		t1 = t2 = t3 = NULL;
		fit = 1;
		for (c = h; c != NULL; c = c->next) {
			s = c->src;
			if (strstr(s, seq1_name)) {
				if (c->start != next_pos1) // lost contiguity?
					fit = 0;
				next_pos1 = c->start + c->size;
				t1 = c->text;
			} if (strstr(s, seq2_name)) {
				if (c->start != next_pos2)
					fit = 0;
				next_pos2 = c->start + c->size;
				t2 = c->text;
			} if (strstr(s, seq3_name)) {
				if (c->start != next_pos3)
					fit = 0;
				next_pos3 = c->start + c->size;
				t3 = c->text;
			}
		}
		if (!fit || t1 == NULL || t2 == NULL || t3 == NULL)
			return 0;
 
		t = h->text;
		for (i = 0; i < a->textSize; ++i) {
			if (t[i] != '-' || t1[i] != '-' ||
			    t2[i] != '-' || t3[i] != '-') {
				human[n_col] = t[i];
				seq1[n_col] = t1[i];
				seq2[n_col] = t2[i];
				seq3[n_col] = t3[i];
				++n_col;
			}
			if (t[i] != '-' && ++pos == e)
				break;
		}
//print_align();
//printf("pos = %d, e = %d\n", pos, e);
//exit(0);
	}

	return 1;
}
// Decide if an aligned exon has precisely one gap between human and seq2,
// and 3 divides the gap's length.
// If so, return the first and last columns containing the gap
int one3_gap2(int *beg_gap, int *end_gap) {
	int ngaps_human = 0, ngaps_seq2 = 0, i, prev_i, size_gap = 0;
	char s, t;
	
	*beg_gap = *end_gap = -1;
	// we reject exons containing 'N'
	for (prev_i = -1, i = 0; i < n_col;  ++i) {
		s = human[i];
		t = seq2[i];
		if (toupper(s) == 'N' || toupper(t) == 'N')
			return 0;
		if (s == '-' && t == '-')
			continue;
		if (s == '-') {
			++size_gap;
			if (prev_i == -1 || human[prev_i] != '-') {
				*beg_gap = i;
				++ngaps_human;
			}
		} else if (prev_i >= 0 && human[prev_i] == '-')
			*end_gap = i;
		if (t == '-') {
			++size_gap;
			if (prev_i == -1 || seq2[prev_i] != '-') {
				*beg_gap = i;
				++ngaps_seq2;
			}
		} else if (prev_i >= 0 && seq2[prev_i] == '-')
			*end_gap = i;
		prev_i = i;
	}

	return ngaps_human + ngaps_seq2 == 1 && (size_gap % 3) == 0;
}

// Verify that human-vs-seq1 has no gaps near a specified range of columns
int no_gap_near1(int b_col, int e_col) {

	int i, x, y;
	char h, s;

	x = MAX(b_col - FUDGE, 0);
	y = MIN(e_col + FUDGE, n_col);
	
	for (i = x; i < y; ++i) {
		h = human[i];
		s = seq1[i];
		if ((h == '-' && s != '-') ||
		    (h != '-' && s == '-'))
			return 0;
	}
	return 1;
}

int same_gaps23() {
	int i;
	char s, t;

	for (i = 0; i < n_col; ++i) {
		s = seq2[i];
		t = seq3[i];
		if ((s == '-' && t != '-') ||
		    (s != '-' && t == '-'))
			return 0;
	}
	return 1;
}

int main(int argc, char **argv) {
	struct mafFile *mf;
	FILE *fp;
	char buf[500];
	int b, e, gap_beg, gap_end, cool_exon, hum_exon, aligned_exon;

	argv0 = "cool_exons17";

	if (argc != 6)
		fatal("args: chr.maf chr-exons seq1-name seq2-name seq3-name");
	
	mf = mafOpen(argv[1], 0);
	fp = ckopen(argv[2], "r");
	seq1_name = argv[3];
	seq2_name = argv[4];
	seq3_name = argv[5];

	cool_exon = hum_exon = aligned_exon = 0;
	while (fgets(buf, 500, fp)) { 
		if (sscanf(buf, "%*s %d %d", &b, &e) != 2)
			fatalf("ends: %s", buf);
		++hum_exon;
		if (get_align(mf, b, e)) {
			++aligned_exon;
			if (one3_gap2(&gap_beg, &gap_end) &&
			    gap_beg > 4 && gap_beg <= gap_end &&
			    gap_end < n_col - 4 &&
			    same_gaps23() &&
			    no_gap_near1(gap_beg, gap_end)) {
				++cool_exon;
				printf("%s", buf);
				print_align();
				putchar('\n');
			}
		}
	}
	fprintf(stderr,
	  "%d coding exons, %d completely aligned, %d look interesting\n",
	  hum_exon, aligned_exon, cool_exon);
	return 0;
}
