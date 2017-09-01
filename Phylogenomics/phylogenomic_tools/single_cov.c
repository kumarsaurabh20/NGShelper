/*
* single_cov.c - select from and/or trim a set of alignments to produce a high
* scoring single-coverage set.  Version of Aug. 12, 2001 by Webb Miller.
*
* The basic syntax is either "single_cov alignment_file" or "single_cov";
* the second form reads stdin.  Each point in the first sequence is covered by
* at most one selected alignment.  Every point aligned in the original
* alignment should remain aligned, except that the last step discards very
* short alignments (<= TOO_SHORT bp).
*
* Unfortunately, trimming alignments invalidates information about their score
* as well as the percent identity of the first and last gap-free segment.
*/

#define VERSION 1

#include "lib.h"

enum {
  BUF_SIZE=500,
  TOO_SHORT=15,	/* discard alignments not longer than this */
};

/* Gap-free segments of an alignment are stored in a doubly linked list. */
typedef struct seg {
	int beg1, beg2, end1, end2, pct;
	struct seg *next, *prev;
} SEG;

/* Each alignment is stored as a header and a list of segments.  Each alignment
* is in two sorted lists: a list of all alignments in the same lav block,
* sorted by their current value of beg1 (beg1 is raised if the alignment is
* trimmed at the front) and a list of ALL alignments, sorted by its initial
* value of beg1. */
typedef struct align {
	int beg1, beg2, end1, end2, score;
	int orig_beg1;
	SEG *first, *last;
	struct align *next, *next_in_lav;
} ALIGN;

/* The input is stored as a linked list of arbitrary lines, with interspersed
alignments */
typedef struct line_rec {
	char *line;
	ALIGN *align;
	struct line_rec *next;
} LINE_REC, *LINE_PTR;

void print_align(ALIGN *a)
{
	SEG *s;

	if (a->end1 - a->beg1 >= TOO_SHORT) {
		printf("a {\n");
		printf("  s %d\n", a->score);
		printf("  b %d %d\n", a->beg1, a->beg2);
		printf("  e %d %d\n", a->end1, a->end2);
		for (s = a->first; s; s = s->next)
			printf("  l %d %d %d %d %d\n",
			  s->beg1, s->beg2, s->end1, s->end2, s->pct);
		printf("}\n");
	}
}

int compar(const void *a, const void *b)
{
	return (*((ALIGN **)a))->beg1 - (*((ALIGN **)b))->beg1;
}

void print_sorted(ALIGN *a)
{
	ALIGN *p, **al;
	int n, n_align;

	for (n_align = 0, p = a; p; ++n_align, p = p->next_in_lav)
		;

	al = ckalloc(n_align*sizeof(ALIGN *));
	for (n = 0, p = a; p; p = p->next_in_lav) {
		if (n >= n_align)
			fatal("print_sorted: too many alignments.");
		al[n++] = p;
	}
	if (n != n_align)
		fatal("print_sorted: n != n_align");
	/* sort alignments by beg1 */
	qsort((void *)al, n_align, sizeof(ALIGN *), compar);
	for (n = 0; n < n_align; ++n)
		print_align(al[n]);
	free(al);
}

void print_lines(LINE_PTR p, char *cmd)
{
	char *s;

	printf("%s", p->line);
	p = p->next;
	printf("%s", p->line);
	p = p->next;
	if (strstr(p->line, "blastz") && cmd != NULL) {
		if ((s = strchr(p->line, '\n')) != NULL)
			*s = '\0';
		printf("%s    (processed by %s)\n", p->line, cmd);

	} else
		printf("%s", p->line);
	p = p->next;
	for ( ; p; p = p->next) {
		if (p->line)
			printf("%s", p->line);
		else
			print_sorted(p->align);
	}
}

/* approximate 100 times number of matches in alignment from b to e in seq1 */
int match100(ALIGN *a, int b, int e)
{
	SEG *s;
	int m100, m, M;

	for (m100 = 0, s = a->first; s && s->beg1 <= e; s = s->next) {
		m = MAX(s->beg1, b);
		M = MIN(s->end1, e);
		if (M >= m)
			m100 += s->pct * (M - m + 1);
	}
	return m100;
}

