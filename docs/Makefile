# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
PAPER         ?=
BUILDDIR      ?= _build

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .
.PHONY: help Makefile

# Put it first so that "make" without argument is still useful.
help:
	@$(SPHINXBUILD) -M help $(ALLSPHINXOPTS) $(BUILDDIR)

.DEFAULT_GOAL := help

html:
	@$(SPHINXBUILD) -M html $(ALLSPHINXOPTS) $(BUILDDIR)

clean:
	@$(SPHINXBUILD) -M clean $(ALLSPHINXOPTS) $(BUILDDIR)

livehtml:
	sphinx-autobuild -b html $(ALLSPHINXOPTS) . $(BUILDDIR)/html

.PHONY: help html clean livehtml

