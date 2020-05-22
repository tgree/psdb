PYPSDB_VERS := 0.9.0
PYPSDB_DEPS := \
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
		psdb/targets/stm32h7/*.py		\
		psdb/targets/stm32g0/*.py   	\
		psdb/targets/stm32g4/*.py   	\
		psdb/targets/stm32wb55/*.py		\
		psdb/targets/stm32wb55/ipc/*.py \
		psdb/util/*.py

.PHONY: all
all: pypsdb pypsdb3

.PHONY: clean
clean:
	rm -rf dist pypsdb.egg-info
	find . -name "*.pyc" | xargs rm

.PHONY: test
test:
	python3 -m flake8 psdb

.PHONY: pypsdb
pypsdb: dist/pypsdb-$(PYPSDB_VERS)-py2-none-any.whl

.PHONY: pypsdb3
pypsdb3: dist/pypsdb-$(PYPSDB_VERS)-py3-none-any.whl

.PHONY: install
install: pypsdb
	sudo pip uninstall -y pypsdb
	sudo pip install dist/pypsdb-$(PYPSDB_VERS)-py2-none-any.whl

.PHONY: install3
install3: pypsdb3
	sudo pip3 uninstall -y pypsdb
	sudo pip3 install dist/pypsdb-$(PYPSDB_VERS)-py3-none-any.whl

.PHONY: uninstall
uninstall:
	sudo pip uninstall pypsdb

.PHONY: uninstall3
uninstall3:
	sudo pip3 uninstall pypsdb

dist/pypsdb-$(PYPSDB_VERS)-py2-none-any.whl: $(PYPSDB_DEPS)
	python setup.py sdist bdist_wheel

dist/pypsdb-$(PYPSDB_VERS)-py3-none-any.whl: $(PYPSDB_DEPS)
	python3 setup.py sdist bdist_wheel