/* reset first aligned position in seq1 to x */
void trim_front(ALIGN *a, int x)
{
	SEG *s;

	while (a->first && a->first->end1 < x) {
		/* discard a's first segment */
		s = a->first;
		a->first = a->first->next;
		free(s);
	}
	if (a->first && a->first->beg1 < x) {
		/* trim the segment to start at x */
		a->first->beg2 += (x - a->first->beg1);
		a->first->beg1 = x;
	}
	if (a->first == NULL) {
		a->last = NULL;
		a->end1 = a->beg1 - 1;
	} else {
		a->first->prev = NULL;
		a->beg1 = a->first->beg1;
		a->beg2 = a->first->beg2;
	}
}

/* reset last aligned position in seq1 to x */
void trim_rear(ALIGN *a, int x)
{
	SEG *s;

	while (a->last && a->last->beg1 > x) {
		/* discard a's last segment */
		s = a->last;
		a->last = a->last->prev;
		free(s);
	}
	if (a->last && a->last->end1 > x) {
		/* trim the segment to end at x */
		a->last->end2 += (x - a->last->end1);
		a->last->end1 = x;
	}
	if (a->last == NULL) {
		a->first = NULL;
		a->end1 = a->beg1 - 1;
	} else {
		a->last->next = NULL;
		a->end1 = a->last->end1;
		a->end2 = a->last->end2;
	}
}

/* copy the gap-free segments of alignment a to d */
void copy_segs(ALIGN *a, ALIGN *d)
{
	SEG *as, *ds, *new;

	if (a->first == NULL) {
		d->first = d->last = NULL;
		return;
	}
	d->first = NULL;
	for (as = a->first, ds = NULL; as; as = as->next, ds = new) {
		new = ckalloc(sizeof(SEG));
		new->beg1 = as->beg1;
		new->beg2 = as->beg2;
		new->end1 = as->end1;
		new->end2 = as->end2;
		new->pct = as->pct;
		if (ds == NULL) {	/* first segment */
			new->prev = NULL;
			d->first = new;
		} else {
			new->prev = ds;
			ds->next = new;
		}
	}
	ds->next = NULL;
	d->last = ds;
}

/* replace alignment by its prefix ending at position x in seq1, and its
*  suffix starting at y */
void split_align(ALIGN *a, int x, int y)
{
	ALIGN *p, *copy = ckalloc(sizeof(ALIGN));

	copy->beg1 = a->beg1;
	copy->beg2 = a->beg2;
	copy->end1 = a->end1;
	copy->end2 = a->end2;
	copy->score = a->score;
	copy_segs(a, copy);
	trim_front(copy, y);
	copy->orig_beg1 = y;

	/* insert in list of alignments in the same lav block (sort later) */
	copy->next_in_lav = a->next_in_lav;
	a->next_in_lav = copy;

	/* insert in list of all alignments, sorted by orig_big1 */
	for (p = a; p->next && p->next->orig_beg1 < y; p = p->next)
		;
	copy->next = p->next;
	p->next = copy;

	trim_rear(a, x);
}

/* enforce single coverage on a pair of potentially overlapping alignments */
void overlap(ALIGN *a, ALIGN *b)
{
	ALIGN *t;
	int beg, end;

	/* sort by beg1 */
	if (a->beg1 > b->beg1) {
		t = a; a = b; b = t;
	}
	if (a->end1 < b->beg1 || b->end1 - b->beg1 < TOO_SHORT)
		return;
	if (b->end1 <= a->end1) {   /* a's projection on seq1 contains b's */
		beg = b->beg1;
		end = b->end1;
		if (match100(a, beg, end) >= match100(b, beg, end))
			b->end1 = b->beg1 - 1;	/* discard b */
		else
			split_align(a, beg - 1, end + 1);
	} else {
		/* Here, the domains of a and b "properly overlap",
		*  with a->beg1 <= b->beg1 and a->end1 < b->end1.
		*  Determine begin and end of the overlap in seq1 and trim
		*  the one with the lower percent identity in the overlap */
		beg = b->beg1;
		end = a->end1;
		if (match100(a, beg, end)  > match100(b, beg, end))
			trim_front(b, end + 1);
		else
			trim_rear (a, beg - 1);
	}
}

