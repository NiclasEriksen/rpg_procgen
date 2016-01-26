PYTHON ?= python
top_srcdir := `pwd`
PYTHONPATH ?= $(top_srcdir)
SUBDIRS = \
	$(top_srcdir)/utils \
	$(top_srcdir)/test/resources \
	$(top_srcdir)/test/util \
	$(top_srcdir)/test \
	$(top_srcdir)/doc

INTERPRETERS = python2.7 python3.2 python3.3 pypy2.0

all: clean docs

clean:
	@echo "Cleaning up in $(top_srcdir)/ ..."
	@rm -f *.cache *.core *~ MANIFEST *.pyc *.orig
	@rm -rf __pycache__
	@rm -rf build dist doc/html

	@for dir in $(SUBDIRS); do \
		if test -f $$dir/Makefile; then \
			make -C $$dir clean; \
		else \
			cd $$dir; \
			echo "Cleaning up in $$dir..."; \
			rm -f *~ *.cache *.core *.pyc *.orig *py.class; \
			rm -rf __pycache__; \
		fi \
	done

docs:
	@echo "Creating docs package"
	@rm -rf doc/html
	@cd doc && PYTHONPATH=$(PYTHONPATH) make html
	@mv doc/_build/html doc/html
	@rm -rf doc/_build
	@cd doc && make clean

testall:
	@for interp in $(INTERPRETERS); do \
		PYTHONPATH=$(PYTHONPATH) $$interp -B -m test.util.runtests; \
	done
