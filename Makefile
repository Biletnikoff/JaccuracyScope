.PHONY: compile test lint install

compile:
	cd Display/Balls && gcc -fPIC -shared -o GNUball3.so exportme3.c -lm -Wall -Werror

test:
	python -m pytest tests/ -v

lint:
	ruff check Display/

install:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	$(MAKE) compile
