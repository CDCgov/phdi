.PHONY: docs
docs:
	sphinx-apidoc -o docs/_source phdi_transforms
	cd docs && make singlehtml

.PHONY: test
test:
	pytest
	black .
	flake8
