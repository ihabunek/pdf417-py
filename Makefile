default :
	python setup.py bdist
	python setup.py bdist_wheel --universal

clean :
	rm -rf build dist *.egg-info MANIFEST
