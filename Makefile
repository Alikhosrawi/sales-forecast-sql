PY ?= python

.PHONY: setup data run sample test leak screenshot

setup:      ## install dependencies
	$(PY) -m pip install -r requirements.txt

data:       ## regenerate the synthetic CRM data (seed 42)
	$(PY) generate_data.py

run:        ## forecast the latest week -> output/
	$(PY) run.py

sample:     ## rebuild output/sample/ (last week + this week)
	$(PY) run.py --sample

test:       ## run the test suite
	$(PY) -m pytest

leak:       ## scan tracked files and commit messages
	bash scripts/leak_scan.sh

screenshot: ## re-render docs/images/weekly_report.png (needs markdown + wkhtmltoimage)
	$(PY) scripts/screenshot_report.py
