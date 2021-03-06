// lib.h -- header file for some useful procedures

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <limits.h>   /* INT_MAX, INT_MIN, LONG_MAX, LONG_MIN, etc. */
#include <stdarg.h>

typedef unsigned char uchar;
typedef int bool;

extern char *argv0;

void print_argv0(void);
#ifdef __GNUC__     /* avoid some "foo might be used uninitialized" warnings */
	void fatal(const char *msg) __attribute__ ((noreturn));
	void fatalf(const char *fmt, ...) __attribute__ ((noreturn));
	void fatalfr(const char *fmt, ...) __attribute__ ((noreturn));
#else
	void fatal(const char *msg);
	void fatalf(const char *fmt, ...);
	void fatalfr(const char *fmt, ...);
#endif
FILE *ckopen(const char *name, const char *mode);
void *ckalloc(size_t amount);
bool same_string(const char *s, const char *t);
char *copy_string(const char *s);

#undef MAX
#define MAX(x,y) ((x) > (y) ? (x) : (y))
#undef MIN
#define MIN(x,y) ((x) < (y) ? (x) : (y))
