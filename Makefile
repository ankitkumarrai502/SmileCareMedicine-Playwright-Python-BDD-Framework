# SmileCareMedicine automation — common tasks.
# (Targets are scaffolded now; some depend on framework code that lands with the first module.)

.PHONY: help install browsers test test-smoke test-headed report clean lint

help:
	@echo "install     - create venv deps + install Playwright browsers"
	@echo "test        - run the full suite (headless)"
	@echo "test-smoke  - run @smoke tests only"
	@echo "test-headed - run visibly in a browser (Browser agent style)"
	@echo "report      - open the Allure report"
	@echo "lint        - ruff + black --check"
	@echo "clean       - remove reports/ and caches"

install:
	pip install -r requirements.txt
	playwright install

browsers:
	playwright install

test:
	pytest -n auto

test-smoke:
	pytest -m smoke

test-headed:
	HEADED=1 pytest --headed

# Allure HTML report. One-time tooling: a Java JRE/JDK + the Allure CLI must be installed
#   Windows:  winget install Microsoft.OpenJDK.17  &&  npm install -g allure-commandline
# `report`     -> quick: build a temp report and open it in the browser
# `report-html`-> persistent static site in reports/allure-report, then open it
report:
	allure serve reports/allure-results

report-html:
	allure generate reports/allure-results -o reports/allure-report --clean
	allure open reports/allure-report

lint:
	ruff check .
	black --check .

clean:
	rm -rf reports/allure-results reports/traces reports/videos .pytest_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
