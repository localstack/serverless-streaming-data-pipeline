import os

import constants
from aws_cdk import App, Fn
from data_pipeline_stack import DataPipelineStack
from external_test_resources_stack import ExternalTestResourcesStack


def main():
    port = 5111
    host = os.getenv("TINYBIRD_MOCK_HOST") or "host.docker.internal"
    tinybird_mock_path = "tinybird"
    tinybird_mock_url = f"http://{host}:{port}/{tinybird_mock_path}"
    app = App()

    external_resources = ExternalTestResourcesStack(
        app,
        "ExternalTestResourcesStack",
        env=constants.ENV_LOCAL,
    )

    data_pipeline = DataPipelineStack(
        app,
        "DataPipelineStack",
        env=constants.ENV_LOCAL,
        monitored_log_group_arn=Fn.import_value("test-logger-log-group-arn"),
        tinybird_auth_token="dummy value",
        tinybird_url=tinybird_mock_url,
    )
    data_pipeline.add_dependency(external_resources)

    app.synth()


if __name__ == "__main__":
    main()
