.PHONY : clean java-requirement save-reqs

# test: I should also run mypy
test : venv java-requirement
	source venv/bin/activate && py.test pdart

java-requirement :
	@if ! [ -x "$(shell command -v java)" ]; then \
	    echo "**** Java must be installed to run PDART tests ****" ; \
	    exit 1; \
	fi

venv : requirements.txt
	virtualenv --no-site-packages -p python2.7 $@
	# pyfits requires numpy to be installed first; dunno why
	source venv/bin/activate && pip install numpy==1.16.4
	source venv/bin/activate && pip install -r requirements.txt

save-reqs :
	source venv/bin/activate && pip freeze > requirements.txt

#
# To use/run mypy
#
mypy : mypy-venv
	source mypy-venv/bin/activate && mypy --py2 .

mypy-venv : requirements-mypy.txt
	virtualenv --no-site-packages -p python3 $@
	source mypy-venv/bin/activate && pip install -r requirements-mypy.txt

clean :
	find . -name '*~' -delete
	find . -name '#*' -delete
	find . -name '*.pyc' -delete
	-rm -rf apidocs dist MANIFEST
	-rm -rf venv
	-rm -rf mypy-venv