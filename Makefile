PSDB_VERS := 0.9.4
PSDB_DEPS := \
		setup.cfg                           \
		setup.py							\
		psdb/*.py							\
		psdb/block/*.py						\
		psdb/component/*.py					\
		psdb/cpus/*.py 						\
		psdb/devices/*.py                   \
		psdb/devices/core/*.py				\
		psdb/devices/msp432/*.py            \
		psdb/devices/stm32/*.py             \
		psdb/devices/stm32g0/*.py   		\
		psdb/devices/stm32g4/*.py   		\
		psdb/devices/stm32h7/*.py			\
		psdb/devices/stm32wb55/*.py			\
		psdb/devices/stm32wb55/ipc/*.py 	\
		psdb/elf/*.py						\
		psdb/hexfile/*.py					\
		psdb/probes/*.py					\
		psdb/probes/stlink/*.py				\
		psdb/probes/xds110/*.py				\
		psdb/targets/*.py					\
		psdb/targets/msp432/*.py			\
		psdb/targets/stm32g0/*.py   		\
		psdb/targets/stm32g4/*.py   		\
		psdb/targets/stm32h7/*.py			\
		psdb/targets/stm32wb55/*.py			\
		psdb/util/*.py

.PHONY: all
all: psdb

.PHONY: clean
clean:
	rm -rf dist psdb.egg-info build
	find . -name "*.pyc" | xargs rm
	find . -name __pycache__ | xargs rm -r

.PHONY: test
test:
	python3 -m flake8 psdb

.PHONY: psdb
psdb: dist/psdb-$(PSDB_VERS)-py3-none-any.whl

.PHONY: install
install: psdb
	sudo pip3 uninstall -y psdb
	sudo pip3 install dist/psdb-$(PSDB_VERS)-py3-none-any.whl

.PHONY: uninstall
uninstall:
	sudo pip3 uninstall psdb

dist/psdb-$(PSDB_VERS)-py3-none-any.whl: $(PSDB_DEPS) Makefile
	python3 setup.py --quiet sdist bdist_wheel
	python3 -m twine check $@
