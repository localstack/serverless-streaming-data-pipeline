VENV_CMD ?= python3 -m venv
VENV_DIR ?= .venv
VENV_RUN = . $(VENV_DIR)/bin/activate
REGION = "us-east-2"

clean:
	rm -rf loader_package
	rm -rf kinesis_tinybird_loader_pkg.zip
	rm -rf test_logger_pkg.zip

build-tinybird-lambda:
	pip3 install -r lambdas/kinesis_tinybird_loader/requirements.txt --target ./loader_package
	cd loader_package ; zip -r ../kinesis_tinybird_loader_pkg.zip .
	zip -gj kinesis_tinybird_loader_pkg.zip lambdas/kinesis_tinybird_loader/kinesis_tinybird_loader.py

build-test-logger-lambda:
	zip -gj test_logger_pkg.zip lambdas/test_logger/test_logger.py

build-lambdas: build-tinybird-lambda build-test-logger-lambda

$(VENV_DIR)/bin/activate: setup.cfg setup.py
	$(VENV_CMD) $(VENV_DIR)
	$(VENV_RUN); pip install --upgrade pip setuptools wheel
	touch $(VENV_DIR)/bin/activate

venv: $(VENV_DIR)/bin/activate

lint:
	$(VENV_RUN); python -m pflake8 --show-source

lint-modified:
	$(VENV_RUN); python -m pflake8 --show-source `git ls-files -m | grep '\.py$$' | xargs`

format:
	$(VENV_RUN); python -m isort . ; python -m black .

format-modified:
	$(VENV_RUN); python -m isort `git ls-files -m | grep '\.py$$' | xargs`; python -m black `git ls-files -m | grep '\.py$$' | xargs`

init-precommit: install
	$(VENV_RUN); pre-commit install

install: venv
	$(VENV_RUN); pip install -e .[test,dev]

deploy-external-resources-local: clean install build-lambdas
	$(VENV_RUN); cd deployments/cdk; cdklocal bootstrap --app "python local_app.py" || true
	$(VENV_RUN); cd deployments/cdk; cdklocal deploy --app "python local_app.py" ExternalTestResourcesStack --require-approval never

invoke-test-logger-local:
	$(VENV_RUN); LAMBDA_NAME=$(shell awslocal cloudformation list-exports --region=$(REGION) --query="Exports[?Name=='test-logger-lambda-name'].Value" --no-paginate --output text); \
		$(VENV_RUN); awslocal lambda invoke --function-name $$LAMBDA_NAME /dev/stdout 2>/dev/null --region $(REGION) --payload '{"message": "hello world"}'

deploy-local: deploy-external-resources-local invoke-test-logger-local
	$(VENV_RUN); cd deployments/cdk; cdklocal deploy --app "python local_app.py" DataPipelineStack --require-approval never

test-integration: clean install
	$(VENV_RUN); pytest tests/integration

start-request-recorder:
	$(VENV_RUN); python tests/integration/mocks/tinybird_request_recorder.py


.PHONY: clean build-tinybird-lambda build-test-logger-lambda build-lambdas venv lint lint-modified format format-modified init-precommit install
