PSDB_VERS := 1.0.2
PSDB_DEPS := \
	setup.cfg				\
	setup.py				\
	psdb/*.py				\
	psdb/block/*.py				\
	psdb/component/*.py			\
	psdb/cpus/*.py 				\
	psdb/devices/*.py			\
	psdb/devices/core/*.py			\
	psdb/devices/msp432/*.py		\
	psdb/devices/stm32/*.py			\
	psdb/devices/stm32g0/*.py		\
	psdb/devices/stm32g4/*.py		\
	psdb/devices/stm32h7/*.py		\
	psdb/devices/stm32u5/*.py		\
	psdb/devices/stm32wb55/*.py		\
	psdb/devices/stm32wb55/ipc/*.py 	\
	psdb/elf/*.py				\
	psdb/hexfile/*.py			\
	psdb/inspect_tool/*.py			\
	psdb/probes/*.py			\
	psdb/probes/stlink/*.py			\
	psdb/probes/xds110/*.py			\
	psdb/probes/xtswd/*.py			\
	psdb/targets/*.py			\
	psdb/targets/msp432/*.py		\
	psdb/targets/stm32g0/*.py		\
	psdb/targets/stm32g4/*.py		\
	psdb/targets/stm32h7/*.py		\
	psdb/targets/stm32u5/*.py		\
	psdb/targets/stm32wb55/*.py		\
	psdb/util/*.py
PYTHON := python3

.PHONY: all
all: psdb

.PHONY: clean
clean:
	rm -rf dist psdb.egg-info build
	find . -name "*.pyc" | xargs rm
	find . -name __pycache__ | xargs rm -r

.PHONY: test
test:
	$(PYTHON) -m flake8 psdb

.PHONY: psdb
psdb: dist/psdb-$(PSDB_VERS)-py3-none-any.whl

.PHONY: install
install: psdb
	sudo $(PYTHON) -m pip uninstall -y psdb
	sudo $(PYTHON) -m pip install dist/psdb-$(PSDB_VERS)-py3-none-any.whl

.PHONY: uninstall
uninstall:
	sudo $(PYTHON) -m pip uninstall psdb

.PHONY: publish
publish: psdb
	$(PYTHON) -m twine upload \
		dist/psdb-$(PSDB_VERS)-py3-none-any.whl \
		dist/psdb-$(PSDB_VERS).tar.gz

dist/psdb-$(PSDB_VERS)-py3-none-any.whl: $(PSDB_DEPS) Makefile
	$(PYTHON) setup.py --quiet sdist bdist_wheel
	$(PYTHON) -m twine check $@
