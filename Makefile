CC = gcc
CFLAGS = -std=c11 -O2 -g -Wall -Wextra -Werror -pedantic
PYTHON = python3

.PHONY: all test experiment presentation clean
all: build/scheduler_sim build/linux_baseline

build:
	mkdir -p $@

build/scheduler_sim: src/scheduler_sim.c | build
	$(CC) $(CFLAGS) $< -o $@

build/linux_baseline: src/linux_baseline.c | build
	$(CC) $(CFLAGS) $< -o $@

test: all
	$(PYTHON) -m unittest discover -s tests -v

experiment: all
	$(PYTHON) scripts/run_experiments.py

presentation:
	$(PYTHON) scripts/build_week2_presentation.py

clean:
	rm -rf build
