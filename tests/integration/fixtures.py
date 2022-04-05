import logging

import boto3
import pytest

endpoint_url = "http://localhost:4566"
region = "us-east-2"

LOG = logging.getLogger(__name__)


def _create_external_boto_client(service):
    return boto3.client(
        service_name=service,
        endpoint_url=endpoint_url,
        region_name=region,
        aws_secret_access_key="test",
        aws_access_key_id="test",
    )


@pytest.fixture(scope="class")
def lambda_client():
    return _create_external_boto_client("lambda")


@pytest.fixture(scope="class")
def cloudformation_client():
    return _create_external_boto_client("cloudformation")
