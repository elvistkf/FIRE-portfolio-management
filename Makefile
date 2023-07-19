install-dep:
	sudo apt-get install -y libmariadb-dev
	python -m pip install --upgrade pip
	pip install ruff pytest flake8
	if [ -f server/requirements.txt ]; then pip install -r server/requirements.txt; fi
lint-py:
	flake8 . --count --extend-ignore=E501 --show-source --statistics
test-py:
	PYTHONPATH=server/src pytest server/tests
deploy:
	docker compose up -d