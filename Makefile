PROJECT		:= ff-relay
PY_LIB_NAME := ffrelay
VENV_NAME	:= ff_relay311
MAIN_BRANCH := main

check-ppm-path:
    # Check that the py package manager lib is installed and set up.
    ifeq ($(origin PPM_ABS_PATH), undefined)
        $(info PPM_ABS_PATH not set.)
        $(error You must set up Py Package Manager first.)
    else
        $(info PPM_ABS_PATH set.)
    endif
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
