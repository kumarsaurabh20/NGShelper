// mini-maf.c - Read/write maf format.  Stolen from Jim Kent & seriously abused
#include "lib.h"
#include "maf.h"

struct mafFile *mafOpen(char *fileName, int verbose) {
	struct mafFile *mf;
	FILE *fp;
	char buf[500], *s;

	mf = ckalloc(sizeof(struct mafFile));
	mf->next = NULL;
	fp = mf->fp = ckopen(fileName, "r");
	if (fgets(buf, 500, fp) == NULL)
		fatalf("empty file %s", fileName);
	if (sscanf(buf, "##maf version=%d", &(mf->version)) != 1)
		fatalf("improper maf header line: %s", buf);
	if ((s = strstr(buf, "scoring=")) != NULL)
		mf->scoring = copy_string(s+8);
	else
		mf->scoring = NULL;
	mf->alignments = NULL;
	mf->fileName = copy_string(fileName);
	mf->line_nbr = 0;
	mf->verbose = verbose;
	return mf;
}

/* ------- start of code to read arbitrarily long lines and echo comments --- */

static int need(unsigned long n, char **linep, unsigned long *np) {
	char *p;

	if (*np <= n) {
		*np += (*np >> 5) + 16;
		if ((p = realloc(*linep, *np)) == 0)
			return -1;
		*linep = p;
	}
	return 0;
}

static unsigned long get_line(char **linep, unsigned long *np, FILE *fp) {
	int ch;
	unsigned long n = 0;

	while ((ch = fgetc(fp)) != -1) {
		if (need(n+1, linep, np))
			return -1;
		(*linep)[n++] = ch;
		if (ch == '\n')
			break;
	}
	if (need(n+1, linep, np))
		return -1;
	(*linep)[n] = 0;
	if (n == 0 && ch == -1)
		return -1;
	return n;
}

static unsigned long get_maf_line(char **linep, unsigned long *np, FILE *fp,
  struct mafFile *mf) {
	long nn;

	while ((nn = get_line(linep, np, fp)) > 1) {
		mf->line_nbr++;
		//if  ((*linep)[0] == '#' && (*linep)[1] != '#') {
		if  ((*linep)[0] == '#') {
			if (mf->verbose)
				printf("%s", *linep);
		} else break;
	}
	return nn;
}

/* ------- end of code to read arbitrarily long lines and echo comments --- */

struct mafAli *mafNext(struct mafFile *mf) {
	FILE *fp = mf->fp;
	struct mafAli *a = ckalloc(sizeof(struct mafAli));
	struct mafComp *c, *last;
	char buf[500];
	static char *line = NULL;
	static unsigned long nb = 0;
	int i, len;

	if ((len = get_maf_line(&line, &nb, fp, mf)) == -1) {
		fclose(fp);
		mf->fp = NULL;
		return NULL;
	}
	if (strncmp(line, "a score=", 8) == 0)
        	a->score = atof(line+8);
	else if (line[0] == 'a')
		a->score = 0.0;
	else
		fatalf("Expecting 'a score=xxx' in file %s, line %d:\n%s",
		  mf->fileName, mf->line_nbr, line);
        a->score = atof(line+8);
	a->textSize = 0;
	last = a->components = NULL;
	a->next = NULL;
	while ((len = get_maf_line(&line, &nb, fp, mf)) != -1 &&
	  line[0] != '\n') {
// if (line[0] != 'i' || line[0] == 'e') continue;
		c = ckalloc(sizeof(struct mafComp));
		c->text = ckalloc(len*sizeof(char));
		if (sscanf(line, "s %s %d %d %c %d %s",
		  buf, &(c->start), &(c->size), &(c->strand),
		  &(c->srcSize), c->text) != 6)
			fatalf("bad component in file %s, line %d:\n%s",
			  mf->fileName, mf->line_nbr, buf);
		c->src = copy_string(buf);
		c->next = NULL;
		if (a->components == NULL) {
			a->textSize = strlen(c->text);
			a->components = c;
		} else {
			if (a->textSize != (signed)strlen(c->text))
				fatalf("line %d of %s: inconsistent row size",
				  mf->line_nbr, mf->fileName);
			last->next = c;
		}
		last = c;
		/* Do some sanity checking. */
		if (c->srcSize <= 0 || c->size <= 0)
			fatalf("Size <= 0 at line %d of file %s:\n%s",
			  mf->line_nbr, mf->fileName, line);
		if (c->start < 0 || c->start + c->size > c->srcSize) {
			if (c != a->components) {
				c = a->components;
				fprintf(stderr,
				  "in maf entry with top row %s:%d len = %d,\n",
				  c->src, c->start, c->size);
			}
			fatalf("Bad coordinates at line %d of file %s:\n%s",
			  mf->line_nbr, mf->fileName, line);
		}
		for (i = len = 0; i < a->textSize; ++i)
			if (c->text[i] != '-')
				++len;
		if (len != c->size)
	    fatalf("Actual size %d, claimed size %d at line %d of file %s:\n%s",
	      len, c->size, mf->line_nbr, mf->fileName, line);

	}
	mf->line_nbr++;
	return a;
}

