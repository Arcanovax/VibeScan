UV_RUN	= uv run

ARGS	?=

run: install
	@$(UV_RUN) -m srcs $(ARGS)

install:
	uv sync

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf dist

fclean: clean
	rm -rf .venv

.PHONY: run clean fclean install
