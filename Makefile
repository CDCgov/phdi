.PHONY: docs
docs:
	sphinx-apidoc -o docs/sphinx/_source ./phdi
	cd docs/sphinx && make singlehtml

.PHONY: test
test:
	pytest
	black .
	flake8
