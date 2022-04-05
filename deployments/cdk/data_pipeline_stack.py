from os import path

from aws_cdk import (
    Duration,
    Stack,
    aws_kinesis,
    aws_lambda,
    aws_lambda_event_sources,
    aws_logs,
    aws_logs_destinations,
)
from constructs import Construct


class DataPipelineStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        monitored_log_group_arn: str,
        tinybird_auth_token: str,
        tinybird_url: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        kinesis_stream = aws_kinesis.Stream(
            self,
            "data_pipeline_kinesis_stream",
            shard_count=1,
        )

        monitored_log_group = aws_logs.LogGroup.from_log_group_arn(
            self, "monitored_log_group", monitored_log_group_arn
        )
        monitored_log_group.add_subscription_filter(
            "monitored_log_group_cloudwatch_subscription",
            destination=aws_logs_destinations.KinesisDestination(kinesis_stream),
            filter_pattern=aws_logs.FilterPattern.all(
                aws_logs.FilterPattern.exists("$.event_class"),
                aws_logs.FilterPattern.exists("$.event_type"),
            ),
        )

        loader_lambda = aws_lambda.Function(
            self,
            "kinesis_tinybird_loader",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="kinesis_tinybird_loader.handler",
            code=aws_lambda.Code.from_asset(
                path.join(
                    path.realpath(path.dirname(__file__)),
                    "../..",
                    "kinesis_tinybird_loader_pkg.zip",
                )
            ),
            timeout=Duration.seconds(7),
            environment={
                "TINYBIRD_AUTH_TOKEN": tinybird_auth_token,
                "TINYBIRD_URL": tinybird_url,
            },
        )
        loader_lambda.add_event_source(
            aws_lambda_event_sources.KinesisEventSource(
                kinesis_stream,
                starting_position=aws_lambda.StartingPosition.LATEST,
                retry_attempts=20,
                batch_size=200,
                max_batching_window=Duration.minutes(2),
            )
        )
