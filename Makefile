PYTHON	= python
PYDOC	= pydoc
PYCS	= $(shell find . -name "*.pyc")
PYCACHE	= $(shell find . -name "__pycache__")
TARGET	= poke_bot.py
MODULE	= poke_bot
ARCHIVE	= $(shell basename `pwd`)
RESULT	= Result.txt
WORKDIR	= ./
PYLINT	= pylint
LINTRCF	= pylintrc.txt
LINTRST	= pylintresult.txt

all:
	@:

wipe: clean
	(cd ../ ; rm -f ./$(ARCHIVE).zip)

clean:
	@for each in ${PYCS} ; do echo "rm -f $${each}" ; rm -f $${each} ; done
	@for each in ${PYCACHE} ; do echo "rm -f $${each}" ; rm -rf $${each} ; done
	@if [ -e $(RESULT) ] ; then echo "rm -f $(RESULT)" ; rm -f $(RESULT) ; fi
	@if [ -e $(LINTRST) ] ; then echo "rm -f $(LINTRST)" ; rm -f $(LINTRST) ; fi
	@find . -name ".DS_Store" -exec rm {} ";" -exec echo rm -f {} ";"
	@xattr -cr ./

test: all
	@rm -f $(RESULT) ; touch $(RESULT)
	@tail -f $(RESULT) &
	$(PYTHON) ./$(TARGET)
	@for each in `ps -o pid,comm | grep tail | grep -v grep | awk '{ print $$1 }'` ; do kill $${each} ; done 

doc:
	$(PYDOC) ./$(TARGET)

zip: wipe
	(cd ../ ; zip -r ./$(ARCHIVE).zip ./$(ARCHIVE)/ --exclude='*/.svn/*')

pydoc:
	(sleep 3 ; open http://localhost:9999/$(MODULE).html) & $(PYDOC) -p 9999

lint: clean
	@if [ ! -e $(LINTRCF) ] ; then $(PYLINT) --generate-rcfile > $(LINTRCF) 2> /dev/null ; fi
	$(PYLINT) --rcfile=$(LINTRCF) `find . -name "*.py"` > $(LINTRST) ; less $(LINTRST)

