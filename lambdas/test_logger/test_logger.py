import json

# This Lambda prints a JSON payload with some arbitrary message field attached.
# It is intended for flushing structured log lines into the streaming data pipeline for testing purposes.


def handler(event, context):
    message = event.get("message", None)
    print(json.dumps({"event_class": "test", "event_type": "test", "message": message}))
