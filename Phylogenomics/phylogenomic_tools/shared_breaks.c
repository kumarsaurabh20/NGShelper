// shared_breaks.c -- find chromosomal breaks shared by a subset of species

#include "lib.h"
#include "maf.h"

#define MIN_SCORE 50000
#define MAX_JUMP 20000
#define MAX_NAMES 1000

struct spec {
	char *spec, chr[100], next_chr[100], strand, next_strand;
	int end, next_start;
} S[MAX_NAMES];

int no_break, nbr_seq;

char *spec(char *src) {
	static char buf[1000];
	char *s;

	strcpy(buf, src);
	if ((s = strchr(buf, '.')) == NULL)
		fatalf("cannot find end of species name in '%s'", buf);
	*s = '\0';
	return buf;
}

char *chr(char *src) {
	static char buf[1000];
	char *s;

	if ((s = strchr(src, '.')) == NULL)
		fatalf("cannot find start of chromosome name in '%s'", src);
	strcpy(buf, s+1);
	return buf;
}

void get_names(char *filename) {
	FILE *fp = ckopen(filename, "r");
	char buf[500], *s;

	while (fgets(buf, 500, fp) && buf[0] != '-' && buf[0] != '_')  {
		if ((s = strchr(buf, '\n')) != NULL)
			*s = '\0';
		S[no_break++].spec = copy_string(buf);
	}
	if (buf[0] != '-' && buf[0] != '_')
		fatalf("%s has %d names but no line starting with '-'",
		  filename, no_break);
	nbr_seq = no_break;
	while (fgets(buf, 500, fp) != NULL) {
		if ((s = strchr(buf, '\n')) != NULL)
			*s = '\0';
		S[nbr_seq++].spec = copy_string(buf);
	}
	
	fclose(fp);
}

// find next block of score >= MIN_SCORE and with at least one species
//   i >= no_break
struct mafAli *find_next(struct mafFile *mf) {
	struct mafAli *a;
	struct mafComp *c;
	int i;

	while ((a = mafNext(mf)) != NULL) {
		if (a->score >= MIN_SCORE) {
			for (c = a->components; c != NULL; c = c->next) {
				for (i = no_break; i < nbr_seq; ++i)
				    if (same_string(spec(c->src), S[i].spec))
					return a;
			}
		}
		mafAliFree(&a);
		continue;
	}
	return NULL;
}

struct mafComp *pick_mafComp(struct mafAli *a, char *species) {
	struct mafComp *c;

	for (c = a->components;
	     c != NULL && !same_string(spec(c->src), species);
	     c = c->next)
		;
	return c;
}

int adjacent(struct mafComp *c, struct mafComp *d) {
	return same_string(c->src, d->src) && c->strand == d->strand &&
	   c->start + c->size <= d->start && c->start + MAX_JUMP > d->start;
}

int main(int argc, char **argv) {
	struct mafFile *mf;
	struct mafAli *a, *b;
	struct mafComp *c, *d;
	int i;

	if (argc != 3)
		fatal("args: align.maf name-file");

	get_names(argv[2]);

	mf = mafOpen(argv[1], 0);
	for (a = find_next(mf); (b = find_next(mf)) != NULL; a = b) {
		for (i = 0; i < nbr_seq; ++i)
			if ((c = pick_mafComp(a, S[i].spec)) == NULL ||
			    (d = pick_mafComp(b, S[i].spec)) == NULL ||
			    (i < no_break && !adjacent(c,d)) ||
			    (i >= no_break && adjacent(c,d)))
				break;
		if (i == nbr_seq) {
			c = a->components;
			printf("break at %d\n", c->start + c->size);
		}
		mafAliFree(&a);
	}

	return 0;
}
