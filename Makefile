ENV_FILE = .env
run:
	uv run --env-file=$(ENV_FILE) main.py

test:
	uv run --env-file=$(ENV_FILE) pytest 