int get_lines(char *file, LINE_PTR *first_line_addr) {
	FILE *ap;
	char buf[BUF_SIZE];
	LINE_PTR last_line, new;
	ALIGN *newal, *prev_in_lav;
	SEG *newseg;
	int nalign;

	if (file == NULL)
		ap = stdin;
	else
		ap = ckopen(file, "r");
	if ((fgets(buf, BUF_SIZE, ap)) == NULL || strcmp(buf, "#:lav\n"))
		fatal("Not an alignment file.");
	*first_line_addr = last_line = ckalloc(sizeof(LINE_REC));
	prev_in_lav = last_line->align = NULL;
	last_line->line = copy_string(buf);
	nalign = 0;
	while (fgets(buf, BUF_SIZE, ap)) {
		if (strncmp(buf, "a {", 3)) {
			new = ckalloc(sizeof(LINE_REC));
			last_line = last_line->next = new;
			last_line->line = copy_string(buf);
			prev_in_lav = last_line->align = NULL;
		} else {
			++nalign;
			newal = ckalloc(sizeof(ALIGN));
			if (prev_in_lav == NULL) {
				new = ckalloc(sizeof(LINE_REC));
				last_line = last_line->next = new;
				last_line->line = NULL;
				last_line->align = newal;
			} else
				prev_in_lav->next_in_lav = newal;
			newal->next_in_lav = NULL;
			prev_in_lav = newal;
			if  (fgets(buf, BUF_SIZE, ap) == NULL ||
			     sscanf(buf, "  s %d", &(newal->score)) != 1) 
				fatalf("no score: %s", buf);
			if  (fgets(buf, BUF_SIZE, ap) == NULL ||
			     sscanf(buf, "  b %d %d", &(newal->beg1),
						      &(newal->beg2)) != 2) 
				fatalf("no beginning: %s", buf);
			newal->orig_beg1 = newal->beg1;
			if  (fgets(buf, BUF_SIZE, ap) == NULL ||
			     sscanf(buf, "  e %d %d", &(newal->end1),
						      &(newal->end2)) != 2) 
				fatalf("no ending: %s", buf);
			newal->first = newal->last = NULL;
			while (fgets(buf, BUF_SIZE, ap) && buf[0] != '}') {
				newseg = ckalloc(sizeof(SEG));
				if (sscanf(buf, "  l %d %d %d %d %d",
				    &(newseg->beg1), &(newseg->beg2),
				    &(newseg->end1), &(newseg->end2),
				    &(newseg->pct)) != 5)
					fatalf("Cannot get segment: %s", buf);
				if (newal->first == NULL) {
					newal->first = newseg;
					newseg->prev = newseg->next = NULL;
				} else {
					newseg->prev = newal->last;
					newal->last->next = newseg;
				}
				newseg->next = NULL;
				newal->last = newseg;
			}
		}
	}
	last_line->next = NULL;

	if (ap != stdin)
		fclose(ap);
	return nalign;
}

int main(int argc, char **argv) {
	int i, n, n_align;
	ALIGN **al, *a, *b, *first_al;
	LINE_PTR first_line, p;
	char cmd[100];

	sprintf(cmd, "single_cov.v%d", VERSION);
	argv0 = cmd;
	if (argc < 1 || argc > 2)
		fatalf("optional arg = blastz-output");
	
	n_align = get_lines(argc == 2 ? argv[1] : NULL, &first_line);

	if (n_align < 1) {
		/* fatal("There were no alignments."); */
		print_lines(first_line, NULL);
		return 0;
	}

	al = ckalloc(n_align*sizeof(ALIGN *));
	for (n = 0, p = first_line; p; p = p->next)
		for (a = p->align; a; a = a->next_in_lav) {
			if (n >= n_align)
				fatal("Too many alignments.");
			al[n++] = a;
		}
	if (n != n_align)
		fatal("n != n_align");
	/* sort alignments by beg1 */
	qsort((void *)al, n_align, sizeof(ALIGN *), compar);

	/* put alignments into a linked list */
	for (i = 0; i < n_align - 1; ++i)
		al[i]->next = al[i+1];
	al[n_align-1]->next = NULL;

	first_al = al[0];
	free(al);

	/* adjust each pair of potentially overlapping alignments */
	for (a = first_al; a; a = a->next) {
		if (a->end1 - a->beg1 < TOO_SHORT)
			continue;
		for (b = a->next; b && b->orig_beg1 <= a->end1; b = b->next)
			overlap(a, b);
	}

	print_lines(first_line, cmd);
	return 0;
}
