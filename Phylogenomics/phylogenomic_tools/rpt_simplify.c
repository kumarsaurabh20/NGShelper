// get_rpts --  simplify a RepeatMasker .out file

#include "lib.h"

int main(int argc, char **argv) {
	FILE *fp;
	char buf[500], div[100], chr[100], type[100], class[100];
	int beg, end, n;

	if (argc != 2)
		fatal("arg : RepeatMasker.out");
	fp = ckopen(argv[1], "r");
	printf("#:rpt\n");
	while (fgets(buf, 500, fp))
		if ((n = sscanf(buf,
		   "%*s %s %*s %*s %s %d %d %*s %*s %s %s %*s %*s %*s %*s",
		   div, chr, &beg, &end, type, class)) >= 6 &&
		   beg > 0 &&
		   !strstr(class, "RNA") &&
		   !strstr(class, "Simple") &&
		   !strstr(class, "complexity") &&
		   !strstr(class, "Satellite")) {
			printf("%d %d %s %s %s\n",
			  beg, end, type, class, div);
		}
	return 0;
}
