PSDB_VERS := 0.9.0
PSDB_DEPS := \
		setup.py						\
		psdb/*.py						\
		psdb/block/*.py					\
		psdb/component/*.py				\
		psdb/cpus/*.py 					\
		psdb/elf/*.py					\
		psdb/probes/*.py				\
		psdb/probes/stlink/*.py			\
		psdb/probes/xds110/*.py			\
		psdb/targets/*.py				\
		psdb/targets/msp432/*.py		\
		psdb/targets/stm32/*.py			\
		psdb/targets/stm32h7/*.py		\
		psdb/targets/stm32g0/*.py   	\
		psdb/targets/stm32g4/*.py   	\
		psdb/targets/stm32wb55/*.py		\
		psdb/targets/stm32wb55/ipc/*.py \
		psdb/util/*.py

.PHONY: all
all: psdb

.PHONY: clean
clean:
	rm -rf dist psdb.egg-info
	find . -name "*.pyc" | xargs rm

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

dist/psdb-$(PSDB_VERS)-py3-none-any.whl: $(PSDB_DEPS)
	python3 setup.py sdist bdist_wheel
