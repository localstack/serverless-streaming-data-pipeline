import json
from time import sleep

from http_server_mock import HttpServerMock

from tests.integration.mocks.tinybird_request_recorder import WSGIRecordData


class TestSupportAnalytics:
    def _get_exported_cloudformation_value(self, cloudformation_client, key_name):
        exports = cloudformation_client.list_exports()["Exports"]
        for export in exports:
            if export["Name"] == key_name:
                return export["Value"]
        raise RuntimeError(f"Unable to locate {key_name} in CloudWatch exports")

    def test_simple_e2e_scenario(self, cloudformation_client, lambda_client):
        app = HttpServerMock(__name__)
        port = 5111
        host = "0.0.0.0"
        tinybird_mock_path = "/tinybird"
        wsgi_records = WSGIRecordData(app.wsgi_app)
        app.wsgi_app = wsgi_records
        num_invocations = 3
        event_messages = [i for i in range(num_invocations)]
        actual_events = []
        actual_event_messages = []
        test_logger_name = self._get_exported_cloudformation_value(
            cloudformation_client, "test-logger-lambda-name"
        )

        @app.route(tinybird_mock_path, methods=["POST"])
        def index():
            return "success"

        with app.run(host, port):
            for i in range(num_invocations):
                lambda_client.invoke(
                    FunctionName=test_logger_name,
                    Payload=json.dumps({"message": event_messages[i]}).encode("utf-8"),
                )

            sleep(5)

            requests = wsgi_records.get_recorded_requests()
            assert (
                len(requests) == num_invocations
            ), "should issue a request to Tinybird for each Lambda invocation"
            for request in requests:
                for line in request.get("data").decode("utf-8").strip().split("\n"):
                    parsed_line = json.loads(line)
                    actual_events.append(parsed_line)
                    actual_event_messages.append(int(parsed_line["message"]))
            assert len(actual_events) == num_invocations, "should receive one event per invocation"
            assert set(event_messages) == set(
                actual_event_messages
            ), "should preserve unique message data per event"
