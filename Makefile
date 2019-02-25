.PHONY: test

RABBIT_CTL_URI?=http://guest:guest@localhost:15672
AMQP_URI?=amqp://guest:guest@localhost:5672


rst-lint:
	rst-lint README.rst
	rst-lint CHANGELOG.rst

flake8:
	flake8 nameko_eventlog_dispatcher test

test: flake8
	pytest test $(ARGS) \
		--rabbit-ctl-uri $(RABBIT_CTL_URI) \
		--amqp-uri $(AMQP_URI)

coverage: flake8 rst-lint
	coverage run --concurrency=eventlet \
		--source nameko_eventlog_dispatcher \
		-m pytest test $(ARGS) \
		--rabbit-ctl-uri $(RABBIT_CTL_URI) \
		--amqp-uri $(AMQP_URI)
	coverage report -m --fail-under 100

