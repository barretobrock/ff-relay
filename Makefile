PROJECT		:= ff-relay
PY_LIB_NAME := ffrelay
VENV_NAME	:= ff_relay311
MAIN_BRANCH := main

check-ppm-path:
	@[  "${PPM_ABS_PATH}" ] && echo "PPM path set: ${PPM_ABS_PATH}" || (echo "PPM path not set" && exit 1)
bump-patch: check-ppm-path
	sh "${PPM_ABS_PATH}" -d --cmd bump --level patch --project $(PROJECT) --lib $(PY_LIB_NAME) --venv $(VENV_NAME) --main-branch $(MAIN_BRANCH)
bump-minor: check-ppm-path
	sh "${PPM_ABS_PATH}" -d --cmd bump --level minor --project $(PROJECT) --lib $(PY_LIB_NAME) --venv $(VENV_NAME) --main-branch $(MAIN_BRANCH)
bump-major: check-ppm-path
	sh "${PPM_ABS_PATH}" -d --cmd bump --level major --project $(PROJECT) --lib $(PY_LIB_NAME) --venv $(VENV_NAME) --main-branch $(MAIN_BRANCH)
pull: check-ppm-path
	sh "${PPM_ABS_PATH}" -d --cmd pull --project $(PROJECT) --lib $(PY_LIB_NAME) --venv $(VENV_NAME) --main-branch $(MAIN_BRANCH)
push: check-ppm-path
	sh "${PPM_ABS_PATH}" -d --cmd push --project $(PROJECT) --lib $(PY_LIB_NAME) --venv $(VENV_NAME) --main-branch $(MAIN_BRANCH)
debug:
	python3 run_debug.py
check:
	pre-commit run --all-files
install:
	# First-time install - use when lock file is stable
	poetry install -v
update:
	# Update lock file based on changed reqs
	poetry update -v
install-dev:
	pre-commit install
test:
	tox
rebuild-test:
	tox --recreate -e py311
