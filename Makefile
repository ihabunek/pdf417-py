default : clean dist

phony: test

test:
	pytest

htmlcov:
	pytest --cov=pdf417gen --cov-report=html

dist :
	@echo "\nMaking source"
	@echo "-------------"
	@python setup.py sdist

	@echo "\nMaking wheel"
	@echo "-------------"
	@python setup.py bdist_wheel --universal

	@echo "\nDone."

clean :
	rm -rf build dist *.egg-info MANIFEST htmlcov

publish :
	twine upload dist/*
