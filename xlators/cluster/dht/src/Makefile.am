xlator_LTLIBRARIES = dht.la nufa.la switch.la
if BUILD_GFDB
   xlator_LTLIBRARIES += tier.la
endif

AM_CFLAGS = -Wall $(GF_CFLAGS)

xlatordir = $(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/cluster

dht_common_source = dht-layout.c dht-helper.c dht-linkfile.c dht-rebalance.c \
	dht-selfheal.c dht-rename.c dht-hashfn.c dht-diskusage.c \
	dht-common.c dht-inode-write.c dht-inode-read.c dht-shared.c \
	$(top_builddir)/xlators/lib/src/libxlator.c

dht_la_SOURCES = $(dht_common_source) dht.c

nufa_la_SOURCES = $(dht_common_source) nufa.c
switch_la_SOURCES = $(dht_common_source) switch.c
tier_la_SOURCES = $(dht_common_source) tier.c

dht_la_LDFLAGS = -module -avoid-version
dht_la_LIBADD = $(top_builddir)/libglusterfs/src/libglusterfs.la

nufa_la_LDFLAGS = -module -avoid-version
nufa_la_LIBADD = $(top_builddir)/libglusterfs/src/libglusterfs.la

switch_la_LDFLAGS = -module -avoid-version
switch_la_LIBADD = $(top_builddir)/libglusterfs/src/libglusterfs.la

tier_la_CFLAGS = $(AM_CFLAGS) $(SQLITE_CFLAGS)
tier_la_LDFLAGS = -module -avoid-version
tier_la_LIBADD = $(top_builddir)/libglusterfs/src/libglusterfs.la\
		 $(top_builddir)/libglusterfs/src/gfdb/libgfdb.la

noinst_HEADERS = dht-common.h dht-mem-types.h dht-messages.h dht-helper.h tier.h\
	$(top_builddir)/xlators/lib/src/libxlator.h

AM_CPPFLAGS = $(GF_CPPFLAGS) -I$(top_srcdir)/libglusterfs/src \
	-I$(top_srcdir)/libglusterfs/src/gfdb \
	-I$(top_srcdir)/xlators/lib/src

CLEANFILES =

uninstall-local:
	rm -f $(DESTDIR)$(xlatordir)/distribute.so

install-data-hook:
	ln -sf dht.so $(DESTDIR)$(xlatordir)/distribute.so

if UNITTEST
CLEANFILES += *.gcda *.gcno *_xunit.xml
noinst_PROGRAMS =
TESTS =

dht_layout_unittest_CPPFLAGS = $(AM_CPPFLAGS)
dht_layout_unittest_SOURCES = unittest/dht_layout_unittest.c \
                              unittest/dht_layout_mock.c \
                              dht-layout.c
dht_layout_unittest_CFLAGS = $(AM_CFLAGS) $(UNITTEST_CFLAGS)
dht_layout_unittest_LDFLAGS = $(UNITTEST_LDFLAGS)
noinst_PROGRAMS += dht_layout_unittest
TESTS += dht_layout_unittest
endif
