LZMAURL=http://tukaani.org/xz/xz-5.2.2.tar.bz2
LZMASRC=xz-5.2.2
LZMACFG=--prefix=/usr --disable-shared --disable-xz --disable-xzdec --disable-lzmadec --disable-lzmainfo --disable-lzma-links --disable-scripts --disable-doc --disable-dependency-tracking --disable-nls --disable-rpath --without-libiconv-prefix --without-libintl-prefix --enable-silent-rules
TOPDIR=$(shell pwd -P)

all: pbzx

pbzx: pbzx.c liblzma/usr/lib/liblzma.a
	gcc -Wall -o pbzx -Iliblzma/usr/include -Lliblzma/usr/lib -llzma -lxar pbzx.c

liblzma/usr/lib/liblzma.a: $(LZMASRC)/config.h
	mkdir -p liblzma
	cd $(LZMASRC) && make DESTDIR=$(TOPDIR)/liblzma install

clean:
	rm -rf liblzma pbzx

extraclean: clean
	rm -rf $(LZMASRC)

$(LZMASRC)/config.h: $(LZMASRC)/*.in
	cd $(LZMASRC) && ./configure $(LZMACFG)

$(LZMASRC)/*.in: download

download:
	test -d $(LZMASRC) || curl -L $(LZMAURL) | tar xjf -

.PHONY: download
