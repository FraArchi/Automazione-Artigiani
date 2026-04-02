.PHONY: dashboard dashboard-open reviewer test

dashboard:
	./scripts/start_local_dashboard.sh

dashboard-open:
	OPEN_BROWSER=1 ./scripts/start_local_dashboard.sh

reviewer:
	./venv/bin/python hermes_reviewer.py --base-url http://127.0.0.1:8010 --watch 30

test:
	./venv/bin/python -m pytest -q