struct mafFile *mafReadAll(char *fileName, int verbose) {
	struct mafFile *mf = mafOpen(fileName, verbose);
	struct mafAli *a, *last;

	for (last = NULL; (a = mafNext(mf)) != NULL; last = a)
		if (last == NULL)
			mf->alignments = a;
		else
			last->next = a;
	return mf;
}

void mafWriteStart(FILE *f, char *scoring) {
	fprintf(f, "##maf version=1 scoring=%s\n", scoring);
}

static int digitsBaseTen(int x) {
	int digCount;

	if (x < 0)
		fatalf("digitsBaseTen: negative argument %d", x);
	for (digCount = 1; x >= 10; x /= 10, ++digCount)
		;
	return digCount;
}


void mafWrite(FILE *f, struct mafAli *a) {
	struct mafComp *c;
	int srcChars = 0, startChars = 0, sizeChars = 0, srcSizeChars = 0;

	fprintf(f, "a score=%3.1f\n", a->score);
	//fprintf(f, "a score=%f\n", a->score);
	/* Figure out length of each field. */
	for (c = a->components; c != NULL; c = c->next) {
		srcChars = MAX(srcChars, (signed int)strlen(c->src));
		startChars = MAX(startChars, digitsBaseTen(c->start));
		sizeChars = MAX(sizeChars,digitsBaseTen(c->size));
		srcSizeChars = MAX(srcSizeChars, digitsBaseTen(c->srcSize));
	}
	for (c = a->components; c != NULL; c = c->next) {
            	fprintf(f, "s %-*s %*d %*d %c %*d %s\n", 
    		  srcChars, c->src, startChars, c->start, sizeChars, c->size,
		  c->strand, srcSizeChars, c->srcSize, c->text);
    	}
	fprintf(f, "\n");	// blank separator line
}
	
void mafCompFree(struct mafComp **pComp) {
	struct mafComp *c = *pComp;

	if (c != NULL) {
		free(c->src);
		free(c->text);
		free(c);
		*pComp = NULL;
	}
}

void mafAliFree(struct mafAli **pAli) {
	struct mafAli *a = *pAli;
	struct mafComp *c, *next;

	for (c = a->components; c != NULL; c = next) {
		next = c->next;
		mafCompFree(&c);
	}
	free(a);
	*pAli = NULL;
}

void mafFileFree(struct mafFile **pmf) {
	struct mafFile *mf = *pmf;
	struct mafAli *a, *next;

	if (mf->fp != NULL)
		fclose(mf->fp);
	if (mf->scoring != NULL)
		free(mf->scoring);
	free(mf->fileName);
	for (a = mf->alignments; a != NULL; a = next) {
		next = a->next;
		mafAliFree(&a);
	}
	free(mf);
	*pmf = NULL;
}
