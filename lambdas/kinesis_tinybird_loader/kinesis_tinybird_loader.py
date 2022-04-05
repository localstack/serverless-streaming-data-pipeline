import base64
import json
import logging
import os
import zlib
from typing import List

import requests

# AWS Lambda function for reading structured analytics events off of a Kinesis stream and sending them to Tinybird

log = logging.getLogger()


def extract_analytics_events(lambda_event) -> List[str]:
    """
    Extracts analytics events from a lambda event invocation payload.
    :param lambda_event: The event payload sent to the Lambda function at its execution. This payload is expected to
                         contain Kinesis records, which in turn contain CloudWatch log messages (base64 encoded and
                         gzipped).
    :return: A list of serialized analytics events, each with a newline at the end.
    """
    analytics_events = []
    for record in lambda_event["Records"]:
        record_data = record["kinesis"]["data"]
        log_payload = json.loads(
            zlib.decompress(base64.b64decode(record_data), 16 + zlib.MAX_WBITS)
        )
        for log_event in log_payload["logEvents"]:
            log_message = log_event["message"]
            analytics_events.append(
                log_message + "\n" if not log_message.endswith("\n") else log_message
            )
    return analytics_events


def load_events_to_tinybird(
    analytics_events: List[str], tinybird_url: str, tinybird_auth_token: str
):
    """
    Loads analytics events into a Tinybird datasource.
    :param analytics_events: A list of serialized, JSON-encoded analytics events. Each event is expected to end with a
                             newline delimiter.
    :param tinybird_url: Complete Tinybird URL to POST events to (via the 'events' API)
    :param tinybird_auth_token: HTTP bearer token for Tinybird
    :raises RuntimeError: If Tinybird returns a non 2XX HTTP response code
    """
    headers = {"Authorization": f"Bearer {tinybird_auth_token}"}
    body = "".join(analytics_events)
    response = requests.post(tinybird_url, data=body, headers=headers)
    if response.status_code > 299:
        log.error(
            f"failed to load events to Tinybird with status code {response.status_code}: {response.text}"
        )
        raise RuntimeError("failed to load events to Tinybird")
    log.info(response.text)


def handler(event, context):
    tinybird_url = os.getenv("TINYBIRD_URL")
    if tinybird_url is None:
        raise EnvironmentError("env var TINYBIRD_URL not set")
    tinybird_auth_token = os.getenv("TINYBIRD_AUTH_TOKEN")
    if tinybird_auth_token is None:
        raise EnvironmentError("env var TINYBIRD_AUTH_TOKEN not set")

    analytics_events = extract_analytics_events(event)
    load_events_to_tinybird(analytics_events, tinybird_url, tinybird_auth_token)
