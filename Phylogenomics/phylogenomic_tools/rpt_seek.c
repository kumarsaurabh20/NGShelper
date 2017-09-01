// Read a list of intervals (for interspersed repeats) for "species 1" and
// consult alignments of species 1 with two other species, looking for repeat
// elements that (1) align with the second species and (2) look like a clean
// insertion in species 1 relative to species 3.

#include "lib.h"

#define DEFAULT_COV 0.75
#define DEFAULT_MIN_BP 40

#undef ABS
#define ABS(x) ((x) > 0 ? (x) : -(x))

void swap(int *x, int *y) {
	int tmp = *x;

	*x = *y;
	*y = tmp;
}

// find the next gap-free aligned segment in a blastz output file
// return 0 at end of file
int next_line(FILE *fp, int *b1, int *e1, int flip) {
	char buf[500];
	int x, y;

	while (fgets(buf, 500, fp))
		if (sscanf(buf, "  l %d %d %d %d", b1, &x, e1, &y)  == 4) {
			if (flip) {
				*b1 = x;
				*e1 = y;
			}
			return 1;
		}
	return 0;
}

// return the amount of interval b-to-e covered by alignments in *fp
int find_cov(int b, int e, FILE *fp, int flip) {
	static int b1 = 0, e1 = 0, old_e = 0, done = 0;
	int cov;

	if (b <= old_e)
		fatalf("overlapping intervals in find_cov");
	old_e = e;
	if (done)
		return 0;
	// find the first relevant MSP (gap-free aligned segment) 
	while (e1 < b)
		if (next_line(fp, &b1, &e1, flip) == 0) {
			done = 1;
			return 0;
		}
	b1 = MAX(b, b1);
	cov = 0;
	while (e1 < e) {
		cov += (e1-b1+1);
		if (next_line(fp, &b1, &e1, flip) == 0) {
			done = 1;
			return cov;
		}
	}
//if (b == 669378) fprintf(stderr, "cov = %d\n", cov + e - MIN(b1, e));
	return cov + e - MIN(b1-1, e);
}

// return the amount of by which interval b-to-e differs from being a clean
// insertion relative to alignments in *fp
int missing(int b, int e, FILE *fp, int flip) {
	static int left_e1 = 0, left_e2 = 0, right_b1 = 0, right_b2 = 0,
	  right_e1, right_e2, old_e = 0, done = 0;
	char buf[500], *status;
	int mid = (b+e)/2, hole;

	if (b <= old_e)
		fatalf("overlapping intervals in find_cov");
	old_e = e;
	if (done)
		return 1000000;
//if (b == 669378) fprintf(stderr, "b = %d, e = %d, left_e1 = %d\n",b,e,left_e1);
	while (right_b1 <= mid) {
		left_e1 = right_e1;
		left_e2 = right_e2;
		while ((status = fgets(buf, 500, fp)) != NULL &&
		       !same_string(buf, "a {\n"))
			;
		if (status == NULL) {
			done = 1;
			return 1000000;
		}
		if (fgets(buf, 500, fp) == NULL ||
		    fgets(buf, 500, fp) == NULL ||
		    sscanf(buf, "  b %d %d", &right_b1, &right_b2) != 2 ||
		    fgets(buf, 500, fp) == NULL ||
		    sscanf(buf, "  e %d %d", &right_e1, &right_e2) != 2)
			fatal("bad data in second alignment file");
		if (flip) {
			swap(&right_b1, &right_b2);
			swap(&right_e1, &right_e2);
		}
	}
/*
if (b == 669378) fprintf(stderr, "after loop, left_e1 = %d, right_b1 = %d\n",
left_e1, right_b1);
*/

	hole = MAX(ABS(left_e1-b), ABS(e-right_b1));
/*
if (b == 669378) fprintf(stderr, "hole = max of %d and abs of %d-%d\n", hole,
left_e2, right_b2);
*/
	return MAX(hole, ABS(left_e2-right_b2));
}

FILE *do_open(char *filename, char *first_line, int must) {
	FILE *fp;
	char buf[500];

	if ((fp = fopen(filename, "r")) == NULL) {
		if (must)
			fatalf("cannot open %s", filename);
		else
			return NULL;
	}
	if (fgets(buf, 500, fp) == NULL ||
	    !same_string(buf, first_line))
		fatalf("%s is not the right kind of file", filename);
	return fp;
}

int main(int argc, char **argv) {
	FILE *rpt, *fp1, *fp2;
	char buf[500], *s;
	int b, e, old_e, nlap, cov, len, hole, flip1, flip2,
	  min_bp = DEFAULT_MIN_BP;
	float f = DEFAULT_COV;

	if (argc == 6) {
		f = atof(argv[4]);
		min_bp - atoi(argv[5]);
	} else if (argc != 4)
	 fatal("args: species1 species2 species3 [fract-cov insert-diff]");
	sprintf(buf, "%s.rpts", argv[1]);
	rpt  = do_open(buf, "#:rpt\n", 1);

	flip1 = flip2 = 0;

	sprintf(buf, "%s.%s.bz", argv[1], argv[2]);
	if ((fp1 = do_open(buf, "#:lav\n", 0)) == NULL) {
		flip1 = 1;
		sprintf(buf, "%s.%s.bz", argv[2], argv[1]);
		fp1 = do_open(buf, "#:lav\n", 1);
	}

	sprintf(buf, "%s.%s.bz", argv[1], argv[3]);
	if ((fp2 = do_open(buf, "#:lav\n", 0)) == NULL) {
		flip2 = 1;
		sprintf(buf, "%s.%s.bz", argv[3], argv[1]);
		fp2 = do_open(buf, "#:lav\n", 1);
	}

	nlap = e = 0;
	while (fgets(buf, 500, rpt)) {
		old_e = MAX(e, old_e);
		if (sscanf(buf, "%d %d", &b, &e) != 2)
			fatalf("cannot parse: %s", buf);
		if (b <= old_e) {
			++nlap;
			continue;
		}
		if ((len = e - b + 1) > 100 &&
		    (cov = find_cov(b, e, fp1, flip1)) > f*len &&
		    (hole = missing(b, e, fp2, flip2)) <= min_bp) {
			if ((s = strchr(buf, '\n')) != NULL)
				*s = '\0';
			printf("%s %4.2f %d\n",
			  buf, (float)cov/(float)len, hole);
		}
	}
/*
	if (nlap > 0)
	    fprintf(stderr, "%d overlapping repeats were ignored\n", nlap);
*/
	return 0;
}
