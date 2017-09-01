// Given a UCSC-format file of gene positions and a chromosome name (e.g.,
// "chr22"), write a sorted, non-redundant list of coding exons.

#include "lib.h"

#define MAX_EXONS 100000

struct exon {
	char *gene;
	int beg, end, strand, phase;
} Exon[MAX_EXONS];

int compar(struct exon *a, struct exon *b) {
	int x = a->beg, y = b->beg, p = a->end, q = b->end;

	if (x < y)
		return -1;
	if (y < x)
		return 1;
	if (p < q)
		return -1;
	if (q < p)
		return 1;
	return 0;
}

int main(int argc, char **argv) {
	FILE *fp;
	char buf[50000], *s, *T, *t, x[100], y[100], z[100], chr[100];
	int i, j, b, e, B, E, bad, phase, tot_len = 0, ngenes = 0,
	  nexons = 0, nuniq = 0;

	if (argc != 3)
		fatal("args: UCSC-gene-table chr-name");

	fp = ckopen(argv[1], "r");
	fgets(buf, 50000, fp);	// discard first line
	while (fgets(buf, 50000, fp)) {
		if (sscanf(buf, "%s %s %s %*s %*s %d %d",
		  x, y, z, &B, &E) != 5)
			fatalf("5 fields: %s", buf);
		if (!same_string(y, argv[2]))
			continue;
		strcpy(chr, y);
		++ngenes;
		for (s = buf, i = 0; s != NULL && i < 8;
		  s = strchr(s+1, '\t'), ++i)
			;
		if (s == NULL)
			fatalf("ran off end of %s", buf);
		if ((T = strchr(++s, '\t')) == NULL)
			fatalf("ends of exons: %s", buf);
		t = T+1;
		tot_len = 0;
		while (s != NULL && t != NULL && s < T) {
			b = MAX(atoi(s), B);
			e = MIN(atoi(t), E);
			if (b <= e) {
				Exon[nexons].gene = copy_string(x);
				Exon[nexons].beg = b;
				Exon[nexons].end = e;
				Exon[nexons].strand = z[0];
				phase = tot_len % 3;
				Exon[nexons].phase = phase;
				++nexons;
				tot_len += (e - b);
			}
			if ((s = strchr(s, ',')) != NULL)
				++s;
			if ((t = strchr(t, ',')) != NULL)
				++t;
		}
	}
	fclose(fp);

	qsort(Exon, (size_t)nexons, sizeof(struct exon), (const void *)compar);

	fp = ckopen(argv[2], "w");
	for (bad = i = 0; i < nexons; ) {
		++nuniq;
		for (j = i, ++i;
		   i < nexons && Exon[j].beg == Exon[i].beg &&
		   Exon[j].end == Exon[i].end;
		   ++i)
			if (Exon[j].strand != Exon[i].strand ||
			    Exon[j].phase != Exon[i].phase)
				if (Exon[j].phase >= 0) {
					fprintf(stderr,
					  "%d-%d: %s(%d) %s(%d)\n",
					  Exon[j].beg, Exon[j].end,
					  Exon[j].gene, Exon[j].phase,
					  Exon[i].gene, Exon[i].phase);
					Exon[j].phase = -1;
					Exon[i].phase = -1;
				}
		if (Exon[j].phase == -1)
			++bad;
		else
			printf("%s %d %d %c\n", chr, Exon[j].beg,
			  Exon[j].end, Exon[j].strand);
/*
			printf("%s %d %d %c %d\n", chr, Exon[j].beg,
			  Exon[j].end, Exon[j].strand, Exon[j].phase);
*/
	}
	fclose(fp);
	fprintf(stderr, "%d coding exons in %d genes; %d unique exons\n",
	  nexons, ngenes, nuniq);
	if (bad > 0)
		fprintf(stderr, "%d exons have inconsistent phase\n", bad);

	return 0;
}
