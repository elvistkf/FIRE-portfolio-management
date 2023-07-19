install-dep:
	sudo apt-get update
	sudo apt-get install -y libmariadb-dev
	python -m pip install --upgrade pip
	pip install ruff pytest
	if [ -f server/requirements.txt ]; then pip install -r server/requirements.txt; fi
lint-py:
	ruff check server
test-py:
	PYTHONPATH=server/src pytest server/tests
deploy:
	docker compose up -d