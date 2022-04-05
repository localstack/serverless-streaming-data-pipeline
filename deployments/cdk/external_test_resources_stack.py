from os import path

from aws_cdk import ArnFormat, CfnOutput, Duration, Stack, aws_lambda
from constructs import Construct


class ExternalTestResourcesStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        test_logger_lambda = aws_lambda.Function(
            self,
            "test_logger",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="test_logger.handler",
            code=aws_lambda.Code.from_asset(
                path.join(
                    path.realpath(path.dirname(__file__)),
                    "../..",
                    "test_logger_pkg.zip",
                )
            ),
            timeout=Duration.seconds(2),
        )

        test_logger_log_group_arn = self.format_arn(
            resource="log-group",
            service="logs",
            account=self.account,
            partition=self.partition,
            region=self.region,
            arn_format=ArnFormat.COLON_RESOURCE_NAME,
            resource_name=f"/aws/lambda/{test_logger_lambda.function_name}:*",
        )

        CfnOutput(
            self,
            "test_logger_lambda_name",
            value=test_logger_lambda.function_name,
            export_name="test-logger-lambda-name",
        )
        CfnOutput(
            self,
            "test_logger_log_group_arn",
            value=test_logger_log_group_arn,
            export_name="test-logger-log-group-arn",
        )
