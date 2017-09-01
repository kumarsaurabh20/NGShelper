C=gcc -g -W -Wall

everything : rpt_simplify rpt_seek single_cov coding_exons coding_indels \
   shared_breaks coding_indels17

rpt_simplify : rpt_simplify.c
	$C rpt_simplify.c lib.c -o rpt_simplify

rpt_seek : rpt_seek.c
	$C rpt_seek.c lib.c -o rpt_seek

single_cov : single_cov.c
	$C single_cov.c lib.c -o single_cov

coding_exons : coding_exons.c
	$C coding_exons.c lib.c -o coding_exons

coding_indels : coding_indels.c
	$C coding_indels.c lib.c -o coding_indels

coding_indels17 : coding_indels17.c
	$C coding_indels17.c lib.c maf.c -o coding_indels17

shared_breaks : shared_breaks.c
	$C shared_breaks.c lib.c maf.c -o shared_breaks

tarfile :
	tar -c README Makefile species *.c *.h | gzip > phylogenomic.tar.gz

E1=/depot/data1/cache/ENCODE/JAN-2006/ENm001
Out=/depot/data1/cache/ENCODE/RepeatMasker
R=/depot/data1/cache/human/hg18/misc/RefSeq
A17=/depot/data1/cache/human/hg18/align/17-way
Align=/depot/data1/cache/human/hg18/align
Fly=/depot/data1/cache/fly/dm2/align/9way/maf

test1 :
	blastz $(E1)/human.ENm001.fa $(E1)/mouse.ENm001.fa B=0 C=2 H=2000 Y=2000 | single_cov > human.mouse.bz
	blastz $(E1)/human.ENm001.fa $(E1)/dog.ENm001.fa B=0 C=2 H=2000 Y=2000 | single_cov > human.dog.bz
	rpt_simplify $(Out)/human.ENm001.1.fa.out > human.rpts
	rpt_seek human mouse dog

test2 :
	coding_exons $R chr15 > exons
	gunzip -c $(Align)/armadillo/axtNet/chr15.axt.gz > armadillo.axt
	gunzip -c $(Align)/elephant/axtNet/chr15.axt.gz > elephant.axt
	cp $(Align)/opossum/axtNet/chr15.axt opossum.axt
	coding_indels exons armadillo.axt elephant.axt opossum.axt

test3 :
	shared_breaks $(Fly)/chr2R.maf species

test4 :
	coding_exons $R chr15 > exons
	coding_indels17 $(A17)/chr15.maf exons dasNov loxAfr monDom

bak :
	cp README Makefile *.c *.h SAVE.d
